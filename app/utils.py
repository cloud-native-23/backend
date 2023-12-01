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

def generate_time_slots(start_date: date, start_time: int, end_date: date, end_time: int, stadium_open_hour: int, stadium_close_hour: int):
    

    current_datetime = dt.combine(start_date, dt.min.time()) + timedelta(hours=start_time)

    if current_datetime == dt.combine(end_date, dt.min.time()) + timedelta(hours=end_time):
        return ([{'date': current_datetime.date(), 'start_time': current_datetime.hour}])
    else:
        result = []
        while current_datetime < dt.combine(end_date, dt.min.time()) + timedelta(hours=end_time):
            current_date = current_datetime.date()
            current_hour = current_datetime.hour

            if stadium_open_hour <= current_hour < stadium_close_hour:
                result.append({'date': current_date, 'start_time': current_hour})

            current_datetime += timedelta(hours=1)

    return result