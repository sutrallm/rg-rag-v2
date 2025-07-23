import argparse
import graphrag.my_graphrag.cloud as model


def main():
    parser = argparse.ArgumentParser(description="Check connection to OpenAI API")
    parser.add_argument("--prompt", default="hello", help="the prompt")
    args = parser.parse_args()

    model.check_model_dir()
    model.start_sgl_server_deepseek()
    prompt = args.prompt
    response = model.get_response_from_sgl(prompt)
    print(prompt)
    print(response)
    model.stop_sgl_server()


if __name__ == '__main__':
    main()
