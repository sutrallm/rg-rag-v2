import os
import re
import traceback
import argparse
import ollama
from datetime import datetime
from multiprocessing import Process
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import graphrag.my_graphrag.db as db
from graphrag.my_graphrag.conf import TEXT_TEMPLATE
import graphrag.my_graphrag.raptor as raptor


import nltk
nltk.download('punkt')
from nltk.tokenize import word_tokenize


MODEL_NAME = 'llama3.1:8b-instruct-q8_0'

PROMPT1_MAX_TOKENS = 4000  # 240909 David requires
PROMPT2_MAX_TOKENS = 4000  # 240909 Davie requires
TOP_K_QUERY_CHUNK = 20


FILE_DIR = os.path.dirname(os.path.realpath(__file__))
OUTPUT_DIR = os.path.join(FILE_DIR, 'output')


QUESTION = 'What improvement techniques have people implemented on RAG?'


QUERY_PROMPT1 = '''
You are provided with a question and a piece of text below. Generate a response consisting of a list of key points that respond to the user's question, summarizing all relevant information in the text.

You must use the text below as the primary context for generating the response for the question below.

The response should contain a list of points that you have derived from the text. Each point should be enclosed within <point> </point> tags. Each point should contain three components:

- Title: A brief summary enclosed in <title> </title> tags.
- Description: A comprehensive explanation of the key point enclosed in <content> </content> tags.
- Importance Score: An integer score between 0-100 indicating how important the point is for answering the user's question, enclosed in <score> </score> tags.

The response shall preserve the original meaning and use of modal verbs such as "shall", "may," or "will."

If the text does not contain sufficient information to provide an answer, just say so. Do not make anything up.

Do not include information where the supporting evidence for it is not provided.

== Important Reminder

Your response should answer the question below. The response should be XML format.

== Question

{query}

== Text

{input_text}
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


PROMPT1_RECORD_TEMPLATE = '''<text>
<title>{title}</title>
<content>
{content}
</content>
</text>'''


FINAL_ANSWER_TEMPLATE_NO_TEXT = '''<question>
{question}
</question>

<answer>
{answer}
</answer>

<reference>
{reference}
</reference>
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
    return PROMPT1_RECORD_TEMPLATE.format(content=chunk['report_content'], title=chunk['report_title'])


def convert_chunk_to_prompt1_format_for_raptor_summary(chunk):
    content = chunk['summary_content']
    match = re.search(r'<heading>(.*?)</heading>', content, re.DOTALL)
    title = match.group(1) if match else ''
    return PROMPT1_RECORD_TEMPLATE.format(content=content, title=title)


