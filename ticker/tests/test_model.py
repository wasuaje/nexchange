from django.utils.dateformat import format
from django.test import TestCase
from ticker.models import Price
from decimal import Decimal


class PriceTestCase(TestCase):

    def setUp(self):
        self.price_usd = Decimal(650.88846)
        self.price_rub = Decimal(41758.2)
        self.data = {
            'better_adds_count': 1,
            'price_rub': self.price_rub,
            'price_usd': self.price_usd,
            'type': Price.BUY
        }

        self.price = Price(**self.data)
        self.price.save()

    def test_returns_unix_time(self):
        self.assertEqual(self.price.unix_time,
                         format(self.price.created_on, 'U'))

    def test_returns_price_in_usd(self):
        self.assertEqual(self.price.price_usd_formatted, self.price_usd)

    def test_returns_price_in_rub(self):
        self.assertEqual(self.price.price_rub_formatted, self.price_rub)
