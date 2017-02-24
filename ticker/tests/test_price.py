from django.test import TestCase
import requests
import requests_mock
from ticker.models import Price
from unittest.mock import MagicMock
from decimal import Decimal
from core.utils import money_format


class TestPrice(TestCase):
    TWO_PLACES = Decimal(10) ** -2

    def setUp(self):
        self.adapter = requests_mock.Adapter()
        self.session = requests.session()
        self.session.mount('mock', self.adapter)

    # This test is FAILING I'm not sure about the formula here.
    # TODO: Fix this test
    def test_eur_price(self):
        test_eur_usd = Decimal(1.5)
        test_usd_price = Decimal(600.00)
        test_rub_price = Decimal(40000.00)

        ret = MagicMock(return_value={'rates': {'USD': test_eur_usd}})
        self.adapter.register_uri('GET', Price.EUR_RESOURCE, ret)

        p = Price(price_usd=test_usd_price, price_rub=test_rub_price)
        p.save()

        # TODO: enhance test
        self.assertEqual(money_format(p.rate_eur),
                         money_format(p.price_rub /
                                      p.price_eur))

    def test_usd_price(self):
        test_usd_rub = Decimal(60.00)
        test_rub_price = Decimal(40000.00)
        test_usd_price = test_rub_price / test_usd_rub

        p = Price(price_usd=test_usd_price, price_rub=test_rub_price)
        p.save()

        self.assertEqual(p.rate_usd, test_usd_rub)
