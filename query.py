import os
import re
import traceback
import argparse
import ollama
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import graphrag.my_graphrag.db as db
from graphrag.my_graphrag.conf import TEXT_TEMPLATE
from graphrag.my_graphrag.raptor import raptor_query


import nltk
nltk.download('punkt')
from nltk.tokenize import word_tokenize


MODEL_NAME = 'llama3.1:8b-instruct-q8_0'

PROMPT1_MAX_TOKENS = 4000  # 240909 David requires
PROMPT2_MAX_TOKENS = 4000  # 240909 Davie requires
TOP_K_COMMUNITY_REPORT = 20


QUESTION = 'What improvement techniques have people implemented on RAG?'


QUERY_PROMPT1 = '''
You are provided with question and a data table below. Generate a response consisting of a list of key points that respond to the user's question, summarizing all relevant information in the data table.

The data table is a sequence of records in the following XML format:

<record>
<id> ... </id>
<title> ... </title>
<content> ... </content>
</record>

where <id> contains the record ID. The following is an example.

<record>
<id>50</id>
<title>DPR Retrieval Model Community</title>
<content>
The DPR retrieval model community is centered around the Dual-Purpose Representations (DPR) model, which has been adapted and extended by various researchers for domain-specific tasks. The community's entities include the DPR model itself, its variants like RAG-END2END, and related datasets such as TriviaQA.
</content>
</record>

You should use the data provided in the data table below as the primary context for generating the response for the question below.

The response should contain list of points that you have derived from the data records. Each point should be put in <point> </point> tags. Each point should contain four components:

- a title in <title> </title> tags.
- a comprehensive description in <content> </content> tags.
- a list record id(s) on which the point is based on in <ref> </ref> tags. This list should be id(s) only. Avoid explicitly mentioning "record" or record title.
- an importance score which is an integer score between 0-100 that indicates how important the point is in answering the user's question in <score> </score> tags.

The response shall preserve the original meaning and use of modal verbs such as "shall", "may," or "will."

If the data table does not contain sufficient information to provide an answer, just say so. Do not make anything up.

Do not include information where the supporting evidence for it is not provided.

== Important Reminder

Your response should answer the question below. Provide reference by stating the record id(s) for each point in your response. The response should be XML format.

== Question

{query}

== Data Table

{input_text}

== Important Reminder

Your response should answer the question above. Provide reference by stating the record id(s) for each point in your response. The response should be XML format.
'''


QUERY_PROMPT2 = '''
You are a helpful assistant responding to questions about a dataset by synthesizing perspectives from multiple analysts.

Generate a response that directly answers the user's question by summarizing and integrating the key points from all the analysts' reports, which focus on different aspects of the dataset.

Note that the analysts' reports provided below are ranked in the **descending order of importance**.

If the provided reports do not contain sufficient information to answer the question, or if you are unsure of the answer, state this clearly without speculating or making assumptions.

The final response should remove all irrelevant information from the analysts' reports and combine the relevant information into a cohesive and comprehensive answer that explains the key points and their implications appropriately.

Structure your response using sections and commentary where appropriate, and style the response using markdown.

The response shall preserve the original meaning and use of modal verbs such as "shall", "may" or "will".

Do not include information where the supporting evidence for it is not provided.

== Question

{query}

== Analyst Reports

{report_data}
'''


PROMPT1_RECORD_TEMPLATE = '''<record>
<id>{id}</id>
<title>{title}</title>
<content>
{content}
</content>
</record>'''


FINAL_ANSWER_TEMPLATE_NO_TEXT = '''<question>
{question}
</question>

<answer>
{answer}
</answer>

<reference_id>
{reference_id}
</reference_id>
'''


FINAL_ANSWER_TEMPLATE_WITH_TEXT = '''<question>
{question}
</question>

<answer>
{answer}
</answer>

<reference_id>
{reference_id}
</reference_id>

<reference_text>
{reference_text}
</reference_text>
'''


