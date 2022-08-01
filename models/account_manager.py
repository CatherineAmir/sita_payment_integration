# -*- coding: utf-8 -*-

from odoo import models, fields, api


class account_manager(models.Model):
    _name = 'account_manager'
    _inherit = ["mail.thread"]
    _description = 'Account Manager'

    name = fields.Char(string='Account Name',compute='_compute_name',store=1)
    company_id=fields.Many2one('res.company',required=True, readonly=False, default=lambda self: self.env.company,tracking=1)
    currency_id=fields.Many2one('res.currency',required=True, readonly=False,tracking=1,default=lambda self :  self.env.company.currency_id)
    integration_username=fields.Char(string='API User Name',required=1,tracking=1,compute='compute_api_user_name',store=True)
    integration_password=fields.Char(string='API User Password',required=1,tracking=1)
    merchant_name=fields.Char(string='Merchant Name',required=1,tracking=1)
    merchant_id=fields.Char(string='Merchant ID',required=1,tracking=1)
    api_url=fields.Selection(selection=[('https://test-nbe.gateway.mastercard.com/api/nvp/version/65','Test'),('https://nbe.gateway.mastercard.com/api/nvp/version/65','Live')],default='https://test-nbe.gateway.mastercard.com/api/nvp/version/65',required=1)
    @api.depends('company_id','currency_id')
    def _compute_name(self):
        if self.company_id and self.currency_id:
            self.name=self.company_id.name +" " + self.currency_id.name
        else :
            self.name=''


    @api.depends('merchant_id')
    def compute_api_user_name(self):
        if self.merchant_id:
            self.integration_username='merchant.'+self.merchant_id
        else:
            self.merchant_id=False







