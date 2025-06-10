import base64
import six
import uuid

from django.core.files.base import ContentFile
from rest_framework import serializers


class Base64ImageField(serializers.ImageField):
    """Поле сериализатора для обработки изображений в формате base64."""

    def to_internal_value(self, data):
        
        if isinstance(data, six.string_types):
            
            if 'data:image' in data and ';base64,' in data:
                header, base64_string = data.split(';base64,')
                try:
                    decoded_file = base64.b64decode(base64_string)
                except TypeError:
                    self.fail('invalid_image')

                
                file_extension = header.split('/')[1]
                
                file_name = str(uuid.uuid4()) + "." + file_extension

                data = ContentFile(decoded_file, name=file_name)

        return super(Base64ImageField, self).to_internal_value(data) 