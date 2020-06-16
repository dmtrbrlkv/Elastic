from es_client import get_client, load_to_index
from consts import FLIGHTS_INDEX, FLIGHTS_FN


def main():
    client = get_client()
    load_to_index(client, FLIGHTS_INDEX, FLIGHTS_FN)


if __name__ == "__main__":
    main()