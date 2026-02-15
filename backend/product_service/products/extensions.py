# products/extensions.py
from drf_spectacular.extensions import OpenApiSerializerFieldExtension
from drf_spectacular.plumbing import ResolvedComponent
from drf_spectacular.types import OpenApiTypes

# Важливо: імпортуй реальний клас
from cloudinary.models import CloudinaryField


class CloudinaryFieldInModelFieldExtension(OpenApiSerializerFieldExtension):
    target_class = 'rest_framework.fields.ModelField'  # саме ModelField в серіалайзері

    priority = 1  # вищий пріоритет — щоб перехопити раніше за дефолт

    def map_serializer_field(self, auto_schema, direction):
        model_field = getattr(auto_schema.field, 'model_field', None)

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

        # якщо не наш випадок — пропускаємо далі
        return None  # або super().map_serializer_field(...) — але None безпечніше тут