def convert_chunk_to_prompt1_format_for_graphrag(chunk):
    return PROMPT1_RECORD_TEMPLATE.format(id=chunk['report_id'], content=chunk['report_content'], title=chunk['report_title'])


def convert_chunk_to_prompt1_format_for_raptor_summary(chunk):
    content = chunk['summary_content']
    match = re.search(r'<heading>(.*?)</heading>', content, re.DOTALL)
    title = match.group(1) if match else ''
    return PROMPT1_RECORD_TEMPLATE.format(id=chunk['summary_id'], content=content, title=title)


def convert_prompt1_output(llm_response, id_list):
    point_list = []
    ref_list_list = []
    try:
        point_blocks = re.findall(r"<point>(.*?)</point>", llm_response, re.DOTALL)
        for block in point_blocks:
            try:
                title_match = re.findall(r"<title>(.*?)</title>", block, re.DOTALL)
                title = title_match[0] if title_match else None
                if not title:
                    continue

                content_match = re.findall(r"<content>(.*?)</content>", block, re.DOTALL)
                content = content_match[0] if content_match else None
                if not content:
                    continue

                ref_match = re.findall(r"<ref>(.*?)</ref>", block, re.DOTALL)
                ref = ref_match[0] if ref_match else None

                if not ref:
                    continue
                else:
                    ref_list = [int(i) for i in re.findall(r'\b\d+\b', ref)]
                    correct_ref = True
                    for i in ref_list:
                        if i not in id_list:
                            correct_ref = False
                            break
                    if not correct_ref:
                        continue
                    else:
                        ref = ','.join(map(str, ref_list))

                score_match = re.findall(r"<score>(.*?)</score>", block, re.DOTALL)
                score = score_match[0] if score_match else None
                if not score:
                    continue
                else:
                    score = int(score)
                    if score <= 0:
                        continue

                desp = '<title>%s</title>\n<content>%s</content>\n<ref>%s</ref>' % (title, content, ref)
                point_list.append({
                    'answer': desp,
                    'score': score,
                })

                ref_list_list.append(ref_list)

            except Exception as e:
                traceback.print_exc()
                pass
    except Exception as e:
        traceback.print_exc()
        pass

    return point_list, ref_list_list


def count_tokens(text):
    return len(word_tokenize(text))


def split_chunks_into_batches(chunks, max_tokens, convert_chunk_to_prompt1_format):
    batches = []
    current_batch = []
    current_tokens = 0

    for chunk in chunks:
        chunk_tokens = count_tokens(convert_chunk_to_prompt1_format(chunk))

        # If the chunk itself is larger than max_tokens, treat it as a single batch
        if chunk_tokens > max_tokens:
            if current_batch:
                batches.append(current_batch)
                current_batch = []
                current_tokens = 0
            batches.append([chunk])
        else:
            # If adding the chunk exceeds max_tokens, start a new batch
            if current_tokens + chunk_tokens > max_tokens:
                batches.append(current_batch)
                current_batch = []
                current_tokens = 0

            current_batch.append(chunk)
            current_tokens += chunk_tokens

    # Add the last batch if it's not empty
    if current_batch:
        batches.append(current_batch)

    return batches


def get_cosine_sim(str1, str2):
    tfidf = TfidfVectorizer().fit_transform([str1, str2])
    cosine_sim = cosine_similarity(tfidf[0:1], tfidf[1:2])
    return cosine_sim[0][0]


