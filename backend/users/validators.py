from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.deconstruct import deconstructible


@deconstructible
class UTMSourceValidator(RegexValidator):
    regex = r"^[a-zA-Z0-9_]+$"
    message = "UTM-метка может содержать только латинские буквы, цифры и символ подчеркивания."
    code = "invalid_utm_source"


validate_utm_source_format = UTMSourceValidator()


def validate_utm_source(value: str):
    if len(value) > 64:
        raise ValidationError("UTM-метка не может быть длиннее 64 символов.")
    validate_utm_source_format(value)
