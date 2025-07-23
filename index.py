import os
import shutil
import subprocess
import argparse
import pathlib
import csv
from datetime import datetime
import graphrag.my_graphrag.db as db
import graphrag.my_graphrag.cloud as model
from graphrag.my_graphrag.raptor import raptor_index


FILE_DIR = os.path.dirname(os.path.realpath(__file__))
PRJ_DIR = os.path.join(FILE_DIR, './my_graphrag')
CONFIG_EXAMPLE_DIR = os.path.join(PRJ_DIR, 'config_example')
INPUT_DIR = os.path.join(PRJ_DIR, 'input_groups')
TMP_CONFIG_DIR = os.path.join(PRJ_DIR, 'output/tmp_config')
PROMPTS_DIR = os.path.join(FILE_DIR, 'prompts')
TMP_PROMPTS_DIR = os.path.join(PROMPTS_DIR, 'tmp')
DENOISING_PROMPT_DIR = os.path.join(PROMPTS_DIR, 'denoising')
OUTPUT_DIR = os.path.join(FILE_DIR, 'output')


DENOISING_PROMPT = '''
Reorganise the following text into bullet points. Focus on the principles described, removing any dialogue style or references to individuals. Do not omit any details. There is no need to include headings. Do not add anything beyond what is mentioned in the text. Use "#" as the bullet marker.

e.g.

# point 1
# point 2
# point 3

== Text

{input_text}
'''


def get_denoising_chunk(original_chunk, group_chunk_idx, denoising_group_dir=''):
    prompt = DENOISING_PROMPT.format(input_text=original_chunk)

    output = model.get_response_from_sgl(prompt)

    if denoising_group_dir and os.path.isdir(denoising_group_dir):
        # export input and output
        prefix = f'denoising_prompt_{group_chunk_idx}'

        with open(os.path.join(denoising_group_dir, f'{prefix}_input.txt'), 'w') as f:
            f.write(prompt)
            f.flush()

        with open(os.path.join(denoising_group_dir, f'{prefix}_output.txt'), 'w') as f:
            f.write(output)
            f.flush()

    return output


def save_group_and_paper(export_prompts):
    # use llama for denoise
    model.start_sgl_server_llama()

    cur_group_list = db.get_all_groups()
    cur_paper_list = db.get_all_papers()

    new_paper_list_list_graphrag = []
    new_paper_list_list_raptor = []
    group_folder_list = os.listdir(INPUT_DIR)
    group_folder_list.sort()
    for group_name in group_folder_list:
        new_graphrag = False
        new_raptor = False

        existing_group_id = None
        for cur_group in cur_group_list:
            if group_name == cur_group['group_name']:
                existing_group_id = cur_group['group_id']
                break

        if existing_group_id is not None:
            paper_id_list, chunk_id_list, relationship_id_list, report_id_list, summary_id_list = db.get_ref_ids_for_group(existing_group_id)
            if len(summary_id_list) == 0:
                new_raptor = True
            if len(report_id_list) == 0 or len(relationship_id_list) == 0:
                new_graphrag = True
        else:
            new_graphrag = True
            new_raptor = True

        if not new_graphrag and not new_raptor:
            continue

        # each group can have one or multiple files
        group_dir = os.path.join(INPUT_DIR, group_name)
        txt_file_list = []
        for fn in os.listdir(group_dir):
            if fn.endswith('txt'):
                txt_file_list.append(os.path.join(group_dir, fn))
            else:
                # ignore
                pass
        txt_file_list.sort()

        group_id = db.save_new_group(group_name) if existing_group_id is None else existing_group_id

        denoising_group_dir = ''
        if export_prompts:
            denoising_group_dir = os.path.join(DENOISING_PROMPT_DIR, group_name)
            if os.path.isdir(denoising_group_dir):
                shutil.rmtree(denoising_group_dir)
            os.mkdir(denoising_group_dir)

        new_paper_list = []
        for txt_file_path in txt_file_list:
            with open(txt_file_path, 'r') as txtf:
                paper_content = txtf.read()
            paper_name = os.path.basename(txt_file_path)

            paper_id = None
            if existing_group_id is not None:
                for cur_paper in cur_paper_list:
                    if cur_paper['paper_name'] == paper_name and cur_paper['group_id'] == existing_group_id:
                        paper_id = cur_paper['paper_id']
                        break

            if paper_id is None:
                paper_id = db.save_new_paper(paper_content, paper_name, group_id)
                chunk = paper_content
                denoising_chunk = get_denoising_chunk(chunk, f'{paper_id}', denoising_group_dir)
                db.save_new_chunk(chunk, paper_id, group_id, denoising_chunk=denoising_chunk)

            new_paper_list.append(
                {
                    'txt_path': txt_file_path,
                    'paper_id': paper_id,
                    'group_id': group_id
                }
            )

        if new_paper_list:
            if new_graphrag:
                new_paper_list_list_graphrag.append(new_paper_list)
            if new_raptor:
                new_paper_list_list_raptor.append(new_paper_list)

    model.stop_sgl_server()

    return new_paper_list_list_graphrag, new_paper_list_list_raptor


