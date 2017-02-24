from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils.translation import activate

from core.models import SmsToken, Currency, Price, Order
from payments.models import PaymentMethod, PaymentPreference
from decimal import Decimal


def data_provider(fn_data_provider):
    """
    Data provider decorator
    allows another callable to provide the data for the test
    """
    def test_decorator(fn):
        def repl(self):
            for i in fn_data_provider():
                try:
                    fn(self, *i)
                except AssertionError as e:
                    print("Assertion error caught with data set ", i)
                    raise e
        return repl
    return test_decorator


class UserBaseTestCase(TestCase):

    def setUp(self):
        self.username = '+555190909898'
        self.password = '123Mudar'
        self.data = \
            {
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'johndoe@domain.com',
            }

        activate('en')

        self.user, created = User.objects.get_or_create(username=self.username)
        self.user.set_password(self.password)
        self.user.save()
        assert isinstance(self.user, User)
        token = SmsToken(user=self.user)
        token.save()
        self.client = Client()
        success = self.client.login(username=self.username,
                                    password=self.password)
        assert success
        super(UserBaseTestCase, self).setUpClass()


class OrderBaseTestCase(TestCase):
    PRICE_BUY_RUB = 36000
    PRICE_BUY_USD = 600

    PRICE_SELL_RUB = 30000
    PRICE_SELL_USD = 500

    RATE_EUR = 70.00

    @classmethod
    def setUpClass(cls):
        cls.RUB = Currency(code='RUB', name='Rubles')
        cls.RUB.save()

        cls.USD = Currency(code='USD', name='US Dollars')
        cls.USD.save()

        cls.EUR = Currency(code='EUR', name='EURO')
        cls.EUR.save()

        cls.ticker_buy = \
            Price(type=Price.BUY,
                  price_rub=OrderBaseTestCase.PRICE_BUY_RUB,
                  price_usd=OrderBaseTestCase.PRICE_BUY_USD,
                  rate_eur=Decimal(OrderBaseTestCase.RATE_EUR))

        cls.ticker_buy.save()

        cls.ticker_sell = \
            Price(type=Price.SELL,
                  price_rub=OrderBaseTestCase.PRICE_SELL_RUB,
                  price_usd=OrderBaseTestCase.PRICE_SELL_USD,
                  rate_eur=Decimal(OrderBaseTestCase.RATE_EUR))

        cls.ticker_sell.save()
        super(OrderBaseTestCase, cls).setUpClass()

    @classmethod
    def create_order(cls, user):
        cls.setUpClass()

        payment_method = PaymentMethod.objects.first()

        if payment_method is None:
            method_data = {
                'bin': 426101,
                'fee': 0.0,
                'is_slow': 0,
                'name': 'Alpha Bank Visa'
            }
            payment_method = PaymentMethod(**method_data)
            payment_method.save()

        pref_data = {
            'user': user,
            'currency': cls.USD,
            'identifier': str(payment_method.bin),
            'comment': 'Just testing'
        }
        pref = PaymentPreference(**pref_data)
        pref.save()

        """Creates an order"""
        data = {
            'amount_cash': Decimal(30674.85),
            'amount_btc': Decimal(1.00),
            'currency': cls.USD,
            'user': user,
            'admin_comment': 'test Order',
            'unique_reference': '12345',
            'withdraw_address': '17NdbrSGoUotzeGCcMMCqnFkEvLymoou9j',
            'payment_preference': pref
        }

        order = Order(**data)
        order.full_clean()  # ensure is initially correct
        order.save()

        return order
