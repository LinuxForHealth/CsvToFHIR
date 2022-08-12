def validate_ssn(v):
    """
    Validates that the ssn is a valid SSN
    :param v: The snn value
    :return: The snn value (without dashes) or None if resource value is invalid
    :raise: ValueError if the resourceType is invalid.
    """
    if not v:
        return None  # None is a valid value

    value = v.replace("-", "")
    if len(value) != 9:
        return None

    if not value.isdecimal():
        return None  # must contain only numbers

    s = set(value)
    if len(s) <= 1:
        return None  # remove common ssn place holders 000-00-0000 or 999-99-9999

    return value
