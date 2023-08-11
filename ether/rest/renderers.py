from djangorestframework_camel_case.render import CamelCaseJSONRenderer


class JsonApiV11Renderer(CamelCaseJSONRenderer):
    """
    JSON:API v1.1 compliant renderer.
    See https://jsonapi.org
    """
    media_type = 'application/vnd.api+json'
    format = 'json'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        req = renderer_context['request']
        res = renderer_context['response']
        view = renderer_context['view']
        is_paginated = view.pagination_class is not None
        is_exception = res.exception

        # Current view action: either retrieve, create, update, list or delete
        action = renderer_context['view'].action

        result = {}

        if is_exception:
            result = data
        else:
            # Paginated responses are already properly formatted by the pagination class
            if action == 'list' and is_paginated:
                result = data

            # Handle non-paginated lists
            if action == 'list' and not is_paginated:
                result['data'] = data
                result['links'] = {
                    'self': req.build_absolute_uri()
                }

            # Handle single documents
            if action in ['retrieve', 'create', 'update']:
                result['data'] = data

            # Handle document creation
            if action == 'create':
                res.headers['Location'] = data['links']['self']

        return super().render(result, accepted_media_type, renderer_context)
