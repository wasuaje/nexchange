from rest_framework.routers import SimpleRouter
from ticker.views import LastPricesViewSet, PriceHistoryViewSet

router = SimpleRouter()
router.register(r'price/latest', LastPricesViewSet, base_name='latest')
router.register(r'price/history', PriceHistoryViewSet, base_name='history')
ticker_api_patterns = router.urls
