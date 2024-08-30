null_values = ["null", "Null", "NULL", "none", "None", "NONE"]


def parse_null(value: str | None = None, exclude=""):
    if value == exclude:
        return value

    if value is None or value in null_values or value == "":
        return None

    return value
