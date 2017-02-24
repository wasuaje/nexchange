from django.test import TestCase
from django.utils import timezone
from django.conf import settings

from unittest.mock import Mock, MagicMock

from core.middleware import TimezoneMiddleware
from .utils import data_provider


class TimezoneMiddlewareTestCase(TestCase):

    def setUp(self):
        self.middleware = TimezoneMiddleware()
        self.request = Mock()
        self.request.COOKIES = {}

    def test_process_request_without_tz_cookie(self):
        self.middleware.process_request(self.request)

        active_tz = timezone.get_current_timezone_name()

        self.assertEqual(active_tz, settings.TIME_ZONE)

    def test_process_request_with_tz_cookie(self):
        user_tz = 'Asia/Vladivostok'
        self.request.COOKIES = {'USER_TZ': user_tz}

        self.middleware.process_request(self.request)

        active_tz = timezone.get_current_timezone_name()
        self.assertEqual(active_tz, user_tz)

    def test_uses_settings_tz_for_invalid_cookie(self):
        # ensure starts with one that is not the one in settings.py
        initial_tz = 'Asia/Vladivostok'
        self.assertNotEqual(settings.TIME_ZONE, initial_tz)
        timezone.activate(initial_tz)

        # set a invalid TZ via cookie
        user_tz = 'Wonder/Land'
        self.request.COOKIES = {'USER_TZ': user_tz}
        self.middleware.process_request(self.request)

        active_tz = timezone.get_current_timezone_name()
        self.assertEqual(settings.TIME_ZONE, active_tz)


class DataProviderDecoratorTestCase(TestCase):

    def test_calls_fn_data_provider(self):
        func_that_provides_data = MagicMock(return_value='x')
        func_that_is_decorated = MagicMock()

        decorator = data_provider(func_that_provides_data)
        decorated = decorator(func_that_is_decorated)
        decorated(None)

        self.assertTrue(func_that_provides_data.called)

    def test_calls_decorated_func_with_data_provided(self):
        param = '123'
        expected_calls = [((None, '1'),), ((None, '2'),), ((None, '3'),)]

        func_that_provides_data = MagicMock(return_value=param)
        func_that_is_decorated = MagicMock()

        decorator = data_provider(func_that_provides_data)
        decorated = decorator(func_that_is_decorated)

        decorated(None)

        self.assertEqual(func_that_is_decorated.call_count, 3)
        self.assertEqual(func_that_is_decorated.call_args_list, expected_calls)

    def test_catches_assertionError_on_decorated(self):

        func_that_provides_data = MagicMock(return_value='1')
        func_that_is_decorated = MagicMock(
            side_effect=AssertionError('Boom!'))

        decorator = data_provider(func_that_provides_data)
        decorated = decorator(func_that_is_decorated)

        with self.assertRaises(AssertionError):
            decorated(None)
