import argparse
import os
from collections import OrderedDict
from datetime import datetime
from time import sleep

import tablib
import twstock

from log import get_logger

LOGGER = get_logger(__name__)

class DateTimeIter(object):
    def __init__(self, date, delta):
        self.date = date
        self.delta = delta

        self.min = datetime(1900, 1, 1)
        self.max = datetime.now()

    def __next__(self):
        out = self.date
        self.date += self.delta

        if out < self.min or out > self.max:
            raise StopIteration

        return out

    def __iter__(self):
        return self


class MonthIter(object):
    def __init__(self, year, month, min_year=1900):
        self.year = year
        self.month = month
        self.min_year = min_year

    def __next__(self):
        cur = datetime(self.year, self.month, 1)

        self.month -= 1

        if cur.month == 1:
            self.month = 12
            self.year -= 1

        if cur.year < self.min_year:
            raise StopIteration

        return cur.year, cur.month

    def __iter__(self):
        return self


def parse_arg():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--stock', type=str, default='0050')
    parser.add_argument('-o', '--output-dir', type=str, default='data')
    parser.add_argument(
        '-i',
        '--interval',
        type=int,
        default=5,
        help='Fetech interval in seconds')

    return parser.parse_args()


def save_csv(dataset, f):
    with open(f, 'w', newline='') as fp:
        fp.write(dataset.export('csv'))


def fetch_history(sid, interval):
    now = datetime.now()
    months = MonthIter(now.year, now.month)

    history = OrderedDict()

    # fetch
    stock = twstock.Stock(sid, initial_fetch=False)
    for year, month in months:
        LOGGER.info(f'Fetching {sid} {year}/{month}')
        month_data = stock.fetch(year, month)
        sleep(interval)

        if len(month_data) == 0:
            LOGGER.info(f'This month ({year}/{month}) has no data, stop here')
            break

        for day_data in month_data:
            history[day_data.date] = day_data

    return history


def save_history(history, f):
    os.makedirs(os.path.dirname(f), exist_ok=True)

    LOGGER.info(f'Saving history to {f}')

    # use tablib to save as csv file
    headers = ('date', 'capacity', 'turnover', 'open', 'high', 'low', 'close',
               'change', 'transaction')
    dataset = tablib.Dataset(headers=headers)

    for date in sorted(history.keys()):
        day_data = history[date]

        day_data = list(day_data._asdict().values())
        day_data[0] = day_data[0].strftime('%Y%m%d')
        dataset.append(day_data)

    save_csv(dataset, f)


def main():
    args = parse_arg()

    history = fetch_history(args.stock, args.interval)

    if history.values():
        f = os.path.join(args.output_dir, '{}.csv'.format(args.stock))
        save_history(history, f)


if __name__ == "__main__":
    main()
