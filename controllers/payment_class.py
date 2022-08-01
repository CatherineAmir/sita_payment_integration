import requests
import json
import base64
from requests.structures import CaseInsensitiveDict
import urllib
host_name='localhost:8069'
# ma3had
# host_name='143.244.213.72'

class Payment():
    def __init__(self, apiUsername, apiPassword, merchant,order_id,url):
        self.apiUsername = apiUsername
        self.apiPassword = apiPassword
        self.merchant = merchant
        self.order_id = order_id
        self.url=url
        self.order_currency = None
        self.order_amount = None
        self.checkout_mode = None
        self.result = None
        self.session_id = None
        self.success_indictator = None
        self.session_version = None
        self.session_update_status = None

    def create_header(self):
        headers = CaseInsensitiveDict()
        headers["Content-Type"] = "application/x-www-form-urlencoded"

        return headers

    def authorize(self, order_currency, order_id, order_amount):
        self.order_currency = str(order_currency)
        self.order_amount = str(order_amount)

        payload = 'apiOperation=INITIATE_CHECKOUT&apiPassword=' + \
                  self.apiPassword + '&apiUsername=' + self.apiUsername + '&merchant=' + self.merchant + '&interaction.operation=PURCHASE&interaction.returnUrl=http://'+host_name+'/success_payment/&order.id=' + \
                  self.order_id + '&order.amount=' + self.order_amount + '&order.currency=' + self.order_currency
        # +'&checkoutMode=PAYMENT_LINK'
        # url = 'https://test-nbe.gateway.mastercard.com/api/nvp/version/65'
        #
        # url = 'https://nbe.gateway.mastercard.com/api/nvp/version/65'
        # url = 'https://eshopping.nbe.com.eg/webapi/api/nvp/version/65'
        # https://sita-eg.com


        response = requests.post(self.url, headers=self.create_header(), data=payload)
        print('session_response_dict , response', response)

        response_dict = self.response_handler(response.content.decode())
        print('session_response_dict',response_dict)

        try:
            self.result = response_dict['result']
            print('result',self.result)
            self.session_id = response_dict['session.id']
            self.session_version = response_dict['session.version']
            print('session_version', self.session_version)

            self.success_indicator = response_dict['successIndicator']
            print('success_indicator', self.success_indicator)
            self.session_update_status = response_dict['session.updateStatus']
        except Exception as e:
            print('exception',e)
            pass
        return response_dict


    def response_handler(self, content):
        result = urllib.parse.parse_qs(content)
        for k in result.keys():
            result[k] = result[k][0]
        return result

    def retrieve_order(self):
        # url = 'https://test-nbe.gateway.mastercard.com/api/nvp/version/65'
        # url = 'https://nbe.gateway.mastercard.com/api/nvp/version/65'
        payload = 'apiOperation=RETRIEVE_ORDER&apiPassword=' + self.apiPassword + '&apiUsername=' + self.apiUsername + '&merchant=' + self.merchant + '&order.id=' + self.order_id

        response = requests.post(self.url, headers=self.create_header(), data=payload)


        response_dict = self.response_handler(response.content.decode())


        return response_dict