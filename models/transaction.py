from odoo import api , fields ,models

class Transaction(models.Model):
    _name='transaction'
    _inherit='mail.thread'
    _description='details for transaction'
    _order='created_on desc'
    name=fields.Char()
    account_id=fields.Many2one('account_manager',string="Account",tracking=1)
    created_on=fields.Datetime()
    verified_on=fields.Datetime()
    client_name=fields.Char('Client Name')
    client_email=fields.Char('Client Email')
    client_mobile=fields.Char('Client Mobile')
    amount=fields.Float('Amount',tracking=1)
    link_validity=fields.Char()
    payment_status=fields.Selection(selection=[('done','Done'),
                                               ('rejected','Rejected'),
                                               ('pending','Pending')],string='Payment Status',traking=1)
    payment_subject=fields.Text('Service for Payment')
    payment_link=fields.Char()
    currency_id=fields.Many2one('res.currency',related='account_id.currency_id',store=1)