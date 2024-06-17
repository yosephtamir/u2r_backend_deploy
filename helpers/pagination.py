
from typing import Any
from rest_framework import pagination, response



class PaginatorGenerator:
    def __call__(self, _page_size:int, _paginator_class:Any=pagination.PageNumberPagination):
        
        class PaginatorClass(_paginator_class):
            page_size = _page_size

            def get_paginated_response(self, data):
                return response.Response({
                    'status_code': 200,
                    'message': 'Success',
                    'page_info': {
                        'count': self.page.paginator.count,
                        'next': self.get_next_link(),
                        'previous': self.get_previous_link(),
                    },
                    'data': data,
                    'status': 'success'
                })
        
        return PaginatorClass
