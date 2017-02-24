from django.db import models

from core.common.models import TimeStampedModel, SoftDeletableModel
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _


class PaymentMethodManager(models.Manager):
    def get_by_natural_key(self, bin_code):
        return self.get(bin=bin_code)


class PaymentMethod(TimeStampedModel, SoftDeletableModel):
    BIN_LENGTH = 6
    objects = PaymentMethodManager()
    name = models.CharField(max_length=100)
    handler = models.CharField(max_length=100, null=True)
    bin = models.IntegerField(null=True, default=None)
    fee = models.FloatField(null=True)
    is_slow = models.BooleanField(default=False)
    is_internal = models.BooleanField(default=False)

    def natural_key(self):
        return self.bin

    def __str__(self):
        return "{} ({})".format(self.name, self.bin)


class PaymentPreference(TimeStampedModel, SoftDeletableModel):
    # NULL or Admin for out own (buy adds)
    enabled = models.BooleanField(default=True)
    user = models.ForeignKey(User)
    payment_method = models.ForeignKey('PaymentMethod', default=None)
    currency = models.ManyToManyField('core.Currency')
    # Optional, sometimes we need this to confirm
    identifier = models.CharField(max_length=100)
    comment = models.CharField(max_length=255, default=None,
                               blank=True, null=True)
    sub_type = models.CharField(max_length=100, null=True,
                                blank=True, default=None)
    main_type = models.CharField(max_length=100, null=True,
                                 blank=True, default=None)

    def save(self, *args, **kwargs):
        if not hasattr(self, 'payment_method'):
            self.payment_method = self.guess_payment_method()
        super(PaymentPreference, self).save(*args, **kwargs)

    def guess_payment_method(self):
        card_bin = self.identifier[:PaymentMethod.BIN_LENGTH]
        payment_method = []
        while all([self.identifier,
                   not len(payment_method),
                   len(card_bin) > 0]):
            payment_method = PaymentMethod.objects.filter(bin=card_bin)
            card_bin = card_bin[:-1]

        return payment_method[0] if len(payment_method) \
            else PaymentMethod.objects.get(name='Cash')

    def __str__(self):
        return "{} - {} - ({})".format(self.user.profile.phone or
                                       self.user.username,
                                       self.identifier,
                                       self.payment_method.name)


class Payment(TimeStampedModel, SoftDeletableModel):
    nonce = models.CharField(_('Nonce'),
                             max_length=256,
                             null=True,
                             blank=True)
    amount_cash = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.ForeignKey('core.Currency')
    is_redeemed = models.BooleanField(default=False)
    is_complete = models.BooleanField(default=False)
    is_success = models.BooleanField(default=False)
    payment_preference = models.ForeignKey('PaymentPreference',
                                           null=False, default=None)
    # Super admin if we are paying for BTC
    user = models.ForeignKey(User)
    # Todo consider one to many for split payments, consider order field on
    # payment
    order = models.ForeignKey('core.Order', null=True, default=None)
    reference = models.CharField(max_length=255,
                                 null=True, default=None)


class PaymentCredentials(TimeStampedModel, SoftDeletableModel):
    payment_preference = models.ForeignKey('PaymentPreference')
    uni = models.CharField(_('Uni'), max_length=60,
                           null=True, blank=True)
    nonce = models.CharField(_('Nonce'), max_length=256,
                             null=True, blank=True)
    token = models.CharField(_('Token'), max_length=256,
                             null=True, blank=True)
    is_default = models.BooleanField(_('Default'), default=False)
    is_delete = models.BooleanField(_('Delete'), default=False)

    def __str__(self):
        pref = self.paymentpreference_set.get()
        return "{0} - ({1})".format(pref.user.username,
                                    pref.identifier)