def check_config_example_dir():
    if not os.path.isdir(CONFIG_EXAMPLE_DIR):
        print('Please put the config example on ' + CONFIG_EXAMPLE_DIR)
        return False

    settings_file = os.path.join(CONFIG_EXAMPLE_DIR, 'settings.yaml')
    cache_dir = os.path.join(CONFIG_EXAMPLE_DIR, 'cache')
    input_dir = os.path.join(CONFIG_EXAMPLE_DIR, 'input')
    output_dir = os.path.join(CONFIG_EXAMPLE_DIR, 'output')
    prompts_dir = os.path.join(CONFIG_EXAMPLE_DIR, 'prompts')

    if not os.path.isfile(settings_file):
        print('Please put settings.yaml in ' + CONFIG_EXAMPLE_DIR)
        return False

    if not os.path.isdir(prompts_dir):
        os.mkdir(prompts_dir)

    if os.path.isdir(cache_dir):
        shutil.rmtree(cache_dir)
    os.mkdir(cache_dir)

    if os.path.isdir(input_dir):
        shutil.rmtree(input_dir)
    os.mkdir(input_dir)

    if os.path.isdir(output_dir):
        shutil.rmtree(output_dir)
    os.mkdir(output_dir)

    return True


def process_arguments():
    parser = argparse.ArgumentParser()

    default_db_path = db.DATABASE_PATH
    parser.add_argument(
        '--db_path', '-p',
        type=str,
        default=default_db_path,
        help=f'Database path. Default is "{default_db_path}"'
    )

    parser.add_argument(
        '--raptor', '-r',
        type=lambda x: x.lower() == 'true',
        default=True,
        help='If True, run raptor index. If False, skip raptor index. Default is True.'
    )

    parser.add_argument(
        '--graphrag', '-g',
        type=lambda x: x.lower() == 'true',
        default=True,
        help='If True, run graphrag index. If False, skip graphrag index. Default is True.'
    )

    parser.add_argument(
        '--del_group', '-d',
        type=int,
        default=-1,
        help='ID of the group to delete. If not provided, skip.'
    )

    parser.add_argument(
        '--del_option', '-o',
        type=str,
        default='all',
        choices=['all', 'graphrag', 'raptor'],
        help='Choose which part you want to delete in the group.'
    )

    parser.add_argument(
        '--export_prompts',
        type=lambda x: x.lower() == 'true',
        default=False,
        help=f'If True, export the input and output text of all 3 index prompts. If False, skip exporting. Default is False.'
    )

    args = parser.parse_args()

    if not args.raptor and not args.graphrag:
        print('Please select at least one of the index options: "--raptor True" or "--graphrag True".')
        return None

    input_db_path = args.db_path
    if not os.path.isabs(input_db_path):
        input_db_path = os.path.join(os.getcwd(), input_db_path)

    parent_dir = pathlib.Path(input_db_path).parent
    if not parent_dir.exists():
        print(f'Please check your input database path. The parent directory "{parent_dir}" does not exist.')
        return None

    db.update_db_path(input_db_path)

    if args.del_group != -1:
        if args.del_option == 'graphrag':
            del_graphrag = True
            del_raptor = False
        elif args.del_option == 'raptor':
            del_graphrag = False
            del_raptor = True
        else:
            del_graphrag = True
            del_raptor = True

        db.delete_group(str(args.del_group), del_graphrag, del_raptor)
        return None

    return args


