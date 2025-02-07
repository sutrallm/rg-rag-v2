import os
import re
import argparse
from datetime import datetime
from multiprocessing import Process
import graphrag.my_graphrag.db as db
import graphrag.my_graphrag.model as model


FILE_DIR = os.path.dirname(os.path.realpath(__file__))
OUTPUT_DIR = os.path.join(FILE_DIR, 'output')
EXPORT_PROMPTS_DIR = ''


QUESTION = 'Do Buddhists Also Need Knowledge and Scholarship to Practice Buddhism?'


QUERY_PROMPT1 = '''
You are provided with a question and a piece of text below. Please determine whether the text is relevant to the question. Indicate your answer by putting yes or no within <relevant> </relevant> tags. If the text is relevant, extract the relevant information in bullet points, placing the bullets within <info> </info> tags. Add a blank line between each bullet. Do not mention the source of information or "the text" in your response. Put a heading for the relevant information. The heading should be in <heading></heading> tags and within <info> </info> tags.

<question>
{question}
</question>

<text>
{context}
</text>
'''


QUERY_PROMPT2 = '''
You are provided with a question and some pieces of information below. Please provide a structured answer to the question based on the given information. Do not mention that your answer is based on these information. Provide as much detail in the answer as possible.

<question>
{question}
</question>

{context}
'''


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

    parser.add_argument(
        '--export_prompts',
        type=lambda x: x.lower() == 'true',
        default=False,
        help=f'If True, export the input and output text of all query prompts. If False, skip exporting. Default is False.'
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
            report_text = report['report_content']
            group_id = report['group_id']
            if group_id == export_group_id:
                file_name = f'report_{report_id}.txt'
                file_path = os.path.join(output_report_folder, file_name)
                with open(file_path, 'w') as f:
                    f.write(report_text)
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


def export_prompts(fn, text):
    if EXPORT_PROMPTS_DIR and os.path.isdir(EXPORT_PROMPTS_DIR):
        with open(os.path.join(EXPORT_PROMPTS_DIR, fn), 'w') as f:
            f.write(text)
            f.flush()


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
        query_type = 'GraphRAG + Raptor'
    elif args.query_option == 2:
        query_type = 'Raptor'
    elif args.query_option == 3:
        query_type = 'GraphRAG'
    elif args.query_option == 4:
        query_type = 'Basic RAG'
    else:
        print('Please select at least one of the query options: 1. GraphRAG + Raptor: community report + summary; 2. Raptor: base + summary; 3. GraphRAG: community report; 4. Basic RAG: base.')
        return

    print(f'{query_type} query ...')

    # use deepseek for all types of query
    model.remove_model_tmp_file()
    model.start_sgl_server_deepseek()

    global EXPORT_PROMPTS_DIR
    if args.export_prompts:
        EXPORT_PROMPTS_DIR = os.path.join(FILE_DIR, 'prompts', f'query-{datetime.now().strftime("%Y%m%d%H%M%S")}-{args.query_option}-{query_type.replace(" ", "")}')
        os.makedirs(EXPORT_PROMPTS_DIR, exist_ok=True)

    query_chunk_list = db.get_query_chunks(args.query_option, QUESTION, args.top_k, args.group_id)

    # step 1
    ref_paper_id_list = []
    info_list = []
    for i, chunk in enumerate(query_chunk_list):
        prompt_step1 = QUERY_PROMPT1.format(question=QUESTION, context=chunk['text'])
        answer_step1 = model.get_response_from_sgl(prompt_step1)

        export_prompts('query1_chunk%03d_input.txt' % (i + 1), prompt_step1)
        export_prompts('query1_chunk%03d_output.txt' % (i + 1), answer_step1)

        result_content = re.search(r'<info>(.*?)</info>', answer_step1, re.DOTALL)
        # ignore relevant, just get <info>
        relevant_info = result_content.group(1).strip() if result_content else ''

        is_relevant = relevant_info != ''
        if is_relevant:
            info_list.append(relevant_info)
            ref_paper_id_list += chunk['paper_id_list']

    # step 2
    context_step2 = '\n\n'.join(['<info>\n%s\n</info>' % info for info in info_list])
    prompt_step2 = QUERY_PROMPT2.format(question=QUESTION, context=context_step2)
    answer_step2 = model.get_response_from_sgl(prompt_step2)

    export_prompts('query2_input.txt', prompt_step2)
    export_prompts('query2_output.txt', answer_step2)

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

    export_prompts(f'answer_{query_type.replace(" ", "")}.txt', final_answer)

    end = datetime.now()
    print('run time:', end - start)

    db.rm_db_tmp_file()

    model.stop_sgl_server()


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

