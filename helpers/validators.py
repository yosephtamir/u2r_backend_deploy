
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _

@deconstructible
class ImageSizeValidator:
    def __init__(self, max_bytes_size=5*1024*1024):
        self.max_bytes_size = max_bytes_size
    
    def __call__(self, image):
        image_size_in_bytes = image.file.size

        if image_size_in_bytes > self.max_bytes_size:
            raise ValidationError(f"File Size cannot be more than {self.max_bytes_size/(1024*1024)}MB")

@deconstructible
class FileSizeValidator:
    def __init__(self, max_bytes_size=5*1024*1024):
        self.max_bytes_size = max_bytes_size
    
    def __call__(self, file):
        file_size_in_bytes = file.size

        if file_size_in_bytes > self.max_bytes_size:
            raise ValidationError(f"File Size cannot be more than {self.max_bytes_size/(1024*1024)}MB")

def validate_positive_decimal(value):
    if value < 0:
        raise ValidationError(
            _(f'{value} is not a positive decimal')
        )