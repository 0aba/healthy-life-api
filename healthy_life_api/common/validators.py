from django.core.exceptions import ValidationError
from PIL import Image as PilImage


def validate_image(image, size_file_MB: float, max_len_name: int, max_x: int, max_y: int):
    size_to_bits = size_file_MB * 1024 * 1024
    if image.size > size_to_bits:
        raise ValidationError(f'Error: image size must not exceed {size_file_MB} MB')

    if len(image.name) > max_len_name:
        raise ValidationError(f'Error: file name must not exceed {max_len_name} characters')

    image_file = PilImage.open(image)
    if image_file.size[0] > max_x or image_file.size[1] > max_y:
        raise ValidationError(f'Error: image size must not exceed {max_x}x{max_y} pixels')

    return image

