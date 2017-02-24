from payments.models import Payment, PaymentMethod, PaymentPreference
from core.models import Order, Address, Transaction
from .utils import UserBaseTestCase, OrderBaseTestCase
from nexchange.utils import release_payment, check_transaction
from decimal import Decimal
from unittest import skip


class RoboTestCase(UserBaseTestCase):

    def setUp(self):
        super(RoboTestCase, self).setUp()

    @skip("causes failures, needs to be migrated")
    def test_bad_paysuccess(self):
        r = self.client.post('/en/paysuccess/robokassa')
        self.assertEqual(r.json()['result'], 'bad request')

    @skip("causes failures, needs to be migrated")
    def test_bad_paysuccess_with_param(self):
        r = self.client.post('/en/paysuccess/robokassa',
                             {'OutSum': 1,
                              'InvId': 1,
                              'SignatureValue': 'fsdfdfdsd'})
        self.assertEqual(r.json()['result'], 'bad request')


class PaymentReleaseTestCase(UserBaseTestCase, OrderBaseTestCase):

    def setUp(self):
        super(PaymentReleaseTestCase, self).setUp()
        self.method_data = {
            "is_internal": 1,
            'name': 'Robokassa'
        }

        amount_cash = Decimal(30000.00)

        self.payment_method = PaymentMethod(name='ROBO')
        self.payment_method.save()

        self.addr_data = {
            'type': 'W',
            'name': '17NdbrSGoUotzeGCcMMCqnFkEvLymoou9j',
            'address': '17NdbrSGoUotzeGCcMMCqnFkEvLymoou9j',

        }

        self.addr = Address(**self.addr_data)
        self.addr.user = self.user
        self.addr.save()

        pref_data = {
            'user': self.user,
            'comment': 'Just testing',
            'payment_method': self.payment_method
        }

        pref = PaymentPreference(**pref_data)
        pref.save('internal')

        self.data = {
            'amount_cash': amount_cash,
            'amount_btc': Decimal(1.00),
            'currency': self.RUB,
            'user': self.user,
            'admin_comment': 'test Order',
            'unique_reference': '12345',
            'payment_preference': pref,
            'is_paid': True
        }

        self.order = Order(**self.data)
        self.order.save()

        self.pay_data = {
            'amount_cash': self.order.amount_cash,
            'currency': self.RUB,
            'user': self.user,
            'payment_preference': pref,
        }

        self.payment = Payment(**self.pay_data)
        self.payment.save()

        tx_id_ = '76aa6bdc27e0bb718806c93db66525436' \
                 'fa621766b52bad831942dee8b618678'

        self.transaction = Transaction(tx_id=tx_id_,
                                       order=self.order, address_to=self.addr)
        self.transaction.save()

    def test_bad_release_payment(self):
        for o in Order.objects.filter(is_paid=True, is_released=False):
            p = Payment.objects.filter(user=o.user,
                                       amount_cash=o.amount_cash,
                                       payment_preference=o.payment_preference,
                                       is_complete=False,
                                       currency=o.currency).first()
            if p is not None:
                tx_id_ = release_payment(o.withdraw_address,
                                         o.amount_btc)
                self.assertEqual(tx_id_, None)

    def test_orders_with_approved_payments(self):

        for o in Order.objects.filter(is_paid=True, is_released=False):

            p = Payment.objects.filter(user=o.user,
                                       amount_cash=o.amount_cash,
                                       payment_preference=o.payment_preference,
                                       is_complete=False,
                                       currency=o.currency).first()

            if p is not None:

                o.is_released = True
                o.save()

                p.is_complete = True
                p.save()

            self.assertTrue(o.is_released)
            self.assertTrue(p.is_complete)

    def checker_transactions(self):
        if check_transaction(self.transaction.tx_id):
            self.transaction.is_completed = True
            self.transaction.save()
        self.assertTrue(self.transaction.is_completed)
