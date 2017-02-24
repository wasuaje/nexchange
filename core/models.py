from django.db import models
from core.common.models import TimeStampedModel, \
    SoftDeletableModel, Currency, UniqueFieldMixin

from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField
from ticker.models import Price
from referrals.models import ReferralCode
from .validators import validate_bc
from django.conf import settings

from django.utils.translation import ugettext_lazy as _

from core.common.models import Balance
from core.utils import money_format
from django.utils.crypto import get_random_string
from datetime import timedelta
from django.utils import timezone
from decimal import Decimal


class ProfileManager(models.Manager):

    def get_by_natural_key(self, username):
        return self.get(user__username=username)


class Profile(TimeStampedModel, SoftDeletableModel):
    objects = ProfileManager()

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = PhoneNumberField(_('Phone'), blank=False, help_text=_(
        'Enter phone number in international format. eg. +555198786543'))
    first_name = models.CharField(max_length=20, blank=True)
    last_name = models.CharField(max_length=20, blank=True)
    last_visit_ip = models.CharField(max_length=39,
                                     default=None, null=True)
    last_visit_time = models.DateTimeField(default=None, null=True)
    notify_by_phone = models.BooleanField(default=True)
    notify_by_email = models.BooleanField(default=True)
    ip = models.CharField(max_length=39,
                          null=True,
                          default=None)
    sig_key = models.CharField(max_length=64, blank=True)

    @property
    def partial_phone(self):
        phone = str(self.phone)
        phone_len = len(phone)
        start = phone[:settings.PHONE_START_SHOW - 1]
        end = phone[phone_len - 1 - settings.PHONE_END_SHOW:]
        rest = \
            ''.join([settings.PHONE_HIDE_PLACEHOLDER
                     for x in
                     range(phone_len - settings.PHONE_START_SHOW -
                           settings.PHONE_END_SHOW)])
        return "{}{}{}".format(start, rest, end)

    @property
    def is_banned(self):
        return \
            Order.objects.filter(user=self,
                                 is_paid=True,
                                 expired=True).length \
            > settings.MAX_EXPIRED_ORDERS_LIMIT

    def natural_key(self):
        return self.user.username

    def save(self, *args, **kwargs):
        """Add a SMS token at creation. Used to verify phone number"""
        if self.pk is None:
            token = SmsToken(user=self.user)
            token.save()
        if not self.phone:
            self.phone = self.user.username

        # TODO: move to user class, allow many(?)
        ReferralCode.objects.get_or_create(user=self.user)

        return super(Profile, self).save(*args, **kwargs)


User.profile = property(lambda u:
                        Profile.objects.
                        get_or_create(user=u)[0])


class SmsToken(TimeStampedModel, SoftDeletableModel, UniqueFieldMixin):
    sms_token = models.CharField(
        max_length=settings.SMS_TOKEN_LENGTH, blank=True)
    user = models.ForeignKey(User, related_name='sms_token')

    @staticmethod
    def get_sms_token():
        return User.objects.make_random_password(
            length=settings.SMS_TOKEN_LENGTH,
            allowed_chars=settings.SMS_TOKEN_CHARS
        )

    @property
    def valid(self):
        return self.created_on > timezone.now() -\
            timedelta(minutes=settings.SMS_TOKEN_VALIDITY)

    def save(self, *args, **kwargs):
        self.sms_token = self.get_sms_token()
        super(SmsToken, self).save(*args, **kwargs)

    def __str__(self):
        return "{} ({})".format(self.sms_token, self.user.profile.phone)


class BtcBase(TimeStampedModel):

    class Meta:
        abstract = True

    WITHDRAW = 'W'
    DEPOSIT = 'D'
    TYPES = (
        (WITHDRAW, 'WITHDRAW'),
        (DEPOSIT, 'DEPOSIT'),
    )
    type = models.CharField(max_length=1, choices=TYPES)


class Address(BtcBase, SoftDeletableModel):
    WITHDRAW = 'W'
    DEPOSIT = 'D'
    TYPES = (
        (WITHDRAW, 'WITHDRAW'),
        (DEPOSIT, 'DEPOSIT'),
    )
    name = models.CharField(max_length=100, blank=True)
    address = models.CharField(max_length=35, validators=[validate_bc])
    user = models.ForeignKey(User)
    order = models.ForeignKey('core.Order', null=True, default=None)


class Transaction(BtcBase):
    # null if withdraw from our balance on Kraken
    confirmations = models.IntegerField(default=0)
    tx_id = models.CharField(max_length=55, default=None, null=True)
    address_from = models.ForeignKey(
        'core.Address',
        related_name='address_from',
        default=None,
        null=True)
    address_to = models.ForeignKey('core.Address', related_name='address_to')
    # TODO: how to handle cancellation?
    order = models.ForeignKey('core.Order')
    is_verified = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)


class ReferralTransaction(Transaction):
    pass


class CmsPage(models.Model):
    allcms = [a for a in settings.CMSPAGES.values()]
    allcms = allcms[0] + allcms[1]

    t_footers = [(a[0], a[0]) for a in allcms]

    TYPES = (
        t_footers
    )

    name = models.CharField(default=None, max_length=50, choices=TYPES)
    head = models.TextField(default=None, null=True)
    written_by = models.TextField(default=None, null=True)
    body = models.TextField(default=None, null=True)
    locale = models.CharField(default=settings.LANGUAGES[0],
                              max_length=2,
                              null=True, choices=settings.LANGUAGES)


