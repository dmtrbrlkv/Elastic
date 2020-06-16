from csv import writer
from datetime import datetime
from dateutil import parser
from argparse import ArgumentTypeError

from elasticsearch_dsl import Search

from es_client import get_es_client, es_arg_parser
from consts import LOGS_INDEX

import matplotlib as mpl
import matplotlib.pyplot as plt


def bytes_per_host(es, dt_begin, dt_end):
    s = Search(using=es, index=LOGS_INDEX)

    s = s.filter('range', timestamp={"from": dt_begin, "to": dt_end})

    s.aggs \
        .bucket('bytes_per_day', 'date_histogram', field='timestamp', calendar_interval='day') \
        .bucket('bytes_per_host', 'terms', field='host.keyword') \
        .metric("sum_bytes", 'sum', field='bytes')

    response = s.execute()
    res = []
    for per_day in response.aggregations.bytes_per_day.buckets:
        day = per_day.key_as_string

        for bytes_per_host in per_day.bytes_per_host.buckets:
            res.append((day, bytes_per_host.key, bytes_per_host.sum_bytes.value))

    return res


def bytes_per_host_to_csv(bytes_per_day, filename):
    with open(filename, "w", newline='') as f:
        csv_writer = writer(f)
        csv_writer.writerow(("Date", "Host", "Sum of bytes"))

        for bytes_per_host in bytes_per_day:
            day, host, bytes = bytes_per_host
            day = parser.parse(day)
            day = day.strftime("%d.%m.%Y")

            csv_writer.writerow((day, host, bytes))


def bytes_per_host_to_img(bytes_per_day, filename):
    plt.figure(figsize=(15, 10))

    by_host_x = {}
    by_host_y = {}

    for per_day in bytes_per_day:
        day, host, bytes = per_day
        if host not in by_host_x:
            by_host_x[host] = []
            by_host_y[host] = []

        by_host_x[host].append(parser.parse(day))
        by_host_y[host].append(bytes)

    hosts = by_host_x.keys()

    for host in hosts:
        plt.bar(by_host_x[host], by_host_y[host], label=host)

    plt.xlabel("Date", fontdict={"weight": "bold"})
    plt.ylabel("Sum of bytes", fontdict={"weight": "bold"})
    plt.title("Sum of bytes per day", fontdict={"weight": "bold", "size": 20})
    plt.legend()
    # plt.show()
    with open(filename, "w") as f:
        plt.savefig(filename)


def load_args():
    def valid_date(s):
        try:
            return datetime.strptime(s, "%Y-%m-%d")
        except ValueError:
            msg = f"Not a valid date: '{s}'."
            raise ArgumentTypeError(msg)

    arg_parser = es_arg_parser()
    arg_parser.add_argument("-b", "--begin", action="store", type=valid_date, default="2019-03-01")
    arg_parser.add_argument("-e", "--end", action="store", type=valid_date, default="2019-04-01")
    arg_parser.add_argument("-f", "--filename", action="store", default="bytes.csv")
    arg_parser.add_argument("-i", "--imagename", action="store", default="bytes.png")

    return arg_parser.parse_args()


def main():
    args = load_args()

    host = args.host
    port = args.port
    dt_begin = args.begin
    dt_end = args.end
    csv_filename = args.filename
    img_filename = args.imagename

    client = get_es_client(host, port)
    bytes_per_day = bytes_per_host(client, dt_begin, dt_end)
    bytes_per_host_to_csv(bytes_per_day, csv_filename)
    bytes_per_host_to_img(bytes_per_day, img_filename)


if __name__ == "__main__":
    main()
