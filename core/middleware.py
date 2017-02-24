import pytz

from django.conf import settings
# from datetime import datetime
from django.utils import timezone


class TimezoneMiddleware(object):

    def process_request(self, request):
        # TODO implement logout if TZ changes during session
        tzname = request.COOKIES.get('USER_TZ', settings.TIME_ZONE)
        try:
            timezone.activate(pytz.timezone(tzname))
        except Exception:
            timezone.deactivate()


class LastSeenMiddleware(object):

    def process_response(self, request, response):
        pass