class Order(TimeStampedModel, SoftDeletableModel, UniqueFieldMixin):
    USD = "USD"
    RUB = "RUB"
    EUR = "EUR"

    BUY = 1
    SELL = 0
    TYPES = (
        (SELL, 'SELL'),
        (BUY, 'BUY'),
    )

    # Todo: inherit from BTC base?, move lengths to settings?
    order_type = models.IntegerField(choices=TYPES, default=BUY)
    amount_cash = models.DecimalField(max_digits=12, decimal_places=2)
    amount_btc = models.DecimalField(max_digits=18, decimal_places=8)
    currency = models.ForeignKey(Currency)
    payment_window = models.IntegerField(default=settings.PAYMENT_WINDOW)
    user = models.ForeignKey(User, related_name='orders')
    is_paid = models.BooleanField(default=False)
    is_released = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)
    is_failed = models.BooleanField(default=False)
    unique_reference = models.CharField(
        max_length=settings.UNIQUE_REFERENCE_LENGTH, unique=True)
    admin_comment = models.CharField(max_length=200)
    payment_preference = models.ForeignKey('payments.PaymentPreference',
                                           default=None,
                                           null=True)

    class Meta:
        ordering = ['-created_on']

    def save(self, *args, **kwargs):
        old_referral_revenue = None

        self.unique_reference = \
            self.gen_unique_value(
                lambda x: get_random_string(x),
                lambda x: Order.objects.filter(unique_reference=x).count(),
                settings.UNIQUE_REFERENCE_LENGTH
            )
        self.convert_coin_to_cash()

        if 'is_completed' in kwargs and\
                kwargs['is_completed'] and\
                not self.is_completed:
            old_referral_revenue = self.user.referral.get().revenue

        super(Order, self).save(*args, **kwargs)
        if len(self.user.referral.all()):
            # TODO: Add referralTransaction
            new_referral_revenue = self.user.referral.get().revenue
            revenue_from_trade = \
                new_referral_revenue - old_referral_revenue

            balance, created = \
                Balance.objects.get(user=self.user, currency=self.currency)
            balance.balance += revenue_from_trade
            balance.save()

    def convert_coin_to_cash(self):
        self.amount_btc = Decimal(self.amount_btc)
        queryset = Price.objects.filter().order_by('-id')[:2]
        price_sell = [price for price in queryset if price.type == Price.SELL]
        price_buy = [price for price in queryset if price.type == Price.BUY]

        # Below calculation affect real money the client pays
        assert all([len(price_sell),
                    price_sell[0].price_usd,
                    price_buy[0].price_rub,
                    price_buy[0].price_eur])

        assert all([len(price_buy),
                    price_buy[0].price_usd,
                    price_buy[0].price_rub,
                    price_buy[0].price_eur])

        # TODO: Make this logic more generic,
        # TODO: migrate to using currency through payment_preference

        # SELL
        self.amount_cash = Decimal(self.amount_btc)

        if self.order_type == Order.SELL and self.currency.code == Order.USD:
            self.amount_cash *= price_buy[0].price_usd

        elif self.order_type == Order.SELL and self.currency.code == Order.RUB:
            self.amount_cash *= price_buy[0].price_rub

        elif self.order_type == Order.SELL and self.currency.code == Order.EUR:
            self.amount_cash *= price_buy[0].price_eur

        # BUY
        if self.order_type == Order.BUY and self.currency.code == Order.USD:
            self.amount_cash *= price_sell[0].price_usd

        elif self.order_type == Order.BUY and self.currency.code == Order.RUB:
            self.amount_cash *= price_sell[0].price_rub

        elif self.order_type == Order.BUY and self.currency.code == Order.EUR:
            self.amount_cash *= price_sell[0].price_eur

        self.amount_cash = money_format(self.amount_cash)

    @property
    def payment_deadline(self):
        """returns datetime of payment_deadline (creation + payment_window)"""
        # TODO: Use this for pay until message on 'order success' screen
        return self.created_on + timedelta(minutes=self.payment_window)

    @property
    def expired(self):
        """Is expired if payment_deadline is exceeded and it's not paid yet"""
        # TODO: validate this business rule
        # TODO: Refactor, it is unreasonable to have different standards of
        # time in the DB
        return (timezone.now() > self.payment_deadline) and\
               (not self.is_paid) and not self.is_released

    @property
    def payment_status_frozen(self):
        """return a boolean indicating if order can be updated
        Order is frozen if it is expired or has been paid
        """
        # TODO: validate this business rule
        return self.expired or \
            (self.is_paid and
             self.payment_set.last() and
             self.payment_set.last().
             payment_preference.
             payment_method.is_internal)

    @property
    def withdrawal_address_frozen(self):
        """return bool whether the withdraw address can
           be changed"""
        return self.is_released

    @property
    def has_withdraw_address(self):
        """return a boolean indicating if order has a withdraw adrress defined
        """
        # TODO: Validate this business rule
        return len(self.transaction_set.all()) > 0

    @property
    def withdraw_address(self):
        addr = None

        if self.has_withdraw_address:
            addr = self.transaction_set.first().address_to.address

        return addr

    def __str__(self):
        return "{} {} {} BTC {} {}".format(self.user.username or
                                           self.user.profile.phone,
                                           self.order_type,
                                           self.amount_btc,
                                           self.amount_cash,
                                           self.currency)