def query_step1(chunk_list, convert_chunk_to_prompt1_format, id_key):
    batch_list = split_chunks_into_batches(chunk_list, PROMPT1_MAX_TOKENS, convert_chunk_to_prompt1_format)

    point_list = []
    ref_list_list = []
    for batch in batch_list:
        record_list = []
        id_list = []
        for chunk in batch:
            record_list.append(convert_chunk_to_prompt1_format(chunk))
            id_list.append(int(chunk[id_key]))

        prompt1 = QUERY_PROMPT1.format(query=QUESTION, input_text='\n\n'.join(record_list))
        response1 = get_ollama_response(prompt1)
        cur_point_list, cur_ref_list_list = convert_prompt1_output(response1, id_list)
        point_list += cur_point_list
        ref_list_list += cur_ref_list_list

    sorted_point_indices = sorted(range(len(point_list)), key=lambda i: point_list[i]['score'], reverse=True)
    unique_point_list = []
    unique_ref_list_list = []
    for i in sorted_point_indices:
        cur_point = point_list[i]

        repeat = False
        try:
            score1 = cur_point['score']
            answer1 = cur_point['answer']
            for d2 in unique_point_list:
                score2 = d2['score']
                answer2 = d2['answer']
                if score1 == score2 and get_cosine_sim(answer1, answer2) > 0.9:
                    repeat = True
                    break
        except:
            pass
        if not repeat:
            unique_point_list.append(cur_point)
            unique_ref_list_list.append(ref_list_list[i])

    return unique_point_list, unique_ref_list_list


def select_indices_based_on_score(point_list1, point_list2, max_tokens):
    combined = [{'source': 1, 'data': item} for item in point_list1] + [{'source': 2, 'data': item} for item in point_list2]
    combined.sort(key=lambda x: x['data']['score'], reverse=True)

    data = []
    total_tokens = 0
    selected_indices_1 = []
    selected_indices_2 = []
    for item in combined:
        cur_point = item['data']
        cur_data = f'<analyst>\n{cur_point["answer"]}\n<score>{cur_point["score"]}<\score>\n</analyst>'
        cur_tokens = count_tokens(cur_data)

        if total_tokens + cur_tokens <= max_tokens:
            total_tokens += cur_tokens
            data.append(cur_data)
            if item['source'] == 1:
                selected_indices_1.append(point_list1.index(item['data']))
            else:
                selected_indices_2.append(point_list2.index(item['data']))
        else:
            break

    return selected_indices_1, selected_indices_2, data


def get_ollama_response(prompt):
    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt
            },
        ],
        options={
            'temperature': 0.1,
            'num_ctx': 32000,

        }
    )
    output = response['message']['content']
    return output


def query_step2(data):
    prompt2 = QUERY_PROMPT2.format(query=QUESTION, report_data='\n\n'.join(data))

    # print('--- prompt2 ---')
    # print(prompt2)
    # print('--- prompt2 ---')

    response2 = get_ollama_response(prompt2)
    return response2


def get_ref_id_and_text_for_report(selected_indices, ref_list_list, chunk_list):
    final_ref_list = []
    for i in selected_indices:
        final_ref_list += ref_list_list[i]

    # convert report id to group id and chunk id
    group_chunk_dict = {}
    for report in chunk_list:
        report_id = int(report['report_id'])
        if report_id in final_ref_list:
            chunk_id_list = report['chunk_id_list']
            for chunk_id in chunk_id_list:
                paper_id, group_id = db.get_ref_id_of_chunk(str(chunk_id))
                if group_id is not None:
                    if group_id not in group_chunk_dict:
                        group_chunk_dict[group_id] = []
                    group_chunk_dict[group_id].append(chunk_id)

    ref_template = 'group id {group_id}: chunk ids {chunk_ids}'
    group_id_list = list(group_chunk_dict.keys())
    group_id_list.sort(key=lambda x: int(x), reverse=False)
    ref_string_list = []

    chunk_text_list = []
    for group_id in group_id_list:
        chunk_id_list = group_chunk_dict[group_id]
        chunk_id_list = list(set(chunk_id_list))
        chunk_id_list.sort(key=lambda x: int(x), reverse=False)
        ref_string_list.append(ref_template.format(group_id=group_id, chunk_ids=', '.join(chunk_id_list)))

        for chunk_id in chunk_id_list:
            chunk_text = db.get_chunk(chunk_id)
            chunk_text_list.append(TEXT_TEMPLATE.format(title='chunk', id=chunk_id, text=chunk_text))

    # ref_id, ref_text
    return '\n'.join(ref_string_list), '\n\n'.join(chunk_text_list)


