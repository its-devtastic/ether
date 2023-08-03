from rest_framework import pagination
from rest_framework.response import Response
from rest_framework.utils.urls import replace_query_param


class PageNumberPagination(pagination.PageNumberPagination):
    page_size_query_param = 'page[limit]'
    page_query_param = 'page[current]'

    def get_paginated_response(self, data):
        absolute_uri = self.request.build_absolute_uri()
        return Response({
            'links': {
                'self': absolute_uri,
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
                'first': replace_query_param(absolute_uri, self.page_query_param, 1),
                'last': replace_query_param(absolute_uri, self.page_query_param, self.page.paginator.num_pages),
            },
            'data': data
        })
