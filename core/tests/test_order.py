from django.utils import timezone
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib.auth.models import User
from http.cookies import SimpleCookie
from datetime import timedelta
import pytz
import json
from decimal import Decimal
from unittest import skip


from core.models import Order, Address, Transaction
from payments.models import PaymentMethod, PaymentPreference, Payment
from .utils import UserBaseTestCase, OrderBaseTestCase


class OrderSetAsPaidTestCase(UserBaseTestCase, OrderBaseTestCase):

    def setUp(self):

        super(OrderSetAsPaidTestCase, self).setUp()
        currency = self.RUB

        self.data = {
            'amount_cash': Decimal(30674.85),
            'amount_btc': Decimal(1.00),
            'currency': currency,
            'user': self.user,
            'admin_comment': 'test Order',
            'unique_reference': '12345'
        }
        self.order = Order(**self.data)
        self.order.save()

        self.url = reverse('core.payment_confirmation',
                           kwargs={'pk': self.order.pk})

    def test_cannot_set_as_paid_if_has_no_withdraw_address(self):
        response = self.client.post(self.url, {'paid': 'true'})
        self.assertEqual(403, response.status_code)

        self.assertEquals(
            response.content,
            b'An order can not be set as paid without a withdraw address')

    def test_can_set_as_paid_if_has_withdraw_address(self):
        # Creates an withdraw address fro this user
        address = Address(
            user=self.user, type='W',
            address='17NdbrSGoUotzeGCcMMCqnFkEvLymoou9j')
        address.save()

        # Creates an Transaction for the Order, using the user Address
        transaction = Transaction(
            order=self.order, address_to=address, address_from=address)
        transaction.save()

        # Set Order as Paid
        response = self.client.post(self.url, {'paid': 'true'})
        expected = {"frozen": None, "paid": True, "status": "OK"}
        self.assertJSONEqual(json.dumps(expected), str(
            response.content, encoding='utf8'),)

    def test_can_set_as_paid_if_has_withdraw_address_internal(self):
        # Creates an withdraw address fro this user
        address = Address(
            user=self.user, type='W',
            address='17NdbrSGoUotzeGCcMMCqnFkEvLymoou9j')
        address.save()

        payment_method = PaymentMethod(
            name='Internal Test',
            is_internal=True
        )
        payment_method.save()

        pref = PaymentPreference(
            payment_method=payment_method,
            user=self.order.user,
            identifier='InternalTestIdentifier'
        )
        pref.save()

        payment = Payment(
            payment_preference=pref,
            amount_cash=self.order.amount_cash,
            order=self.order,
            currency=self.RUB,
            user=self.order.user
        )
        payment.save()
        # Creates an Transaction for the Order, using the user Address
        transaction = Transaction(
            order=self.order, address_to=address, address_from=address)
        transaction.save()

        # Set Order as Paid
        response = self.client.post(self.url, {'paid': 'true'})
        expected = {"frozen": True, "paid": True, "status": "OK"}
        self.assertJSONEqual(json.dumps(expected), str(
            response.content, encoding='utf8'),)


class OrderPayUntilTestCase(OrderBaseTestCase, UserBaseTestCase):

    def test_pay_until_message_is_in_context_and_is_rendered(self):
        response = self.client.post(
            reverse('core.order_add'),
            {
                'amount-cash': '31000',
                'currency_from': 'RUB',
                'amount-coin': '1',
                'currency_to': 'BTC',
                'user': self.user,
            }
        )

        order = Order.objects.last()
        pay_until = order.created_on + timedelta(minutes=order.payment_window)

        # Should be saved if HTTP200re
        self.assertEqual(200, response.status_code)

        # Does context contains the atribute, with correct value?
        self.assertEqual(pay_until, response.context['pay_until'])

        # Is rendere in template?
        self.assertContains(response, 'id="pay_until_notice"')

    def test_pay_until_message_is_in_correct_time_zone(self):
        user_tz = 'Asia/Vladivostok'
        self.client.cookies.update(SimpleCookie(
            {'USER_TZ': user_tz}))
        response = self.client.post(
            reverse('core.order_add'),
            {
                'amount-cash': '31000',
                'currency_from': 'RUB',
                'amount-coin': '1',
                'currency_to': 'BTC',
                'user': self.user,
            }
        )

        order = Order.objects.last()
        pay_until = order.created_on + timedelta(minutes=order.payment_window)

        # Should be saved if HTTP200re
        self.assertEqual(200, response.status_code)

        # Does context contains the atribute, with correct value?
        self.assertEqual(pay_until, response.context['pay_until'])

        # Is rendered in template?
        self.assertContains(response, 'id="pay_until_notice"')

        # Ensure template renders with localtime
        timezone.activate(pytz.timezone(user_tz))
        self.assertContains(
            response,
            timezone.localtime(pay_until).strftime("%H:%M%p (%Z)"))

    def test_pay_until_message_uses_settingsTZ_for_invalid_time_zones(self):
        user_tz = 'SOMETHING/FOOLISH'

        self.client.cookies.update(SimpleCookie(
            {'user_tz': user_tz}))
        response = self.client.post(reverse('core.order_add'), {
            'amount-cash': '31000',
            'currency_from': 'RUB',
            'amount-coin': '1',
            'currency_to': 'BTC'}
        )

        order = Order.objects.last()
        pay_until = order.created_on + timedelta(minutes=order.payment_window)

        # Should be saved if HTTP200re
        self.assertEqual(200, response.status_code)

        # Does context contains the atribute, with correct value?
        self.assertEqual(pay_until, response.context['pay_until'])

        # Is rendered in template?
        self.assertContains(response, 'id="pay_until_notice"')

        # Ensure template renders with the timezone defined as default
        timezone.activate(pytz.timezone(settings.TIME_ZONE))
        self.assertContains(response,
                            timezone.localtime(pay_until)
                            .strftime("%H:%M%p (%Z)"))