def get_ref_id_and_text_for_summary(selected_indices, ref_list_list, chunk_list):
    final_ref_list = []
    for i in selected_indices:
        final_ref_list += ref_list_list[i]

    # convert summary id to group id and chunk id
    group_chunk_dict = {}
    for summary in chunk_list:
        summary_id = int(summary['summary_id'])
        if summary_id in final_ref_list:
            group_id = summary['group_id']
            if group_id not in group_chunk_dict:
                group_chunk_dict[group_id] = []
            group_chunk_dict[group_id].append(summary_id)

    ref_template = 'group id {group_id}: summary ids {chunk_ids}'
    group_id_list = list(group_chunk_dict.keys())
    group_id_list.sort(key=lambda x: int(x), reverse=False)

    ref_string_list = []
    chunk_text_list = []
    for group_id in group_id_list:
        chunk_id_list = group_chunk_dict[group_id]
        chunk_id_list = list(set(chunk_id_list))
        chunk_id_list.sort(key=lambda x: int(x), reverse=False)
        ref_string_list.append(ref_template.format(group_id=group_id, chunk_ids=', '.join(map(str, chunk_id_list))))

        for summary_id in chunk_id_list:
            chunk_text = db.get_summary(summary_id)
            chunk_text_list.append(TEXT_TEMPLATE.format(title='summary', id=summary_id, text=chunk_text))

    # ref_id, ref_text
    return '\n'.join(ref_string_list), '\n\n'.join(chunk_text_list)


def graphrag_query(include_summary=False, query_group_id=-1):
    report_chunk_list = db.query_graphrag_community_report(QUESTION, top_k=TOP_K_COMMUNITY_REPORT, query_group_id=query_group_id)

    report_point_list, report_ref_list_list = query_step1(report_chunk_list, convert_chunk_to_prompt1_format_for_graphrag, 'report_id')

    if include_summary:
        summary_chunk_list = db.get_all_summary_chunks()
        summary_chunk_list = [chunk for chunk in summary_chunk_list if query_group_id == -1 or chunk['group_id'] == str(query_group_id)]
        summary_point_list, summary_ref_list_list = query_step1(summary_chunk_list, convert_chunk_to_prompt1_format_for_raptor_summary, 'summary_id')
    else:
        summary_chunk_list = []
        summary_point_list = []
        summary_ref_list_list = []

    report_selected_indices, summary_selected_indices, data = select_indices_based_on_score(report_point_list, summary_point_list, PROMPT2_MAX_TOKENS)
    answer = query_step2(data)

    ref_id_report, ref_text_report = get_ref_id_and_text_for_report(report_selected_indices, report_ref_list_list, report_chunk_list)
    if include_summary:
        ref_id_summary, ref_text_summary = get_ref_id_and_text_for_summary(summary_selected_indices, summary_ref_list_list, summary_chunk_list)
    else:
        ref_id_summary = ''
        ref_text_summary = ''

    ref_id = ref_id_report + '\n' + ref_id_summary if ref_id_summary else ref_id_report
    ref_text = ref_text_report + '\n\n' + ref_text_summary if ref_text_summary else ref_text_report

    # answer, ref_id, ref_text
    return answer, ref_id, ref_text


