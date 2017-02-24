from decimal import Decimal
from hashlib import md5
from django.conf import settings


def money_format(value, is_numeric=True, places=2, curr='', sep=',', dp='.',
                 pos='', neg='-', trailneg=''):
    q = Decimal(10) ** -places  # 2 places --> '0.01'
    if is_numeric:
        return value.quantize(q)
    sign, digits, exp = value.quantize(q).as_tuple()
    result = []
    digits = list(map(str, digits))
    build, next = result.append, digits.pop
    if sign:
        build(trailneg)
    for i in range(places):
        build(next() if digits else '0')
    if places:
        build(dp)
    if not digits:
        build('0')
    i = 0
    while digits:
        build(next())
        i += 1
        if i == 3 and digits:
            i = 0
            build(sep)
    build(curr)
    build(neg if sign else pos)
    return ''.join(reversed(result))


def geturl_robokassa(_inv_id, out_summ):
    # Уникальный номер заказа в Вашем магазине.
    # Указываем именно ноль, чтобы ROBOKASSA
    #  сама вела нумерацию заказов
    inv_id = str(_inv_id)

    hex_string = ':'.join([settings.ROBOKASSA_LOGIN, out_summ,
                           inv_id, settings.ROBOKASSA_PASS1])

    crc = md5(hex_string.encode('utf-8')).hexdigest()

    url = settings.ROBOKASSA_URL.format(
        settings.ROBOKASSA_IS_TEST,
        settings.ROBOKASSA_LOGIN,
        out_summ,
        inv_id,
        crc
    )

    return url


def check_signature_robo(_inv_id, out_summ, crc):
    hex_string = ':'.join([out_summ,
                           _inv_id, settings.ROBOKASSA_PASS1])

    my_crc = md5(hex_string.encode('utf-8')).hexdigest()
    if my_crc == crc:
        return True
    return False
