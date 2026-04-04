# products/hooks.py
from drf_spectacular.plumbing import build_object_type  # ← тільки це


def postprocess_unified_schema(result, generator, request, public):
    """
    Постпроцесінг хук: Обгортає ВСІ відповіді в уніфікований формат.
    """
    print("HOOK CALLED! Processing schema...")
    print(f"Request: {request}, Public: {public}")

    paths = result.get('paths', {})

    for path, path_item in paths.items():
        for method, operation in path_item.items():
            responses = operation.get('responses', {})

            for status_code, response in responses.items():
                is_success = int(status_code) < 400
                content = response.get('content', {}).get('application/json', {})
                original_schema = content.get('schema')

                if original_schema:
                    unified_properties = {
                        'success': {'type': 'boolean'},
                        'message': {'type': 'string', 'nullable': True},
                    }

                    if is_success:
                        unified_properties['data'] = original_schema
                        unified_properties['errors'] = {'type': 'null'}
                    else:
                        unified_properties['data'] = {'type': 'null'}
                        unified_properties['errors'] = {
                            'type': 'array',
                            'items': {
                                'type': 'object',
                                'properties': {
                                    'field': {'type': 'string', 'nullable': True},
                                    'message': {'type': 'string'},
                                    'code': {'type': 'string', 'nullable': True}
                                }
                            }
                        }

                    unified_schema = build_object_type(
                        properties=unified_properties,
                        required=['success']
                    )

                    content['schema'] = unified_schema

    return result