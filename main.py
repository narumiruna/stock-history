import argparse
import os
from collections import OrderedDict
from datetime import datetime, timedelta
from time import sleep

import tablib
import twstock
from dateutil.rrule import MONTHLY, rrule

from log import get_logger

logger = get_logger(__name__)

SID0050 = [
    '1101', '1102', '1216', '1301', '1303', '1326', '1402', '1722', '2002',
    '2105', '2201', '2207', '2301', '2303', '2308', '2311', '2317', '2324',
    '2325', '2330', '2347', '2353', '2354', '2357', '2382', '2409', '2412',
    '2454', '2474', '2498', '2801', '2880', '2881', '2882', '2883', '2885',
    '2886', '2890', '2891', '2892', '2912', '3008', '3045', '3231', '3481',
    '3673', '3697', '4904', '5880', '6505'
]

SID0051 = [
    '1227', '1304', '1314', '1319', '1434', '1440', '1504', '1507', '1590',
    '1605', '1704', '1710', '1717', '1723', '1789', '1802', '1907', '2006',
    '2015', '2049', '2101', '2103', '2106', '2204', '2327', '2337', '2344',
    '2356', '2360', '2362', '2371', '2379', '2384', '2385', '2388', '2392',
    '2393', '2395', '2448', '2450', '2451', '2501', '2504', '2511', '2542',
    '2545', '2548', '2603', '2606', '2607', '2609', '2610', '2615', '2618',
    '2707', '2723', '2727', '2809', '2812', '2823', '2834', '2845', '2855',
    '2884', '2887', '2888', '2889', '2903', '2915', '3034', '3037', '3044',
    '3149', '3189', '3406', '3474', '3702', '4725', '4938', '4958', '5522',
    '5871', '6005', '6176', '6239', '6269', '6285', '6286', '8008', '8046',
    '8078', '8422', '9904', '9907', '9914', '9917', '9921', '9933', '9940',
    '9945'
]


def get_month_range_until_now(year, month):
    start = datetime(year, month, 1)
    end = datetime.now()
    return rrule(MONTHLY, dtstart=start, until=end)


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
    parser.add_argument('-s', '--stock-number', type=str, default='0050')
    parser.add_argument(
        '-i',
        '--interval',
        type=int,
        default=2,
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
        logger.info(f'Fetching {sid} {year}/{month}')
        month_data = stock.fetch(year, month)
        sleep(interval)

        if len(month_data) == 0:
            logger.info(f'This month ({year}/{month}) has no data, stop here')
            break

        for day_data in month_data:
            history[day_data.date] = day_data

    return history

def save_history(history, f):
    logger.info(f'Saving history to {f}')

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
    # args = parse_arg()
    # sid = args.stock_number
    # interval = args.interval
    interval = 2


    for sid in SID0050:
        try:
            history = fetch_history(sid, interval)
        except Exception as e:
            print(e)
            continue

        f = f'sid0050/sid{sid}.csv'
        os.makedirs(os.path.dirname(f), exist_ok=True)
        save_history(history,f)
    
    for sid in SID0051:
        try:
            history = fetch_history(sid, interval)
        except Exception as e:
            print(e)
            continue

        history = fetch_history(sid, interval)
        f = f'sid0051/sid{sid}.csv'
        os.makedirs(os.path.dirname(f), exist_ok=True)
        save_history(history,f)


if __name__ == "__main__":
    main()