class UpdateWithdrawAddressTestCase(UserBaseTestCase, OrderBaseTestCase):

    def setUp(self):
        super(UpdateWithdrawAddressTestCase, self).setUp()

        PaymentMethod.objects.all().delete()

        method_data = {
            'bin': 426101,
            'fee': 0.0,
            'is_slow': 0,
            'name': 'Alpha Bank Visa'
        }
        payment_method = PaymentMethod(**method_data)
        payment_method.save()

        pref_data = {
            'user': self.user,
            'identifier': str(payment_method.bin),
            'comment': 'Just testing'
        }
        pref = PaymentPreference(**pref_data)
        pref.save()
        pref.currency.add(self.USD)
        pref.save()

        """Creates an order"""
        data = {
            'amount_cash': Decimal(30674.85),
            'amount_btc': Decimal(1.00),
            'currency': self.USD,
            'user': self.user,
            'admin_comment': 'test Order',
            'unique_reference': '12345',
            'payment_preference': pref
        }

        order = Order(**data)
        # TODO: patch and uncomment
        # order.full_clean()  # ensure is initially correct
        order.save()
        self.order = order

        pk = self.order.pk
        self.url = reverse('core.update_withdraw_address', kwargs={'pk': pk})

        self.addr_data = {
            'type': 'W',
            'name': '17NdbrSGoUotzeGCcMMCqnFkEvLymoou9j',
            'address': '17NdbrSGoUotzeGCcMMCqnFkEvLymoou9j',

        }
        self.addr = Address(**self.addr_data)
        self.addr.user = self.user
        self.addr.save()

        # The 'other' address for the Transaction
        user = User.objects.create_user(username='onit')
        addr2 = Address(**self.addr_data)
        addr2.user = user
        addr2.save()

    def test_forbiden_to_update_other_users_orders(self):
        username = '+555190909100'
        password = '321Changed'
        User.objects.create_user(username=username, password=password)

        client = self.client
        client.login(username=username, password=password)

        response = client.post(self.url, {
            'pk': self.order.pk,
            'value': self.addr.pk})

        self.assertEqual(403, response.status_code)

        self.client.login(username=self.user.username, password='password')

    def test_sucess_to_update_withdraw_adrress(self):

        response = self.client.post(self.url, {
            'pk': self.order.pk,
            'value': self.addr.pk, })

        self.assertJSONEqual('{"status": "OK"}', str(
            response.content, encoding='utf8'),)

        self.assertEqual(self.order.withdraw_address, self.addr.address)

    def test_throw_error_for_invalid_withdraw_adrress(self):
        response = self.client.post(
            self.url, {'pk': self.order.pk, 'value': 50})

        self.assertEqual(b'Invalid addresses informed.', response.content)


class OrderIndexOrderTestCase(UserBaseTestCase, OrderBaseTestCase):

    def setUp(self):
        super(OrderIndexOrderTestCase, self).setUp()

    def test_renders_empty_list_of_orders_for_anonymous(self):
        self.client.logout()
        with self.assertTemplateUsed('core/index_order.html'):
            response = self.client.get(reverse('core.order'))
            self.assertEqual(200, response.status_code)
            self.assertEqual(0, len(response.context['orders'].object_list))

        success = self.client.login(
            username=self.username, password=self.password)
        self.assertTrue(success)

    def test_renders_empty_list_of_user_orders(self):
        Order.objects.filter(user=self.user).delete()
        with self.assertTemplateUsed('core/index_order.html'):
            response = self.client.get(reverse('core.order'))
            self.assertEqual(200, response.status_code)
            self.assertEqual(0, len(response.context['orders'].object_list))

    @skip("causes failures, needs to be migrated")
    def test_renders_non_empty_list_of_user_orders(self):
        with self.assertTemplateUsed('core/index_order.html'):
            response = self.client.get(reverse('core.order'))
            self.assertEqual(200, response.status_code)
            self.assertEqual(1, len(response.context['orders'].object_list))

        Order.objects.filter(user=self.user).delete()

    @skip("causes failures, needs to be migrated")
    def test_filters_list_of_user_orders(self):
        date = timezone.now().strftime("%Y-%m-%d")
        response = self.client.post(reverse('core.order'), {'date': date})
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, len(response.context['orders'].object_list))

        date = (timezone.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        response = self.client.post(reverse('core.order'), {'date': date})
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.context['orders'].object_list))

        response = self.client.post(reverse('core.order'), {'date': None})
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, len(response.context['orders'].object_list))

        Order.objects.filter(user=self.user).delete()
