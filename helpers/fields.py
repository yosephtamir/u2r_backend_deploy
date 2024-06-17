from django.db import models 
from django.core.validators import FileExtensionValidator
from .validators import ImageSizeValidator
from .validators import FileSizeValidator


class ValidatedImageField(models.ImageField):

    def __init__(self, *args, **kwargs):
        allowed_extensions = kwargs.pop('extensions', ('png', 'jpg', 'jpeg', 'jfif'))
        max_bytes_size = int(kwargs.get('max_bytes_size', 5*1024*1024))
        size_validator = ImageSizeValidator(max_bytes_size)
        extension_validator = FileExtensionValidator(allowed_extensions=(allowed_extensions))
        kwargs.setdefault('validators', [size_validator, extension_validator])
        return super().__init__(*args, **kwargs)


class ValidatedResumeFileField(models.FileField):

    def __init__(self, *args, **kwargs):
        allowed_extensions = kwargs.pop('extensions', ('pdf', 'docx')) # open to deliberation
        size_validator = FileSizeValidator(5*1024*1024)
        extension_validator = FileExtensionValidator(allowed_extensions=allowed_extensions)
        kwargs.setdefault('validators', [size_validator, extension_validator])
        return super().__init__(*args, **kwargs)
