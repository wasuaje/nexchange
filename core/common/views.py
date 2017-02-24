import datetime
from rest_framework import generics, viewsets


class DateFilterViewSet(viewsets.ViewSetMixin, generics.ListAPIView):

    def __init__(self, *args, **kwargs):
        self.queryset = None
        super(DateFilterViewSet, self).__init__(*args, **kwargs)

    def get_queryset(self):
        filters = {}
        params = self.request.query_params

        if 'hours' in params:
            hours = self.request.query_params.get('hours')
            seconds = float(hours) * 3600
            relevant = datetime.datetime.now() - \
                datetime.timedelta(seconds=seconds)
            filters['created_on__gte'] = relevant
        elif 'date' in params:
            # Todo: Add this functionality
            # Todo: Add start and end func
            raise NotImplementedError()
        return self.queryset.filter(**filters).order_by('id')
