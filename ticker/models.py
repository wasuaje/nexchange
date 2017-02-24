from django.db import models
from django.utils.dateformat import format
from core.common.models import TimeStampedModel
import requests
from decimal import Decimal


class Price(TimeStampedModel):
    EUR_RESOURCE = 'http://api.fixer.io/latest?symbols=USD'
    EUR_USD = None
    BUY = 'B'
    SELL = 'S'
    BUY_SELL_CHOICES = (
        (BUY, 'BUY'),
        (SELL, 'SELL')
    )

    type = models.CharField(max_length=1, choices=BUY_SELL_CHOICES)
    price_rub = models.DecimalField(max_digits=12, decimal_places=2)
    price_usd = models.DecimalField(max_digits=12, decimal_places=2)
    price_eur = models.DecimalField(max_digits=12, decimal_places=2)
    rate_usd = models.DecimalField(max_digits=12, decimal_places=2)
    rate_eur = models.DecimalField(max_digits=12, decimal_places=2)
    better_adds_count = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.rate_usd:
            self.rate_usd = Decimal(self.price_rub / self.price_usd)
        self.get_eur_rate()
        self.price_eur = Decimal(self.price_rub / self.rate_eur)
        super(Price, self).save(*args, **kwargs)

    def get_eur_rate(self):
        rate_info = requests.get(Price.EUR_RESOURCE).json()
        self.rate_eur = Decimal(rate_info['rates']['USD']) * self.rate_usd

    # TODO: remove formatted suffix from frontend
    @property
    def rate_eur_usd(self):
        return self.rate_eur / self.rate_usd

    @property
    def unix_time(self):
        return format(self.created_on, 'U')

    @property
    def price_eur_formatted(self):
        return self.price_eur

    @property
    def price_usd_formatted(self):
        return self.price_usd

    @property
    def price_rub_formatted(self):
        return self.price_rub
