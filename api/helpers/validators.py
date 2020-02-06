

def validate_dateformat(
        variable_name: str, date_text: str, format: str = '%Y-%m-%d'):
    """Validates that the given parameter is of a specific date format

    Arguments:
        variable_name {str} -- Name of variable to check
        date_text {str} -- Value of the variable

    Keyword Arguments:
        format {str} -- Date format to check (default: {'%Y-%m-%d'})
    """
    import datetime as dt
    import re

    date_pattern = re.compile(r'\d{4}-\d{2}-\d{2}')
    if isinstance(date_text, dt.datetime) or isinstance(date_text, dt.date):
        pass
    else:
        if date_text:
            try:
                dt.datetime.strptime(date_text, format)
            except ValueError:
                raise ValueError(
                    f"Incorrect date format for parameter {variable_name},"
                    f" expected format is YYYY-MM-DD")
        else:
            raise ValueError(
                f"Input parameter {variable_name} cannot be null or empty,"
                f" expected format is YYYY-MM-Dd")

        if not date_pattern.match(date_text):
            raise ValueError(
                f"Incorrect date format for parameter {variable_name},"
                f" expected format is YYYY-MM-DD")


def validate_string_bool(input: str):
    """Validates that the given parameter is a boolean

    Arguments:
        input {str} -- Input to check

    Returns:
        bool -- Returns boolean of input if it passes the regex
    """
    import re
    input = str(input)

    bool_regex = re.compile(r'^(true|false)$')
    if bool_regex.match(input.lower()):
        if input.lower() == 'true':
            return True
        return False
    else:
        raise ValueError(
            f"Input {input} does not match the values true or false.")


def validate_string_int(input: str):
    """Validates that the given parameter is an int

    Arguments:
        input {str} -- Input to check

    Returns:
        int -- Returns an int representation of the input string
    """
    try:
        int_val = int(input)
        return int_val
    except ValueError:
        raise ValueError("Input is not of type int")
