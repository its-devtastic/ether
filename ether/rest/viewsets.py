from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed, ParseError
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .exceptions import Conflict
from .serializers import JsonApiV11ModelSerializer
from ..contenttypes import registry
from ..utils import log, get_api_id


class JsonApiModelViewSet(ModelViewSet):
    lookup_field = 'id'
    api_id = None

    def perform_create(self, serializer):
        # Check for valid type
        if self.request.data.get('data', {}).get('type') != self.api_id:
            raise Conflict(detail='Type does not match base name')
        return super().perform_create(serializer)

    def perform_update(self, serializer):
        # Check for valid type and ID
        data = self.request.data.get('data', {})
        if data.get('type') != self.api_id:
            raise Conflict(detail='Type does not match base name')
        if not data.get('id'):
            raise Conflict(detail='Resource does not include an ID')
        if data.get('id') != self.kwargs['id']:
            raise Conflict(detail='Resource ID does not match endpoint')

        return super().perform_update(serializer)

    def update(self, request, *args, **kwargs):
        #  Do not allow updates with PUT
        if self.action == 'update':
            raise MethodNotAllowed(method='PUT')

        return super().update(request, *args, **kwargs)

    @action(detail=True, methods=['patch', 'post', 'delete', 'get'],
            url_path='relationships/(?P<relation_field_name>[^/.]+)')
    def update_relationships(self, request, id=None, relation_field_name=None):
        """
        Implements relationship endpoints for one-to-many and many-to-many relationships.

        https://jsonapi.org/format/#crud-updating-relationships
        """
        resource = self.get_object()

        # Check if the field exists on the resource
        if not hasattr(resource, relation_field_name):
            raise ParseError('Relationship does not exist for this resource.')

        # Get the model field object of the related field
        relation_model_field = getattr(self.queryset.model, relation_field_name).field

        # Check if that field is a relation
        if not relation_model_field.is_relation:
            raise ParseError('Field is not a relation.')

        try:
            data = request.method != 'GET' and request.data['data']
        except KeyError:
            raise ParseError('Payload should include a data attribute.')

        # Get the relation manager
        relation_manager = getattr(resource, relation_field_name)

        api_id = get_api_id(relation_model_field.related_model)

        # Many to one (and one to many) fields only allow PATCH updates.
        if relation_model_field.many_to_one:
            if request.method == 'GET':
                return Response(data=relation_manager.id and {'id': relation_manager.id, 'type': api_id})
            if request.method in ['DELETE', 'POST']:
                raise MethodNotAllowed(method=request.method,
                                       detail='Method not allowed for one-to-many relationships.')

            # Check if payload has the correct data structure
            if data is None or type(data) is dict and data.get('id'):
                setattr(resource, f'{relation_field_name}_id', data and data.get('id'))
                resource.save()
            else:
                raise ParseError('Either provide a resource identifier object or null.')

        # Many to many fields allow PATCH, POST and DELETE updates.
        if relation_model_field.many_to_many:
            # Return the relationship objects for a GET request
            if request.method == 'GET':
                return Response(data=[{'id': item.id, 'type': api_id} for item in relation_manager.all()])
            # Check if payload has the correct data structure
            if type(data) is not list:
                raise ParseError('Provide a list of resource identifier objects.')

            # Get the content type instance of the related model
            content_type = registry.get(api_id)

            # If it doesn't exist we will use a default model serializer
            if not content_type:
                log(':warning:',
                    f'[orange]The model for the relationship [bold]{relation_field_name}[/bold] on [bold]{resource._meta.api_id}[/bold] is not registered as a content type. A default model serializer will be used but this might not be what you want.[/orange]',
                    )

                class DefaultSerializer(JsonApiV11ModelSerializer):
                    class Meta:
                        model = relation_model_field.related_model
                        fields = '__all__'

                serializer_class = DefaultSerializer
            else:
                serializer_class = content_type.serializer_class

            if request.method == 'PATCH':
                serializer = serializer_class(data=data, many=True)
                serializer.is_valid(raise_exception=True)

                relation_manager.set(serializer.validated_data)

            if request.method == 'POST':
                for item in data:
                    if item.get('id'):
                        relation_manager.add(item['id'])
                    else:
                        serializer = serializer_class(data=item)
                        serializer.is_valid(raise_exception=True)
                        relation_manager.create(**serializer.validated_data)

            if request == 'DELETE':
                for item in data:
                    if item.get('id'):
                        relation_manager.remove(item['id'])

        return Response(data=self.serializer_class(resource, context={'request': request}).data)
