from selenium import webdriver
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import os
import sys
from django.core.management.base import BaseCommand
from core.models import SmsToken


class Command(BaseCommand):

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.issavescreen = False
        self.url = 'http://localhost:8000/'
        self.screenpath = os.path.join(
            os.path.dirname(__file__), 'Screenshots')

        if not os.path.exists(self.screenpath):
            os.makedirs(self.screenpath)
        user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64)' \
                     ' AppleWebKit/537.36 (KHTML, like Gecko)' \
                     ' Chrome/37.0.2062.120 Safari/537.36'
        self.dcap = dict(DesiredCapabilities.PHANTOMJS)
        self.dcap["phantomjs.page.settings.userAgent"] = user_agent
        self.timeout = 3
        self.driver = webdriver.PhantomJS(
            service_args=['--ignore-ssl-errors=true', '--ssl-protocol=any'],
            desired_capabilities=self.dcap)
        self.driver.set_window_size(1400, 1000)
        self.driver.set_page_load_timeout(3)
        self.wait = WebDriverWait(self.driver, self.timeout)

    def handle(self, *args, **options):
        banks = ['alfa-bank', 'Sberbank', 'Qiwi wallet']
        print('Test buy')
        for b in banks:
            try:
                self.checkbuy(b)
            except Exception as e:
                print(b + " " + str(e))
                sys.exit(1)

        sellmethods = ['fa-credit-card-alt', 'Qiwi wallet', 'Cash']
        print('Test sell')
        for b in sellmethods:
            try:
                self.checksell(b)
            except Exception as e:
                print(b + " " + str(e))
                sys.exit(1)
        self.driver.close()

    def loginphone(self):
        self.doscreenshot('after check method click')
        phone = self.driver.find_elements_by_class_name('phone')
        phone[1].send_keys('1111')

        self.doscreenshot('after input phone number')
        btnes = self.driver.find_elements_by_class_name('create-acc')
        # enter send sms
        for btsendsms in btnes:
            if btsendsms.get_attribute('class') \
                    .find('btn-primary') > -1:
                btsendsms.click()
                break
        sleep(0.3)
        # input sms code
        last_sms = SmsToken.objects.filter().latest('id').sms_token
        self.wait.until(EC.element_to_be_clickable(
            (By.ID, 'verification_code'))).send_keys(last_sms)

        self.doscreenshot('after input code number')

        self.driver.execute_script('window.submit_phone()')

    def checkbuy(self, paymethod):
        print(paymethod)
        self.driver.get(self.url)
        self.doscreenshot('main_')

        self.wait.until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'trigger-buy'))).click()

        sleep(0.3)
        self.doscreenshot('after buy click')
        payments = self.driver.\
            find_elements_by_class_name('payment-method-icon')

        for p in payments:
            try:
                alt = p.get_attribute('alt').lower()
            except:
                continue
            if alt == paymethod.lower() and p.is_displayed():
                paybank = p
                break

        # sleep(1)
        paybank.click()
        # login
        sleep(0.3)
        self.loginphone()
        # end login
        sleep(0.3)
        self.doscreenshot('after verifycate phone')
        # press buy
        bt_buys = self.driver.find_elements_by_class_name('buy-go')
        for b in bt_buys:
            if b.get_attribute('class') \
                    .find('place-order') > -1:
                b.click()
                break
        self.wait.until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'unique_ref')))
        self.doscreenshot('End_')
        print('Ok')
        self.driver.delete_all_cookies()

    def checksell(self, sellmethon):
        print(sellmethon)
        self.driver.get(self.url)
        self.doscreenshot('main_')
        self.wait.until(EC.element_to_be_clickable((
            By.CLASS_NAME, 'trigger-sell'))).click()
        self.doscreenshot('after sell click')
        if sellmethon == 'fa-credit-card-alt':
            self.wait.until(EC.element_to_be_clickable((
                By.CLASS_NAME, sellmethon))).click()
            self.wait.until(EC.element_to_be_clickable((
                By.NAME, 'number'))).send_keys('1111')
            self.wait.until(EC.element_to_be_clickable((
                By.CLASS_NAME, 'save-card'))).click()
        elif sellmethon == 'Qiwi wallet':
            self.wait.until(EC.element_to_be_clickable((
                By.CLASS_NAME, 'payment-method-icon')))
            selments = self.driver. \
                find_elements_by_class_name('payment-method-icon')

            for p in selments:
                try:
                    alt = p.get_attribute('alt').lower()
                except:
                    continue
                if alt == sellmethon.lower() and p.is_displayed():
                    sellbank = p
                    break
            sellbank.click()
            self.wait.until(EC.element_to_be_clickable((
                By.CLASS_NAME, 'phone'))).send_keys('1111')
            card_go = self.driver.find_elements_by_class_name('save-card')
            card_go[1].click()
        # cash
        else:
            self.wait.until(EC.element_to_be_clickable((
                By.CLASS_NAME, 'fa-money'))).click()
            sleep(0.5)
            self.driver.find_element_by_class_name('next-step').click()
        # login
        sleep(0.8)
        self.loginphone()
        # end login
        self.wait.until(EC.element_to_be_clickable((
            By.CLASS_NAME, 'sell-go'))).click()
        self.wait.until(EC.element_to_be_clickable((
            By.CLASS_NAME, 'unique_ref')))
        self.doscreenshot('End_')
        print('Ok')
        self.driver.delete_all_cookies()

    def doscreenshot(self, filename):
        if self.issavescreen:
            self.driver.get_screenshot_as_file(
                os.path.join(self.screenpath, filename + '.png'))
