# -*- coding: utf-8 -*-

from odoo import models, fields, api


class account_manager(models.Model):
    _name = 'account_manager'
    _inherit = ["mail.thread"]
    _description = 'Account Manager'

    name = fields.Char(string='Account Name',compute='_compute_name',store=1)
    company_id=fields.Many2one('res.company',required=True, readonly=False, default=lambda self: self.env.company,tracking=1)
    currency_id=fields.Many2one('res.currency',required=True, readonly=False,tracking=1,default=lambda self :  self.env.company.currency_id)
    integration_username=fields.Char()
    integration_password=fields.Char()
    @api.depends('company_id','currency_id')
    def _compute_name(self):
        if self.company_id and self.currency_id:
            self.name=self.company_id.name +" " + self.currency_id.name
        else :
            self.name=''










