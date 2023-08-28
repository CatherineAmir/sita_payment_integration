from odoo import api, fields, models, _
from datetime import datetime
from datetime import timedelta
from ..controllers.payment_class import Payment
from odoo.exceptions import ValidationError
import urllib.parse as parse
# todo: add
# todo domain account company
# add user id and user see all transaction or hiw own transactions
# website logo
# website footer
# remove contact us
# remove
# sign in

class Transaction(models.Model):
    _name = 'transaction'
    _inherit = 'mail.thread'
    _description = 'details for transaction'
    _order = 'created_on desc'
    name = fields.Char(string="Transaction")
    account_id = fields.Many2one('account_manager', string = "Account", tracking = 1, readonly = 0,
                                 states = {'not_processed': [('readonly', False)]},store=1)
    company_id=fields.Many2one('res.company', string="Hotel Name",default=lambda self:self.env.company.id,readonly=1)
    user_id=fields.Many2one('res.users', string="User",default=lambda self:self.env.user.id)
    created_on = fields.Datetime(default = lambda self: datetime.now(), string = 'Created on')
    verified_on = fields.Datetime(string = 'Verified on', tracking = 1, )
    failed_on = fields.Datetime(string = 'Failed  on', tracking = 1)
    link_created = fields.Datetime(string = 'Link Creation Date', tracking = 1)
    client_name = fields.Char('Guest Name', tracking = 1, readonly = True,
                              states = {'not_processed': [('readonly', False)]})
    client_email = fields.Char('Guest Email', tracking = 1, readonly = True,
                               states = {'not_processed': [('readonly', False)]})
    client_mobile = fields.Char('Guest Mobile', tracking = 1, readonly = True,
                                states = {'not_processed': [('readonly', False)]})
    reservation_id = fields.Char('Reservation Number', tracking = 1)
    amount = fields.Monetary('Amount', tracking = 1, readonly = True,
                             states = {'not_processed': [('readonly', False)]})
    # link_validity=fields.Char()
    state = fields.Selection(selection = [
        ('not_processed', 'New'),
        ('done', 'Done'),
        ('failed', 'Failed'),
        ('pending', 'Pending'), ], string = 'Payment Status', tracking = 1, default = 'not_processed', copy = False,store=1)
    payment_subject = fields.Text('Service  Description', default = 'Hotel Reservation', required = 1, readonly = True,
                                  states = {'not_processed': [('readonly', False)]})

    payment_link = fields.Char(copy = False, tracking = 1)
    currency_id = fields.Many2one('res.currency', related = 'account_id.currency_id', store = 1)
    session_id = fields.Char(string = 'Session ID', copy = False, tracking = 1)
    session_version = fields.Char(string = 'Session Version', copy = False, tracking = 1)
    success_indicator = fields.Char(string = "Success Indicator", copy = False, tracking = 1)
    result = fields.Char(string = " Result", copy = False, tracking = 1)
    authentication_status = fields.Char(string = 'Authentication Status', copy = False, tracking = 1)

    # order_reterive_field=
    amount_charged = fields.Float('Amount Charged')
    auth_3d_transaction_id = fields.Char()
    certainty = fields.Char()
    chargeback_amount = fields.Float('Charge back amount')
    chargeback_currency = fields.Char('Charge back Currency')

    error_cause = fields.Char('Error Cause')
    error_explanation = fields.Char('Error Explanation')
    link_active = fields.Boolean(default = False)
    link_validity = fields.Integer(default = 72, string = "Link expiration after")
    payment_state = fields.Char('Transaction State')

    internal_note = fields.Text("Internal Notes")

    def send_whatsapp(self):

        link = "https://web.whatsapp.com/send?phone=" + self.client_mobile
        if self.client_mobile.startswith("01") and len(self.client_mobile)==11:

            link = "https://wa.me/"+ "+2"+self.client_mobile
        elif self.client_mobile.startswith('+'):
            link = "https://wa.me/" + "+2" + self.client_mobile
        elif len(self.client_mobile)<11 :
            raise ValidationError(_("Client Mobile should be minimum 11 charachers"))
        else:
            raise ValidationError(_("Client Mobile should Start with + and country code if the client is not Egyptian"))


        message_string="""
        *Hello {}* 
        
        *Your reservation description* : {}
        *Your Total Amount is:* {} {} 
        *You can pay by the following link:*
        *{}*
        *This Link is valid for:* {} Hours         
        """.format(self.client_name,self.payment_subject,self.amount,self.currency_id.name
                   ,self.payment_link,self.link_validity)



        return {
            'type': 'ir.actions.act_url',
            'name': "Whatsapp",
            'url': link + "?text=" + parse.quote(message_string),
            'target': 'new'
        }



    def get_order_state(self):
        self.check_link_validity()
        for order_id in self:

            account_id = order_id.account_id
            payment = Payment(account_id.integration_username, account_id.integration_password, account_id.merchant_id,
                              order_id.name, account_id.api_url)
            order_state = payment.retrieve_order()



            try:
                flag = 0

                if order_state['result'] == 'SUCCESS' and order_state['status'] == 'CAPTURED':
                    payment_status = 'done'
                    flag = 1
                elif order_state['result'] == 'SUCCESS' and order_state['status'] == 'AUTHORIZED':
                    payment_status = 'pending'
                    flag = 1
                elif order_state['result'] == 'SUCCESS' and order_state['status'] == 'FAILED':
                    payment_status = 'failed'
                    flag = 1
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
                        'payment_state': order_state['status']
                    }
                    order_id.write(payment_details)
                else:
                    try:
                        # print('in else try')

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
                        # print('Exception failed', e)
                        pass

            except Exception as e:
                # print('Exception success', e)
                pass


    @api.constrains('amount')
    def check_amount(self):
        if self.amount <= 0.0:
            raise ValidationError(_("Order amount must be a positive number Greater than zero"))

    @api.model
    def create(self, vals):

        vals['name'] = self.env['ir.sequence'].next_by_code('transaction.sequence') or _('New')
        return super(Transaction, self).create(vals)

    def create_payment_link(self):
        # base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        base_url="https://sita-pay.com"
        link = base_url + '/checkout/order-pay/' + self.name
        self.payment_link = link
        self.link_created = datetime.now()
        self.link_active = True

    @api.model
    def check_link_validity(self):
        time_now = datetime.now()
        order_ids = self.env['transaction'].sudo().search([("link_active","=",True)])

        for order_id in order_ids:
            link_created = order_id.link_created
            valid_till = order_id.link_validity

            if link_created:
                if link_created + timedelta(hours = valid_till) <= datetime.now():

                    order_id.link_active = False
            else:

                order_id.link_active = False