def main():
    start_time = datetime.now()

    db.rm_db_tmp_file()

    args = process_arguments()
    if args is None:
        db.rm_db_tmp_file()
        return

    if not check_config_example_dir():
        return

    model.remove_model_tmp_file()
    model.check_model_dir()

    if os.path.isdir(TMP_CONFIG_DIR):
        shutil.rmtree(TMP_CONFIG_DIR)

    if not os.path.isdir(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)

    if not os.path.isdir(PROMPTS_DIR):
        os.mkdir(PROMPTS_DIR)
    if os.path.isdir(TMP_PROMPTS_DIR):
        shutil.rmtree(TMP_PROMPTS_DIR)

    db_output_dir = os.path.join(OUTPUT_DIR, os.path.basename(os.path.normpath(db.get_db_path())))
    db_output_prompts_dir = os.path.join(db_output_dir, 'prompts')
    os.makedirs(db_output_prompts_dir, exist_ok=True)
    db_output_graphrag_output_dir = os.path.join(db_output_dir, 'graphrag_output')
    os.makedirs(db_output_graphrag_output_dir, exist_ok=True)

    log_path = os.path.join(db_output_dir, 'index_log_%s.csv' % (start_time.strftime('%Y-%m-%d-%H-%M-%S')))

    if args.export_prompts:
        if os.path.isdir(DENOISING_PROMPT_DIR):
            shutil.rmtree(DENOISING_PROMPT_DIR)
        os.mkdir(DENOISING_PROMPT_DIR)

    new_paper_list_list_graphrag, new_paper_list_list_raptor = save_group_and_paper(args.export_prompts)

    start_time_graphrag = datetime.now()
    if args.graphrag:
        # use deepseek for graphrag indexing
        model.start_sgl_server_deepseek()

        for new_paper_list in new_paper_list_list_graphrag:
            start_time_one_group = datetime.now()

            if os.path.isdir(TMP_PROMPTS_DIR):
                shutil.rmtree(TMP_PROMPTS_DIR)
            if args.export_prompts:
                os.mkdir(TMP_PROMPTS_DIR)

            if os.path.isdir(TMP_CONFIG_DIR):
                shutil.rmtree(TMP_CONFIG_DIR)
            shutil.copytree(CONFIG_EXAMPLE_DIR, TMP_CONFIG_DIR)

            group_name = ''
            group_id = ''
            paper_name_list = []
            paper_id_list = []

            for new_paper in new_paper_list:
                txt_file = new_paper['txt_path']
                shutil.copyfile(txt_file, os.path.join(TMP_CONFIG_DIR, 'input', os.path.basename(txt_file)))
                paper_id_list.append(new_paper['paper_id'])
                paper_name_list.append(os.path.basename(txt_file))
                if not group_name:
                    group_name = os.path.basename(os.path.dirname(txt_file))
                    group_id = new_paper['group_id']

            with open(log_path, 'a') as f:
                writer = csv.writer(f)
                writer.writerow(['Start time', start_time_one_group.strftime('%Y-%m-%d-%H-%M-%S')])
                writer.writerow(['Group ID', group_id])
                writer.writerow(['Group name', group_name])
                writer.writerow(['Document IDs', str(paper_id_list)])
                writer.writerow(['Document names', str(paper_name_list)])
                writer.writerow(['Index type', 'GraphRAG'])
                f.flush()

            db.update_group_id_tmp_file(group_id)

            # python -m graphrag.index --root ./ragtest
            p = subprocess.Popen(['python', '-m', 'graphrag.index', '--root', TMP_CONFIG_DIR])
            p.wait()

            end_time_one_group = datetime.now()

            if os.path.isdir(TMP_CONFIG_DIR):
                shutil.move(TMP_CONFIG_DIR, os.path.join(db_output_graphrag_output_dir, group_name + end_time_one_group.strftime('-%Y-%m-%d-%H-%M-%S')))

            if args.export_prompts:
                denoising_group_dir = os.path.join(DENOISING_PROMPT_DIR, group_name)
                if os.path.isdir(denoising_group_dir) and os.path.isdir(TMP_PROMPTS_DIR):
                    for fn in os.listdir(denoising_group_dir):
                        shutil.move(os.path.join(denoising_group_dir, fn), os.path.join(TMP_PROMPTS_DIR, fn))
                    shutil.rmtree(denoising_group_dir)
                if os.path.isdir(DENOISING_PROMPT_DIR) and len(os.listdir(DENOISING_PROMPT_DIR)) == 0:
                    shutil.rmtree(DENOISING_PROMPT_DIR)

                if os.path.isdir(TMP_PROMPTS_DIR):
                    shutil.move(TMP_PROMPTS_DIR, os.path.join(db_output_prompts_dir, 'index-' + group_name + end_time_one_group.strftime('-%Y-%m-%d-%H-%M-%S')))
                else:
                    print(f'No prompts folder found for {group_name}')

            with open(log_path, 'a') as f:
                writer = csv.writer(f)
                writer.writerow(['Run time', end_time_one_group - start_time_one_group])
                writer.writerow(['End time', end_time_one_group.strftime('%Y-%m-%d-%H-%M-%S')])
                f.flush()

            db.rm_group_id_tmp_file()

        model.stop_sgl_server()

    if os.path.isdir(PROMPTS_DIR) and len(os.listdir(PROMPTS_DIR)) == 0:
        shutil.rmtree(PROMPTS_DIR)

    end_time_graphrag = datetime.now()

    if args.raptor:
        # use llama for raptor summary
        model.start_sgl_server_llama()

        raptor_index([p['paper_id'] for l in new_paper_list_list_raptor for p in l], log_path)

        model.stop_sgl_server()

    end_time_raptor = datetime.now()

    print('graphrag run time:', end_time_graphrag - start_time_graphrag)
    print('raptor run time:', end_time_raptor - end_time_graphrag)
    print('run time:', end_time_raptor - start_time)

    db.count_all_collection()

    db.rm_db_tmp_file()


if __name__ == '__main__':
    main()

