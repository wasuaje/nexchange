from django.db import models
from django.contrib.auth.models import User
from nexchange.settings import REFERRAL_CODE_LENGTH
from decimal import Decimal
from django.utils.crypto import get_random_string
from core.common.models import SoftDeleteMixin, UniqueFieldMixin,\
    TimeStampedModel


class Program(TimeStampedModel):
    name = models.CharField(max_length=255)
    percent_first_degree = models.FloatField()
    percent_second_degree = models.FloatField(default=0)
    percent_third_degree = models.FloatField(default=0)
    currency = models.ManyToManyField('core.Currency')
    max_payout_btc = models.FloatField(default=-1)
    max_users = models.IntegerField(default=-1)
    max_lifespan = models.IntegerField(default=-1)
    is_default = models.BooleanField(default=False)


class ReferralCode(TimeStampedModel, UniqueFieldMixin):
    code = models.CharField(max_length=10, unique=True)
    user = models.ForeignKey(User, related_name='referral_code')
    program = models.ForeignKey(Program, blank=True,
                                null=True, default=None)

    def save(self, *args, **kwargs):
        self.code = self.gen_unique_value(
            lambda x: get_random_string(x),
            lambda x: ReferralCode.objects.filter(code=x).count(),
            REFERRAL_CODE_LENGTH
        )

        super(ReferralCode, self).save(*args, **kwargs)


class Referral(TimeStampedModel, SoftDeleteMixin):
    code = models.ForeignKey('ReferralCode', default=None,
                             null=True)
    referee = models.ForeignKey(User, null=True, default=None,
                                related_name='referral')

    def save(self, *args, **kwargs):
        if 'program' not in kwargs:
            kwargs['program'] = Program.objects.first()

        super(Referral, self).save(*args, **kwargs)

    @property
    def orders(self):
        return self.referee. \
            orders.filter(is_completed=True)

    @property
    def confirmed_orders_count(self):
        return self.orders.count()

    @property
    def turnover(self):
        res = self.\
            orders.aggregate(models.Sum('amount_btc'))
        return res['amount_btc__sum']

    @property
    def program(self):
        return self.referrer.user. \
            referral_code.get(). \
            program

    @property
    def revenue(self,):
        # TODO: implement program and change to dynamic
        return Decimal(self.turnover) / 100 * \
            self.program.percent_first_degree
