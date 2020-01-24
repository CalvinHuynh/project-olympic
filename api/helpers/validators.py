

def validate_dateformat(
        variable_name: str, date_text: str, format: str = '%Y-%m-%d'):
    import datetime as dt
    import re

    date_pattern = re.compile(r'\d{4}-\d{2}-\d{2}')
    if date_text:
        try:
            dt.datetime.strptime(date_text, format)
        except ValueError:
            raise ValueError(
                f"Incorrect date format for parameter {variable_name},"
                f"expected format is YYYY-MM-DD")
    else:
        raise ValueError(
            f"Input parameter {variable_name} cannot be null or empty,"
            f"expected format is YYYY-MM-Dd")

    if not date_pattern.match(date_text):
        raise ValueError(
            f"Incorrect date format for parameter {variable_name},"
            f"expected format is YYYY-MM-DD")
