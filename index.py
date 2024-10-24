import os
import shutil
import subprocess
import argparse
import hashlib
import pathlib
import pdftotext
from datetime import datetime
import graphrag.my_graphrag.db as db
from graphrag.my_graphrag.conf import INDEX_RAPTOR, INDEX_GRAPHRAG
from graphrag.my_graphrag.raptor import raptor_index

FILE_DIR = os.path.dirname(os.path.realpath(__file__))
PRJ_DIR = os.path.join(FILE_DIR, './my_graphrag')
CONFIG_EXAMPLE_DIR = os.path.join(PRJ_DIR, 'config_example')
INPUT_DIR = os.path.join(PRJ_DIR, 'input_groups')
TMP_CONFIG_DIR = os.path.join(PRJ_DIR, 'output/tmp_config')


def extract_text_from_pdf(pdf_path, save_txt_file=False):
    # Load your PDF
    with open(pdf_path, 'rb') as f:
        pdf = pdftotext.PDF(f)
    # Read all the text into one string
    pdftotext_text = '\n\n'.join(pdf)

    if save_txt_file:
        with open(pdf_path[:-4] + '.txt', 'w') as f:
            f.write(pdftotext_text)
            f.flush()

    return pdftotext_text


def save_group_and_paper():
    cur_paper_list = db.get_all_papers()

    new_paper_list_list = []
    for group_name in os.listdir(INPUT_DIR):
        # each group can have one or multiple files
        group_dir = os.path.join(INPUT_DIR, group_name)
        txt_file_list = []
        for fn in os.listdir(group_dir):
            if fn.endswith('txt'):
                txt_file_list.append(os.path.join(group_dir, fn))
            elif fn.endswith('pdf'):
                extract_text_from_pdf(os.path.join(group_dir, fn), save_txt_file=True)
                txt_file_list.append(os.path.join(group_dir, os.path.splitext(fn)[0] + '.txt'))
            else:
                # ignore
                pass

        group_id = None
        new_paper_list = []
        for txt_file_path in txt_file_list:
            with open(txt_file_path, 'r') as txtf:
                paper_content = txtf.read()

            # only add new paper to existing database
            paper_hash = hashlib.sha256(paper_content.encode()).hexdigest()
            is_new = True
            for paper in cur_paper_list:
                if paper['hash'] == paper_hash:
                    is_new = False
                    break

            if is_new:
                paper_name = os.path.basename(txt_file_path)
                if group_id is None:
                    group_id = db.save_new_group(group_name)
                paper_id = db.save_new_paper(paper_content, paper_name, group_id)

                chunks = db.split_text_into_chunks(paper_content)
                for chunk in chunks:
                    db.save_new_chunk(chunk, paper_id=paper_id)

                new_paper_list.append(
                    {
                        'txt_path': txt_file_path,
                        'paper_id': paper_id,
                    }
                )

        if new_paper_list:
            new_paper_list_list.append(new_paper_list)

    return new_paper_list_list


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

    args = parser.parse_args()

    input_db_path = args.db_path
    if not os.path.isabs(input_db_path):
        input_db_path = os.path.join(os.getcwd(), input_db_path)

    parent_dir = pathlib.Path(input_db_path).parent
    if not parent_dir.exists():
        print(f'Please check your input database path. The parent directory "{parent_dir}" does not exist.')
        return None

    db.update_db_path(input_db_path)

    return args


def main():
    start_time = datetime.now()

    db.rm_db_tmp_file()

    if not INDEX_GRAPHRAG and not INDEX_RAPTOR:
        print('Please select at least one of the index options.')
        return

    if not check_config_example_dir():
        return

    if os.path.isdir(TMP_CONFIG_DIR):
        shutil.rmtree(TMP_CONFIG_DIR)

    args = process_arguments()
    if args is None:
        return

    new_paper_list_list = save_group_and_paper()

    if INDEX_GRAPHRAG:
        for new_paper_list in new_paper_list_list:
            if os.path.isdir(TMP_CONFIG_DIR):
                shutil.rmtree(TMP_CONFIG_DIR)
            shutil.copytree(CONFIG_EXAMPLE_DIR, TMP_CONFIG_DIR)

            group_name = ''

            for new_paper in new_paper_list:
                txt_file = new_paper['txt_path']
                shutil.copyfile(txt_file, os.path.join(TMP_CONFIG_DIR, 'input', os.path.basename(txt_file)))
                if not group_name:
                    group_name = os.path.basename(os.path.dirname(txt_file))

            # python -m graphrag.index --root ./ragtest
            p = subprocess.Popen(['python', '-m', 'graphrag.index', '--root', TMP_CONFIG_DIR])
            p.wait()

            if os.path.isdir(TMP_CONFIG_DIR):
                # shutil.rmtree(TMP_CONFIG_DIR)
                ymdhm = datetime.now().strftime('-%Y-%m-%d-%H-%M')
                shutil.move(TMP_CONFIG_DIR, TMP_CONFIG_DIR + '-' + group_name + ymdhm)

    end_time_graphrag = datetime.now()

    if INDEX_RAPTOR:
        raptor_index([p['paper_id'] for l in new_paper_list_list for p in l])

    end_time_raptor = datetime.now()

    print('graphrag run time:', end_time_graphrag - start_time)
    print('raptor run time:', end_time_raptor - end_time_graphrag)
    print('run time:', end_time_raptor - start_time)

    db.count_all_collection()

    db.rm_db_tmp_file()


if __name__ == '__main__':
    main()

