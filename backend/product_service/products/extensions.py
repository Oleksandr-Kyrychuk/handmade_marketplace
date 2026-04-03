# products/extensions.py
from drf_spectacular.extensions import OpenApiSerializerFieldExtension
from drf_spectacular.plumbing import ResolvedComponent
from drf_spectacular.types import OpenApiTypes
from cloudinary.models import CloudinaryField

class CloudinaryFieldInModelFieldExtension(OpenApiSerializerFieldExtension):
    target_class = 'rest_framework.fields.ModelField'

    priority = 1

    def map_serializer_field(self, auto_schema, direction):
        # Новий безпечний спосіб отримати model_field
        field = getattr(auto_schema, '_field', None) or getattr(auto_schema, 'field', None)
        if field is None:
            return None  # пропустити, якщо не знайшли

        model_field = getattr(field, 'model_field', None)

        if model_field is not None and isinstance(model_field, CloudinaryField):
            return ResolvedComponent(
                name='CloudinaryUrl',
                type=OpenApiTypes.STR,
                schema={
                    'type': 'string',
                    'format': 'uri',
                    'nullable': True,
                    'example': 'https://res.cloudinary.com/.../image.jpg',
                    'description': 'Cloudinary-hosted image public URL',
                }
            )

        return None