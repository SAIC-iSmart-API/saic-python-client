import abc
import datetime
import re


class BaseData(abc.ABC):
    def __init__(self):
        self.code: int | None = None
        self.message: str | None = None

    def init_from_dict(self, data: dict):
        self.code = int(data.get('code'))
        self.message = data.get('message')
        return self


TZ_REGEX = re.compile(r'^(?P<base>GMT|UTC)(?P<sign>[+-])(?P<hour>\d{1,2})(:(?P<minute>\d{2}))?$')


class TimeZoneEntity():
    def __init__(self):
        self.timezone = None

    def init_from_dict(self, data: dict):
        self.timezone = data.get('timezone')
        return self

    def __str__(self):
        return f'{{"timezone": "{self.timezone}"}}'

    def get_timezone_offset(self):
        m = TZ_REGEX.match(self.timezone)
        if m is not None:
            sign = m.group('sign')
            hours = int(m.group('hour'))
            minutes = int(m.group('minute')) if m.group('minute') is not None else 0
            if sign == '+':
                offset = datetime.timedelta(hours=hours, minutes=minutes)
            else:
                offset = -datetime.timedelta(hours=hours, minutes=minutes)
            return datetime.timezone(offset=offset, name=self.timezone)
        else:
            raise ValueError(f'Invalid timezone: {self.timezone}')


class TimeZoneResponse(BaseData):
    def __init__(self):
        super().__init__()
        self.data: TimeZoneEntity | None = None

    def init_from_dict(self, data: dict):
        super().init_from_dict(data)
        self.data = TimeZoneEntity().init_from_dict(data.get('data'))
        return self

    def __str__(self):
        return f'{{"code": {self.code}, "message": "{self.message}", "data": {self.data}}}'
