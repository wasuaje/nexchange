from rest_framework import serializers
from ticker.models import Price


class PriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Price
        fields = ('type', 'created_on', 'unix_time', 'price_usd_formatted',
                  'price_rub_formatted', 'price_eur_formatted')
