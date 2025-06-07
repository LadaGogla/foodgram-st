import base64
import six
import uuid

from django.core.files.base import ContentFile
from rest_framework import serializers


class Base64ImageField(serializers.ImageField):
    """Поле сериализатора для обработки изображений в формате base64."""

    def to_internal_value(self, data):
        # Проверяем, если данные не строка base64, обрабатываем как обычный файл
        if isinstance(data, six.string_types):
            # Проверяем, является ли строка base64 изображением
            if 'data:image' in data and ';base64,' in data:
                header, base64_string = data.split(';base64,')
                try:
                    decoded_file = base64.b64decode(base64_string)
                except TypeError:
                    self.fail('invalid_image')

                # Определяем расширение файла
                file_extension = header.split('/')[1]
                # Генерируем уникальное имя файла
                file_name = str(uuid.uuid4()) + "." + file_extension

                data = ContentFile(decoded_file, name=file_name)

        return super(Base64ImageField, self).to_internal_value(data) 