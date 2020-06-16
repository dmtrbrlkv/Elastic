from es_client import get_es_client, load_to_index, es_arg_parser
from consts import LOGS_INDEX, LOGS_FN


def load_args():
    arg_parser = es_arg_parser()
    return arg_parser.parse_args()


def main():
    args = load_args()
    host = args.host
    port = args.port
    client = get_es_client(host, port)
    load_to_index(client, LOGS_INDEX, LOGS_FN)


if __name__ == "__main__":
    main()
