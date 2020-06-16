import csv

from elasticsearch_dsl import Search

from es_client import get_es_client, es_arg_parser
from consts import FLIGHTS_INDEX


def delay_per_carrier(es):
    s = Search(using=es, index=FLIGHTS_INDEX)
    # s = s.exclude("match", DistanceKilometres=0)
    s = s.exclude("match", Cancelled=True)

    s.aggs.bucket('delay_per_carrier', 'terms', field='Carrier.keyword').metric("avg_delay", 'avg',
                                                                                field='FlightDelayMin')

    response = s.execute()
    res = []
    for delay in response.aggregations.delay_per_carrier.buckets:
        res.append((delay.key, delay.avg_delay.value))

    return res


def delays_to_csv(delays, filename):
    with open(filename, "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(("Carrier", "Average FlightDelayMin"))

        for delay in delays:
            writer.writerow(delay)


def load_args():
    arg_parser = es_arg_parser()
    arg_parser.add_argument("-f", "--filename", action="store", default="delays.csv")

    return arg_parser.parse_args()


def main():
    args = load_args()

    host = args.host
    port = args.port
    filename = args.filename
    client = get_es_client(host, port)

    delays = delay_per_carrier(client)
    delays_to_csv(delays, filename)


if __name__ == "__main__":
    main()
