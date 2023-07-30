from odoo import api , fields ,models,_
from datetime import datetime
from datetime import timedelta
from ..controllers.payment_class import Payment
from odoo.exceptions import ValidationError
class Transaction(models.Model):
    _name='transaction'
    _inherit='mail.thread'
    _description='details for transaction'
    _order='created_on desc'
    name=fields.Char()
    account_id=fields.Many2one('account_manager',string="Account",tracking=1,readonly=0,
        states={'not_processed': [('readonly', False)]})
    created_on=fields.Datetime(default=lambda self : datetime.now(),string='Order Created on')
    verified_on=fields.Datetime(string='Order Verified on' , tracking=1,)
    failed_on = fields.Datetime(string='Order Failed  on',tracking=1)
    link_created=fields.Datetime(string='Link Created on',tracking=1)
    client_name=fields.Char('Client Name',tracking=1,readonly=True,
        states={'not_processed': [('readonly', False)]})
    client_email=fields.Char('Client Email',tracking=1,readonly=True,
        states={'not_processed': [('readonly', False)]})
    client_mobile=fields.Char('Client Mobile',tracking=1,readonly=True,
        states={'not_processed': [('readonly', False)]})
    reservation_id=fields.Char('Reservation Number',tracking=1,readonly=True,
        states={'not_processed': [('readonly', False)]})
    amount=fields.Monetary('Amount',tracking=1,readonly=True,
        states={'not_processed': [('readonly', False)]})
    # link_validity=fields.Char()
    state=fields.Selection(selection=[
                                     ('not_processed','New'),
                                            ('done', 'Done'),
                                            ('failed', 'Failed'),
                                            ('pending', 'Pending'),],string='Payment Status',tracking=1,default='not_processed',copy=False)
    payment_subject=fields.Text('Service  Description', default='Order Goods',required=1,readonly=True,
        states={'not_processed': [('readonly', False)]})
    payment_link=fields.Char(copy=False,tracking=1)
    currency_id=fields.Many2one('res.currency',related='account_id.currency_id',store=1)
    session_id=fields.Char(string='Session id',copy=False,tracking=1)
    session_version=fields.Char(string='Session Version',copy=False,tracking=1)
    success_indicator=fields.Char(string="Success Indicator",copy=False,tracking=1)
    result = fields.Char(string=" Result",copy=False,tracking=1)
    authentication_status=fields.Char(string='Authentication Status',copy=False,tracking=1)


    # order_reterive_field=
    amount_charged=fields.Float('Amount Charged')
    auth_3d_transaction_id=fields.Char()
    certainty=fields.Char()
    chargeback_amount = fields.Float('Charge back amount')
    chargeback_currency=fields.Char('Charge back Currency')

    error_cause=fields.Char('Error Cause')
    error_explanation=fields.Char('Error Explanation')
    link_active=fields.Boolean(default=False)
    link_validity=fields.Integer(default=24,string="link expiration after")
    payment_state=fields.Char('Transaction State')

    internal_note=fields.Text("Internal Notes")

    # def send_whatsapp(self):
    #
    #     url="https://wa.me/"whatsappphonenumber?text=urlencodedtext"

    def get_order_state(self):
       for order_id in self:

           account_id = order_id.account_id
           payment = Payment(account_id.integration_username, account_id.integration_password, account_id.merchant_id,order_id.name,account_id.api_url)
           order_state=payment.retrieve_order()
           print('order_state',order_state)
           # print('order_state_result',order_state['result'])
           # print('order_state_status', order_state['status'])


           try:
               flag=0

               if order_state['result']=='SUCCESS' and order_state['status']=='CAPTURED':
                    payment_status='done'
                    flag=1
               elif order_state['result']=='SUCCESS' and  order_state['status']=='AUTHORIZED':
                   payment_status = 'pending'
                   flag = 1
               elif order_state['result'] == 'SUCCESS' and order_state['status'] == 'FAILED':
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
                        'payment_state':order_state['status']
                    }
                    order_id.write(payment_details)
               else:
                   try:
                       print('in else try')

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
                   except Exception as e:
                       print('Exception failed', e)
                       pass

           except Exception as e:
               print('Exception success', e)
               pass






    @api.constrains('amount')
    def check_amount(self):
        if self.amount <=0.0:
            raise ValidationError(_("Order amount must be a positive number Greater than zero"))

    @api.model
    def create(self,vals):

        vals['name']=self.env['ir.sequence'].next_by_code('transaction.sequence') or _('New')
        return super(Transaction, self).create(vals)

    def create_payment_link(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        link=base_url+'/checkout/order-pay/'+self.name+'/reservation_id/'+self.reservation_id
        self.payment_link=link
        self.link_created=datetime.now()
        self.link_active=True

    @api.model
    def check_link_validity(self):
        time_now=datetime.now()
        order_ids= self.env['transaction'].search([('created_on', '>',time_now-timedelta(hours=24))])

        for order_id in order_ids:

            print('order_id',order_id)
            link_created = order_id.link_created
            valid_till = order_id.link_validity
            # print('valid_till', valid_till)
            # print('link_created', link_created)
            if link_created:
                if link_created + timedelta(hours=valid_till) <= datetime.now():
                    # print('link expires')
                    order_id.link_active = False
            else:
                # print('force expire')
                order_id.link_active = False

