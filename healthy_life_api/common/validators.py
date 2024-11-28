from django.core.exceptions import ValidationError
from typing import Union
from PIL import Image


def validate_image(image, size_file_MB: float, max_len_name: int, max_x: int, max_y: int):
    size_to_bits = size_file_MB * 1024 * 1024
    if image.size > size_to_bits:
        raise ValidationError(f'ошибка: размер изображения не должен привышать {size_file_MB} МБ')

    if len(image.name) > max_len_name:
        raise ValidationError(f'ошибка: имя файла не должно превышать {max_len_name} символа')

    image_file = Image.open(image)
    if image_file.size[0] > max_x or image_file.size[1] > max_y:
        raise ValidationError(f'ошибка: максимальный размер изображения {max_x}x{max_y} пискселей')

    return image


def number_between(value: Union[float, int], number_a: Union[float, int], number_b: Union[float, int]):
    if number_a <= value <= number_b:
        return value

    raise ValidationError(f'value is not between {number_a} and {number_b}')


def number_gte(value: Union[float, int], number_then: Union[float, int]):
    if value < number_then:
        raise ValidationError(f'value is not greater than or equal to {number_then}')

    return value
