from marshmallow import ValidationError

__all__ = ['is_positive_number']


def is_positive_number(value: int) -> None:
    """
    Checking value to above then 0

    Args:
        value (int): Value to checking
    Returns:
        None: If value is above then 0
    Raises:
        ValidationError: If Value is less than 0
    """
    if value < 0:
        raise ValidationError('Value must be positive')
