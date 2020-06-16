from elasticsearch import Elasticsearch
from argparse import ArgumentParser
import json

from consts import HOST, PORT


def es_arg_parser():
    arg_parser = ArgumentParser()
    arg_parser.add_argument("-H", "--host", action="store", default=HOST)
    arg_parser.add_argument("-P", "--port", action="store", type=int, default=PORT)

    return arg_parser


def get_es_client(host=HOST, port=PORT):
    return Elasticsearch(host + ":" + str(port))


def load_to_index(client, index, filename):
    with open(filename) as f:
        datas = json.load(f)

    if not client.indices.exists(index):
        client.indices.create(index)

    for data in datas:
        client.index(index, data)
