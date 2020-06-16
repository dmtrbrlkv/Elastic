from es_client import get_client, load_to_index
from consts import LOGS_INDEX, LOGS_FN


def main():
    client = get_client()
    load_to_index(client, LOGS_INDEX, LOGS_FN)


if __name__ == "__main__":
    main()