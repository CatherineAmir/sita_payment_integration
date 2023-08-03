# -*- coding: utf-8 -*-
# from odoo import http
from odoo import http
from odoo.http import request
from .payment_class import Payment
import requests
import jinja2
import os
from datetime import datetime
from datetime import timedelta
import pathlib
searchpath=pathlib.Path(__file__).parent.resolve()
templateLoader = jinja2.FileSystemLoader(searchpath=searchpath)
TEMPLATEENV = jinja2.Environment(loader=templateLoader)
class PaymentRequest(http.Controller):

    @http.route('/checkout/order-pay/<string:order_id>/reservation_id/<string:reservation_id>', type='http', auth="public", methods= ['GET'], website=True)
    def request_value(self,**kw):

        order_id=request.env['transaction'].sudo().search([('name','=',kw['order_id']),('reservation_id','=',kw['reservation_id'])],)[-1]
        link_created=order_id.link_created

        valid_till=order_id.link_validity
        link_type=order_id.account_id.api_url
        company_id=order_id.account_id.company_id
        context={
            "company_id": company_id,
        }



        if order_id.state=='not_processed' or  order_id.state=='failed':

            if link_created:
                if link_created + timedelta(minutes=valid_till) <= datetime.now():
                    # print('link expires')
                    order_id.link_active = False
                    TEMPLATE_FILE = "link_expires.html"
                    template = TEMPLATEENV.get_template(TEMPLATE_FILE)
                    return template.render(context)
                # else:
                #     print('pass', 'link is not create')
                else:
                    account_id = order_id.account_id
                    # print('account_id_url', account_id.api_url)
                    payment = Payment(account_id.integration_username, account_id.integration_password, account_id.merchant_id,order_id.name,account_id.api_url)

                    try:
                        session_dict = payment.authorize(order_id.currency_id.name, order_id.name, order_id.amount)
                        # print('session_dict',session_dict)
                        transaction_vals={
                            'session_id':payment.session_id,
                            'session_version': payment.session_version,
                            'success_indicator':payment.success_indicator,
                            'result':payment.result,


                        }
                        order_id.write(transaction_vals)

                        context = {
                            'link_type':link_type,
                            'session_id': payment.session_id,
                            'order_id': order_id.name,
                            'session_version': payment.session_version,
                            'merchant_name': account_id.merchant_id,
                            'amount': order_id.amount,
                            'currency': order_id.currency_id.name,
                            'description':order_id.payment_subject,
                            'client_name': order_id.client_name,
                            'client_email': order_id.client_email,
                            'reservation_id': order_id.reservation_id,
                            "company_id":company_id,


                            }
                        # print('context',context)

                        TEMPLATE_FILE = "home.html"
                        template = TEMPLATEENV.get_template(TEMPLATE_FILE)
                        return template.render(context)
                    except Exception as e:
                        # print("exception",e)


                        TEMPLATE_FILE = "session_failed.html"
                        template = TEMPLATEENV.get_template(TEMPLATE_FILE)
                        context={
                            'error':e,
                            'order_id':order_id,
                            "company_id":company_id,
                            # 'error_cause':session_dict['error.cause'],
                            # 'error_explanation': session_dict['error.explanation'],

                        }

                    return template.render(context)

        else:
            context = {

                'order_id': order_id.name,
                "company_id":company_id,

            }

            TEMPLATE_FILE = "fail.html"
            template = TEMPLATEENV.get_template(TEMPLATE_FILE)
            return template.render(context)

    @http.route('/success_payment', type='http', auth="none", methods=['GET','POST'])
    def success_transaction(self,**kw):
       result_indicator=kw.get('resultIndicator')
       order_id=request.env['transaction'].sudo().search([('success_indicator','=',result_indicator)])
       if order_id:

           account_id = order_id.account_id

           payment = Payment(account_id.integration_username, account_id.integration_password, account_id.merchant_id,order_id.name,account_id.api_url)
           order_state=payment.retrieve_order()
           try:
               flag=0

               if order_state['result']=='SUCCESS' and order_state['status']=='CAPTURED':
                    payment_status='done'
                    flag=1
               elif order_state['result']=='SUCCESS' and order_state['status']=='FAILED':
                    payment_status = 'failed'
                    flag=1
               if flag:
                    datetime_str = order_state['creationTime']
                    date_time_obj = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S.%fZ')
                    payment_details = {
                        'amount_charged': float(order_state['amount']),
                        'auth_3d_transaction_id': order_state['authentication.3ds.transactionId'],
                        # 'certainty': order_state['certainty'],
                        'chargeback_amount': float(order_state['chargeback.amount']),
                        'chargeback_currency': order_state['chargeback.currency'],
                        'verified_on': date_time_obj,
                        'result': order_state['result'],
                        'state': payment_status,
                        'authentication_status': order_state['authenticationStatus'],
                        'payment_state': order_state['status'],

                    }
                    order_id.write(payment_details)
                    company_id=order_id.account_id.company_id
                    TEMPLATE_FILE = "payment_done.html"
                    template = TEMPLATEENV.get_template(TEMPLATE_FILE)
                    context={
                         'order_id':order_id.name,
                        "company_id":company_id,
                     }
                    return template.render(context)
               else:
                   try:


                       date_time_obj = datetime.now()
                       if order_state['result'] == 'ERROR':
                           payment_status = 'not_processed'
                       payment_details = {
                           'error_cause': order_state['error.cause'],
                           'error_explanation': order_state['error.explanation'],
                           'result': order_state['result'],
                           'state': payment_status,
                           'failed_on': date_time_obj,

                       }

                       order_id.write(payment_details)
                       company_id=order_id.account_id.company_id

                       TEMPLATE_FILE = 'session_failed.html'
                       template = TEMPLATEENV.get_template(TEMPLATE_FILE)
                       context = {
                           'order_id': order_id.name,
                           'company_id':company_id
                       }
                       return template.render(context)


                   except Exception as e:

                       pass

           except Exception as e:

               pass