def process_arguments():
    global QUESTION

    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--question', '-q',
        type=str,
        default=QUESTION,
        help=f'Query question. Default is "{QUESTION}"'
    )

    default_db_path = db.DATABASE_PATH
    parser.add_argument(
        '--db_path', '-p',
        type=str,
        default=default_db_path,
        help=f'Database path. Default is "{default_db_path}"'
    )

    parser.add_argument(
        '--list_group', '-l',
        type=lambda x: x.lower() == 'true',
        default=False,
        help='If True, list group details. If False, execute the query. Default is False.'
    )

    parser.add_argument(
        '--group_id', '-i',
        type=int,
        default=-1,
        help='ID of the group to query. If not provided, all groups will be queried. Default is -1 (query all).'
    )

    parser.add_argument(
        '--raptor', '-r',
        type=lambda x: x.lower() == 'true',
        default=True,
        help='If True, run raptor query. Default is True.'
    )

    parser.add_argument(
        '--graphrag', '-g',
        type=lambda x: x.lower() == 'true',
        default=True,
        help='If True, run graphrag query. Default is True.'
    )

    parser.add_argument(
        '--include_text', '-t',
        type=lambda x: x.lower() == 'true',
        default=False,
        help='If True, final answer will include the reference chunk/summary chunk/community report text. If False, with reference id only. Default is False.'
    )

    args = parser.parse_args()

    QUESTION = args.question

    input_db_path = args.db_path
    if not os.path.isabs(input_db_path):
        input_db_path = os.path.join(os.getcwd(), input_db_path)
    if not os.path.isdir(input_db_path):
        print(f'Database path "{input_db_path}" does not exist.')
        return None

    db.update_db_path(input_db_path)

    if args.group_id != -1:
        has_group = False
        group_list = db.get_all_groups()
        for group in group_list:
            if args.group_id == int(group['group_id']):
                has_group = True
                break
        if not has_group:
            print('Please input an valid Group ID. You can list group IDs by "--list_group True"')
            return None

    if not args.raptor and not args.graphrag:
        print('Please select at least one of the query options: "--raptor True" or "--graphrag True".')
        return None

    return args


def list_group():
    group_list = db.get_all_groups()
    paper_list = db.get_all_papers()

    output_format = "{:^15}|{:^15}|{:^15}| {:<20}"
    print(output_format.format('Group ID', 'Group Name', 'Document ID', 'Document Name'))

    for group in group_list:
        group_id = group['group_id']
        first_line = True
        for paper in paper_list:
            if paper['group_id'] == group_id:
                print(output_format.format(
                    group_id if first_line else '',
                    group['group_name'] if first_line else '',
                    paper['paper_id'],
                    paper['paper_name']
                ))
                first_line = False


def main():
    start = datetime.now()

    db.rm_db_tmp_file()

    args = process_arguments()
    if args is None:
        db.rm_db_tmp_file()
        return

    if args.list_group:
        list_group()
        db.rm_db_tmp_file()
        return

    if args.raptor and args.graphrag:
        print('GraphRAG + Raptor query ...')
        answer, ref_id, ref_text = graphrag_query(include_summary=True, query_group_id=args.group_id)
    elif args.raptor:
        print('Raptor query ...')
        answer, ref_id, ref_text = raptor_query(QUESTION, query_group_id=args.group_id)
    elif args.graphrag:
        print('GraphRAG query ...')
        answer, ref_id, ref_text = graphrag_query(include_summary=False, query_group_id=args.group_id)
    else:
        print('Please select at least one of the query options: "--raptor True" or "--graphrag True".')
        return

    if args.include_text:
        final_answer = FINAL_ANSWER_TEMPLATE_WITH_TEXT.format(
            question=QUESTION,
            answer=answer,
            reference_id=ref_id,
            reference_text=ref_text
        )
    else:
        final_answer = FINAL_ANSWER_TEMPLATE_NO_TEXT.format(
            question=QUESTION,
            answer=answer,
            reference_id=ref_id
        )

    print('--- final answer ---')
    print(final_answer)
    print('--- final answer ---')

    end = datetime.now()
    print('run time:', end - start)

    db.rm_db_tmp_file()


if __name__ == '__main__':
    main()

