from rest_framework.routers import SimpleRouter
from referrals.views import ReferralViewSet
from django.conf.urls import url
from referrals.views import referrals

router = SimpleRouter()
router.register(r'referrals', ReferralViewSet, base_name='referrals')
referrals_api_patterns = router.urls

referral_urls = [
    url(r'', referrals)
]