def convert_prompt1_output(llm_response):
    point_list = []
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

                score_match = re.findall(r"<score>(.*?)</score>", block, re.DOTALL)
                score = score_match[0] if score_match else None
                if not score:
                    continue
                else:
                    score = int(score)
                    if score <= 0:
                        continue

                desp = '<title>%s</title>\n<content>%s</content>' % (title, content)
                point_list.append({
                    'answer': desp,
                    'score': score,
                })

            except Exception as e:
                traceback.print_exc()
                pass
    except Exception as e:
        traceback.print_exc()
        pass

    return point_list


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
    point_list = []
    ref_list_list = []
    for chunk in chunk_list:
        chunk_id = int(chunk[id_key])
        prompt1 = QUERY_PROMPT1.format(query=QUESTION, input_text=convert_chunk_to_prompt1_format(chunk))
        response1 = get_ollama_response(prompt1)
        cur_point_list = convert_prompt1_output(response1)
        point_list += cur_point_list
        ref_list_list += [[chunk_id] for _ in range(len(point_list))]

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
    report_chunk_list = db.query_graphrag_community_report(QUESTION, top_k=TOP_K_QUERY_CHUNK, query_group_id=query_group_id)

    report_point_list, report_ref_list_list = query_step1(report_chunk_list, convert_chunk_to_prompt1_format_for_graphrag, 'report_id')

    if include_summary:
        summary_chunk_list = db.query_graphrag_summary_chunk(QUESTION, top_k=TOP_K_QUERY_CHUNK, query_group_id=query_group_id)
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
        '--query_option', '-o',
        type=int,
        default=1,
        choices=[1, 2, 3, 4],
        help='1. GraphRAG + Raptor: community report + summary; 2. Raptor: base + summary; 3. GraphRAG: community report; 4. Basic RAG: base'
    )

    parser.add_argument(
        '--top_k', '-k',
        type=int,
        default=20,
        help='Top k number of chunks that query is based on.'
    )

    parser.add_argument(
        '--export_reports',
        type=lambda x: x.lower() == 'true',
        default=False,
        help='If True, export the GraphRAG community reports or Raptor summaries. If False, do not export. Default is False.'
    )

    parser.add_argument(
        '--export_type',
        type=int,
        default=1,
        choices=[1, 2],
        help='1. GraphRAG community reports; 2. Raptor summaries'
    )

    parser.add_argument(
        '--export_group_name',
        type=str,
        default='',
        help='You need to specify export_group_name or export_group_id.'
    )

    parser.add_argument(
        '--export_group_id',
        type=int,
        default=-1,
        help='You need to specify export_group_name or export_group_id.'
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


def export_reports(export_type, export_group_name, export_group_id):
    if export_group_name == '' and export_group_id == -1:
        print('Please specify export_group_name or export_group_id.')
        return

    group_list = db.get_all_groups()

    group_name_exist = False
    if export_group_name != '':
        for group in group_list:
            if group['group_name'] == export_group_name:
                export_group_id = group['group_id']
                group_name_exist = True
                break

    group_id_exist = False
    if export_group_id != -1:
        export_group_id = str(export_group_id)
        for group in group_list:
            if group['group_id'] == export_group_id:
                export_group_name = group['group_name']
                group_id_exist = True
                break

    if not group_name_exist and not group_id_exist:
        print('Please specify a correct export_group_name or export_group_id.')
        return

    if not os.path.isdir(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)

    db_name = os.path.basename(os.path.normpath(db.get_db_path()))
    export_type_name = 'GraphRAG_community_reports' if export_type == 1 else 'Raptor_summaries'
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    folder_name = f'{export_group_id}-{export_group_name}-{export_type_name}-{db_name}-{timestamp}'
    output_report_folder = os.path.join(OUTPUT_DIR, folder_name)
    os.mkdir(output_report_folder)

    if export_type == 1:
        report_list = db.get_all_community_reports()
        for report in report_list:
            report_id = report['report_id']
            report_title = report['report_title']
            report_text = report['report_content']
            group_id = report['group_id']
            if group_id == export_group_id:
                file_name = f'report_{report_id}.txt'
                file_path = os.path.join(output_report_folder, file_name)
                with open(file_path, 'w') as f:
                    f.write(f'<title>{report_title}</title>\n')
                    f.write('<text>\n')
                    f.write(report_text)
                    f.write('\n</text>')
                print(f'Exported report {report_id} to {file_path}')

    else:
        summary_list = db.get_all_summary_chunks()
        for summary in summary_list:
            summary_id = summary['summary_id']
            summary_text = summary['summary_content']
            group_id = summary['group_id']
            if group_id == export_group_id:
                file_name = f'summary_{summary_id}.txt'
                file_path = os.path.join(output_report_folder, file_name)
                with open(file_path, 'w') as f:
                    f.write(summary_text)
                print(f'Exported summary {summary_id} to {file_path}')

    print(f'Exported {export_type_name} of group {export_group_id} to {output_report_folder}')


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

    if args.export_reports:
        export_reports(args.export_type, args.export_group_name, args.export_group_id)
        db.rm_db_tmp_file()
        return

    if args.query_option == 1:
        print('GraphRAG + Raptor query ...')
    elif args.query_option == 2:
        print('Raptor query ...')
    elif args.query_option == 3:
        print('GraphRAG query ...')
    elif args.query_option == 4:
        print('Base only query ...')
    else:
        print('Please select at least one of the query options: 1. GraphRAG + Raptor: community report + summary; 2. Raptor: base + summary; 3. GraphRAG: community report; 4. Basic RAG: base.')
        return

    query_chunk_list = db.get_query_chunks(args.query_option, QUESTION, args.top_k, args.group_id)

    # step 1
    ref_paper_id_list = []
    info_list = []
    for chunk in query_chunk_list:
        prompt_step1 = raptor.PROMPT_QUERY_STEP1.format(question=QUESTION, context=chunk['text'])
        answer_step1 = get_ollama_response(prompt_step1)

        result_content = re.search(r'<info>(.*?)</info>', answer_step1, re.DOTALL)
        # ignore relevant, just get <info>
        relevant_info = result_content.group(1).strip() if result_content else ''

        is_relevant = relevant_info != ''
        if is_relevant:
            info_list.append(relevant_info)
            ref_paper_id_list += chunk['paper_id_list']

    # step 2
    context_step2 = '\n\n'.join(['<info>\n%s\n</info>' % info for info in info_list])
    prompt_step2 = raptor.PROMPT_QUERY_STEP2.format(question=QUESTION, context=context_step2)
    answer_step2 = get_ollama_response(prompt_step2)

    paper_list = db.get_all_papers()
    group_dict = {}
    for paper_id in list(set(ref_paper_id_list)):
        for paper in paper_list:
            if paper_id == paper['paper_id']:
                group_id = paper['group_id']
                paper_name = os.path.splitext(paper['paper_name'])[0]
                group_name = db.get_group_name(group_id)

                if group_name not in group_dict:
                    group_dict[group_name] = []
                group_dict[group_name].append(paper_name)

                break

    ref_text = []
    group_name_list = list(group_dict.keys())
    group_name_list.sort()
    for group_name in group_name_list:
        paper_name_list = group_dict[group_name]
        paper_name_list.sort()
        ref_text.append(f'{group_name}: {", ".join(paper_name_list)}')

    final_answer = FINAL_ANSWER_TEMPLATE_NO_TEXT.format(
        question=QUESTION,
        answer=answer_step2,
        reference='\n'.join(ref_text)
    )

    print('--- final answer ---')
    print(final_answer)
    print('--- final answer ---')

    end = datetime.now()
    print('run time:', end - start)

    db.rm_db_tmp_file()


def main_with_timeout():
    timeout = 4 * 60  # 4 minutes timeout
    process = Process(target=main, args=())
    process.start()
    process.join(timeout)
    if process.is_alive():
        process.terminate()
        print('Query time out! Please change the query question or options.')


if __name__ == '__main__':
    main_with_timeout()

