from django.contrib import admin
from .models import ReferralCode, Referral, Program

admin.site.register(ReferralCode)
admin.site.register(Referral)
admin.site.register(Program)
admin.autodiscover()
