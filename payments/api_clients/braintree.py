from django.conf import settings
import braintree
import uuid
import OpenSSL


class BrainTreeAPI:

    def __init__(self):

        if settings.DEBUG:
            braintree_cfg = settings.BRAINTREE_API['SANDBOX']
            braintree.Configuration.configure(
                braintree.Environment.Sandbox,
                merchant_id=braintree_cfg['merchant_id'],
                public_key=braintree_cfg['public_key'],
                private_key=braintree_cfg['private_key'],
                timeout=braintree_cfg['timeout'])
            self.merchant_accounts = braintree_cfg['merchant_accounts']
            self.braintree_vault = braintree_cfg['vault']
        else:
            braintree_cfg = settings.BRAINTREE_API['PRODUCTION']
            braintree.Configuration.configure(
                braintree.Environment.Production,
                merchant_id=braintree_cfg['merchant_id'],
                public_key=braintree_cfg['public_key'],
                private_key=braintree_cfg['private_key'],
                timeout=braintree_cfg['timeout'])
            self.merchant_accounts = braintree_cfg['merchant_accounts']
            self.braintree_vault = braintree_cfg['vault']

    def get_client_token(self, customer_pk):
        if self.braintree_vault:
            try:
                result = braintree.ClientToken.generate({
                    "customer_id": customer_pk
                })
            except:
                result = braintree.ClientToken.generate()
        else:
            result = braintree.ClientToken.generate()
        return result

    def get_client_token_history(self, profile):
        if not profile.sig_key:
            profile.sig_key = self.get_user_sig_key()
            profile.save()
        res = None
        customer = self.find_customer(profile.sig_key)
        user = profile.user
        if not customer or res.is_success:
            res = self.create_customer(user, profile.sig_key)

        if customer or res.is_success:
            res = braintree.ClientToken.generate({
                "customer_id": profile.sig_key
            })

        return res

    def get_user_sig_key(self):
        key = str(uuid.UUID(bytes=OpenSSL.rand.bytes(16)))
        key = key.split("-")
        key = "".join(key)
        return key

    def find_customer(self, key):
        try:
            customer = braintree.Customer.find(key)
        except:
            customer = None
        return customer

    def create_customer(self, user, sig_key):
        if user.first_name:
            first_name = user.first_name
        else:
            first_name = user.username

        if user.last_name:
            last_name = user.last_name
        else:
            last_name = ''

        result = braintree.Customer.create(
            {
                "id": sig_key,
                "first_name": first_name,
                "last_name": last_name
            }
        )
        return result

    def create_payment_method(self, sig_key, payment_method_nonce):
        result = braintree.PaymentMethod.create({
            "customer_id": sig_key,
            "payment_method_nonce": payment_method_nonce,
            "options": {
                "verify_card": True,
                "fail_on_duplicate_payment_method": False
                # "fail_on_duplicate_payment_method": True
            }
        })

        return result

    def make_default(self, pref):
        token = pref.paymentcredentials_set.last().token
        if pref.main_type == 'PayPal':
            result = braintree.PayPalAccount.update(
                token,
                {
                    "options": {
                        "make_default": True
                    }
                }
            )
        elif pref.main_type == 'Card':
            result = braintree.PaymentMethod.update(
                token,
                {
                    "options": {
                        "make_default": True
                    }
                }
            )
        else:
            result = None

        return result

    def delete_payment_method(self, pref):
        token = pref.paymentcredentials_set.last().token
        result = braintree.PaymentMethod.delete(token)
        return result

    def send_payment(self, pref, amount, currency=None):
        if not currency and currency \
                not in self.merchant_accounts:
            raise ValueError("Payment not using the correct currency")

        token = pref.paymentcredentials_set.last().token
        result = braintree.Transaction.sale(
            {
                "payment_method_token": token,
                "amount": amount,
                "merchant_account_id": self.merchant_accounts[currency],
                "options": {"submit_for_settlement": True}
            }
        )
        return result
