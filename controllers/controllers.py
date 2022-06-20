# -*- coding: utf-8 -*-
# from odoo import http


# class SitaPaymentIntegration(http.Controller):
#     @http.route('/sita_payment_integration/sita_payment_integration/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sita_payment_integration/sita_payment_integration/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sita_payment_integration.listing', {
#             'root': '/sita_payment_integration/sita_payment_integration',
#             'objects': http.request.env['sita_payment_integration.sita_payment_integration'].search([]),
#         })

#     @http.route('/sita_payment_integration/sita_payment_integration/objects/<model("sita_payment_integration.sita_payment_integration"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sita_payment_integration.object', {
#             'object': obj
#         })
