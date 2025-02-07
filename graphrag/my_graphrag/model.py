import os
import threading
import requests
from sglang.utils import (
    execute_shell_command,
    wait_for_server,
    terminate_process,
)
from pathlib import Path


PRJ_DIR = os.path.join(Path(os.path.dirname(os.path.realpath(__file__))).parent.parent.absolute())
MODEL_DIR = os.path.join(PRJ_DIR, 'models')
# https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct
MODEL_NAME_LLAMA = 'Llama-3.1-8B-Instruct'
# https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Llama-8B
MODEL_NAME_DEEPSEEK = 'DeepSeek-R1-Distill-Llama-8B'

MODEL_TMP_FILE_PATH = os.path.join(PRJ_DIR, './my_graphrag/model_tmp_file.txt')


SERVER_PROCESS = None
LOCK = threading.RLock()


def check_model_dir():
    if not os.path.isdir(MODEL_DIR):
        os.mkdir(MODEL_DIR)

    model_path_llama = os.path.join(MODEL_DIR, MODEL_NAME_LLAMA)
    if os.path.isdir(model_path_llama):
        if len(os.listdir(model_path_llama)) == 0:
            raise Exception(f'Model {MODEL_NAME_LLAMA} found in {model_path_llama} but it is empty. Please download the model.')

        try:
            start_sgl_server_llama()
        except:
            raise Exception(f'Model {MODEL_NAME_LLAMA} found in {model_path_llama} but failed to start SGL server. Please check the model.')
        finally:
            stop_sgl_server()
    else:
        raise Exception(f'Model {MODEL_NAME_LLAMA} not found in {model_path_llama}. Please download the model.')

    model_path_deepseek = os.path.join(MODEL_DIR, MODEL_NAME_DEEPSEEK)
    if os.path.isdir(model_path_deepseek):
        if len(os.listdir(model_path_deepseek)) == 0:
            raise Exception(f'Model {MODEL_NAME_DEEPSEEK} found in {model_path_deepseek} but it is empty. Please download the model.')

        try:
            start_sgl_server_deepseek()
        except:
            raise Exception(f'Model {MODEL_NAME_DEEPSEEK} found in {model_path_deepseek} but failed to start SGL server. Please check the model.')
        finally:
            stop_sgl_server()
    else:
        raise Exception(f'Model {MODEL_NAME_DEEPSEEK} not found in {model_path_deepseek}. Please download the model.')


def start_sgl_server(model_name):
    global SERVER_PROCESS

    tmp_file_model_path = get_cur_model_path()

    with LOCK:
        if SERVER_PROCESS is not None or tmp_file_model_path:
            print(f'SGL server is already running with {tmp_file_model_path}. Please stop the server first.')

        else:
            model_path = os.path.join(MODEL_DIR, model_name)
            if not os.path.exists(model_path):
                raise Exception(f'Model not found in {model_path}. Please download the model first.')

            server_process = execute_shell_command(f'python -m sglang.launch_server --model-path {model_path} --port 30000 --host 0.0.0.0')
            SERVER_PROCESS = server_process
            update_model_tmp_file(model_path)

            wait_for_server("http://localhost:30000")

            print(f'SGL server started with {model_path}.')


def start_sgl_server_llama():
    start_sgl_server(MODEL_NAME_LLAMA)


def start_sgl_server_deepseek():
    start_sgl_server(MODEL_NAME_DEEPSEEK)


def stop_sgl_server():
    global SERVER_PROCESS

    tmp_file_model_path = get_cur_model_path()

    with LOCK:
        if SERVER_PROCESS is not None:
            try:
                terminate_process(SERVER_PROCESS)
            except:
                pass
            print(f'SGL server stopped with {tmp_file_model_path}.')

        else:
            print('SGL server is not running.')

        SERVER_PROCESS = None

    remove_model_tmp_file()


def get_response_from_sgl(prompt, remove_think=True):
    output = ''
    try:
        tmp_file_model_path = get_cur_model_path()

        if tmp_file_model_path:
            data = {
                "model": tmp_file_model_path,
                "messages": [{"role": "user", "content": prompt}],
            }
            response = requests.post(
                "http://localhost:30000/v1/chat/completions",
                json=data
            )
            output = response.json()['choices'][0]['message']['content']

            if remove_think:
                output = output.split('</think>')[-1].strip()

    except:
        print('Failed to get response from SGL server.')

    return output


def update_model_tmp_file(cur_model_path):
    with open(MODEL_TMP_FILE_PATH, 'w') as f:
        f.write(cur_model_path)
        f.flush()


def remove_model_tmp_file():
    if os.path.isfile(MODEL_TMP_FILE_PATH):
        os.remove(MODEL_TMP_FILE_PATH)


def get_cur_model_path():
    if os.path.isfile(MODEL_TMP_FILE_PATH):
        with open(MODEL_TMP_FILE_PATH, 'r') as f:
            return f.read().strip()
    return ''
