from datetime import datetime, timedelta


def parse_time(text, src_fmt=None, to_fmt=None, **kwargs):
    if isinstance(text, (int, float)):
        dt = datetime.fromtimestamp(text) + timedelta(**kwargs)
    else:
        dt = datetime.strptime(str(text), src_fmt) + timedelta(**kwargs)
    if to_fmt is not None:
        return dt.strftime(to_fmt)
    else:
        return dt.timestamp()


def now(layout=None, accuracy=None, **kwargs):
    dt = datetime.now() + timedelta(**kwargs)

    def with_accuracy():
        sec = int(dt.timestamp())
        micros = sec*1000000+dt.microsecond
        if 'micros' == accuracy:
            return micros
        if 'mills' == accuracy:
            return int(str(micros)[:-3])
        return sec
    return dt.strftime(layout) if layout else with_accuracy()
