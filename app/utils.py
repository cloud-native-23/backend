from datetime import datetime as dt, timedelta, date
import multiprocessing

import pytz


def get_tw_time() -> str:
    tw = pytz.timezone("Asia/Taipei")
    twdt = tw.localize(dt.datetime.now()).strftime("%Y-%m-%d %H:%M:%S %Z%z")
    return twdt

def number_of_workers():
    return max(multiprocessing.cpu_count() + 1, 1)

def get_weekday(date_str: str, timezone_str: str = 'Asia/Taipei', date_str_format: str = '%Y-%m-%d') -> int:
    datetime_obj = dt.datetime.strptime(date_str, date_str_format)
    return datetime_obj.astimezone(pytz.timezone(timezone_str)).weekday() + 1