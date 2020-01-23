
def validate_dateformat(date_text, format: str = '%Y-%m-%d'):
    import datetime as dt
    try:
        dt.datetime.strptime(date_text, format)
    except ValueError:
        raise ValueError(
            "Incorrect date format, expected format is YYYY-MM-DD")
