from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import ModelSerializer


class JsonApiV11ModelSerializer(ModelSerializer):

    def to_representation(self, obj):
        rep = super().to_representation(obj)
        req = self.context.get('request')
        api_id = obj._meta.api_id if hasattr(obj._meta, 'api_id') else f'{obj._meta.model_name}s'
        attributes = dict()
        relationships = dict()

        for (key, field) in self.fields.items():
            # Skip the ID as it's stored at the root of the document
            if key == 'id':
                continue
            if type(field) is PrimaryKeyRelatedField:
                value = rep[key]

                if value is None:
                    relationships[key] = None
                else:
                    field_meta = field.queryset.model._meta
                    rel_api_id = field_meta.api_id if hasattr(field_meta, 'api_id') else f'{field_meta.model_name}s'
                    relationships[key] = {
                        'data': {
                            'id': value,
                            'type': rel_api_id
                        }
                    }
            else:
                attributes[key] = rep[key]

        return {
            'type': api_id,
            'id': obj.id,
            'attributes': attributes,
            'relationships': relationships,
            'links': {
                'self': f'{req.scheme}://{req.META["HTTP_HOST"]}/{api_id}/{obj.id}'
            }
        }

    def to_internal_value(self, data):
        data = data.get('data')

        if not data:
            raise serializers.ValidationError({'data': 'No root data property found.'})

        if not data.get('type'):
            raise serializers.ValidationError(
                {'data.type': 'No type found. Make sure to include the type of the document.'})

        attributes = data.get('attributes', {})
        relationships = {k: v['data']['id'] for k, v in data.get('relationships', {}).items()}

        return super().to_internal_value({**attributes, **relationships})
