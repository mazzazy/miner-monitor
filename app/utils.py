from datetime import datetime, timezone, timedelta


def now():

    return datetime.now(
        timezone(
            timedelta(hours=4)
        )
    )


def now_string():

    return now().strftime(
        "%d/%m/%Y %H:%M:%S (UTC+4)"
    )