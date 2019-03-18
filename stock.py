import urllib
from datetime import datetime
from typing import NamedTuple

import requests

from utils import save_json


class StockData(NamedTuple):
    date: str
    capacity: int
    turnover: int
    open: float
    high: float
    low: float
    close: float
    change: float
    transaction: int


TWSE_URL = 'http://www.twse.com.tw/'


class ResponseData(object):
    def __init__(self, data):
        self.stat = None
        self.date = None
        self.title = None
        self.fields = None
        self.notes = None

        self._parse(data)
        self._parse_data(data)

    def _parse(self, data):
        self.stat = data['stat']
        if self.stat != 'OK':
            return

        self.date = datetime.strptime(data['date'], '%Y%m%d')
        self.title = data['title']
        self.fields = data['fields']
        self.notes = data['notes']

        self._parse_data(data)

    def _parse_data(self, data):
        self.data = []
        for d in data['data']:
            print(d)
            item = StockData(*d)
            self.data.append(item)


class TwseAPI(object):
    def __init__(self):
        self._session = requests.session()

    def get(self, year, month, sid):
        report_url = urllib.parse.urljoin(TWSE_URL, 'exchangeReport/STOCK_DAY')

        params = {'date': '%d%02d01' % (year, month), 'stockNo': sid}
        response = self._session.get(report_url, params=params)

        data = response.json()

        return data


api = TwseAPI()
data = api.get(2012, 8, '0050')
print(ResponseData(data))
