from rest_framework.pagination import PageNumberPagination

class StandardSlotResultsPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'slots_size'
    max_page_size = 30

    