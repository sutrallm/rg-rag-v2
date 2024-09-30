import os
import shutil
import subprocess
import pdftotext
from datetime import datetime
from graphrag.my_graphrag.db import save_new_group, save_new_paper, count_all_collection
from graphrag.my_graphrag.conf import INDEX_RAPTOR, INDEX_GRAPHRAG
from graphrag.my_graphrag.raptor import raptor_index

FILE_DIR = os.path.dirname(os.path.realpath(__file__))
PRJ_DIR = os.path.join(FILE_DIR, './my_graphrag')
CONFIG_EXAMPLE_DIR = os.path.join(PRJ_DIR, 'config_example')
INPUT_DIR = os.path.join(PRJ_DIR, 'input_groups')
TMP_CONFIG_DIR = os.path.join(PRJ_DIR, 'output/tmp_config')
DATABASE_PATH = os.path.join(PRJ_DIR, 'vector_database')


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

        if len(txt_file_list) != 0:
            group_id = save_new_group(group_name)
            for txt_file_path in txt_file_list:
                with open(txt_file_path, 'r') as txtf:
                    paper_content = txtf.read()
                paper_name = os.path.splitext(os.path.basename(txt_file_path))[0]
                save_new_paper(paper_content, paper_name, group_id)


def main():
    start_time = datetime.now()

    if not INDEX_GRAPHRAG and not INDEX_RAPTOR:
        print('Please select at least one of the index options.')
        return

    if not os.path.isdir(CONFIG_EXAMPLE_DIR):
        print('Please put the config example on ' + CONFIG_EXAMPLE_DIR)
        return

    if os.path.isdir(TMP_CONFIG_DIR):
        shutil.rmtree(TMP_CONFIG_DIR)

    if os.path.isdir(DATABASE_PATH):
        shutil.rmtree(DATABASE_PATH)

    save_group_and_paper()

    if INDEX_GRAPHRAG:
        for group_name in os.listdir(INPUT_DIR):
            # each group can have one or multiple files
            group_dir = os.path.join(INPUT_DIR, group_name)
            txt_file_list = []
            for fn in os.listdir(group_dir):
                if fn.endswith('txt'):
                    txt_file_list.append(os.path.join(group_dir, fn))

            if os.path.isdir(TMP_CONFIG_DIR):
                shutil.rmtree(TMP_CONFIG_DIR)
            shutil.copytree(CONFIG_EXAMPLE_DIR, TMP_CONFIG_DIR)

            if len(txt_file_list) != 0:
                for txt_file in txt_file_list:
                    shutil.copyfile(txt_file, os.path.join(TMP_CONFIG_DIR, 'input', os.path.basename(txt_file)))

                # python -m graphrag.index --root ./ragtest
                p = subprocess.Popen(['python', '-m', 'graphrag.index', '--root', TMP_CONFIG_DIR])
                p.wait()

                if os.path.isdir(TMP_CONFIG_DIR):
                  # shutil.rmtree(TMP_CONFIG_DIR)
                  ymdhm = datetime.now().strftime('-%Y-%m-%d-%H-%M')
                  shutil.move(TMP_CONFIG_DIR, TMP_CONFIG_DIR+ymdhm)

    end_time_graphrag = datetime.now()

    if INDEX_RAPTOR:
        raptor_index()

    end_time_raptor = datetime.now()

    print('graphrag run time:', end_time_graphrag - start_time)
    print('raptor run time:', end_time_raptor - end_time_graphrag)
    print('run time:', end_time_raptor - start_time)

    count_all_collection()


if __name__ == '__main__':
    main()

