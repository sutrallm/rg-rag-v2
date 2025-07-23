import os
from openai import OpenAI
from pathlib import Path

PRJ_DIR = os.path.join(Path(os.path.dirname(os.path.realpath(__file__))).parent.parent.absolute())
MODEL_TMP_FILE_PATH = os.path.join(PRJ_DIR, './my_graphrag/model_tmp_file.txt')

client = None

def check_model_dir():
    api_token = os.environ.get("DEEPSEEK_API_TOKEN")
    if not api_token:
        print("Error: missing DEEPSEEK_API_TOKEN environment variable")
        exit(1)

    api_model = os.environ.get("DEEPSEEK_API_MODEL")
    if not api_model:
        print("Error: missing DEEPSEEK_API_MODEL environment variable")
        exit(1)

    api_url = os.environ.get("DEEPSEEK_API_URL")
    if not api_url:
        print("Error: missing DEEPSEEK_API_URL environment variable")
        exit(1)

    print(f'check_model_dir()')


def start_sgl_server():
    print(f'start_sgl_server({os.environ.get("DEEPSEEK_API_MODEL")})')

    global client
    client = OpenAI(
        base_url=os.environ.get("DEEPSEEK_API_URL"),
        api_key=os.environ.get("DEEPSEEK_API_TOKEN"),
    )


def start_sgl_server_llama():
    start_sgl_server()


def start_sgl_server_deepseek():
    start_sgl_server()


def stop_sgl_server():
    print(f'stop_sgl_server()')


def get_response_from_sgl(prompt, remove_think=True):
    if client is None:
        start_sgl_server()

    output = ''
    completion = client.chat.completions.create(
        model=os.environ.get("DEEPSEEK_API_MODEL"),
        messages=[{
            "role": "user",
            "content": prompt,
        }],
        timeout=300,
    )
    output = completion.choices[0].message.content

    if remove_think:
        output = output.split('</think>')[-1].strip()

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
