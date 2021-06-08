# -*- coding: utf-8 -*-
from odoo import http

# class QcComptable(http.Controller):
#     @http.route('/qc_comptable/qc_comptable/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/qc_comptable/qc_comptable/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('qc_comptable.listing', {
#             'root': '/qc_comptable/qc_comptable',
#             'objects': http.request.env['qc_comptable.qc_comptable'].search([]),
#         })

#     @http.route('/qc_comptable/qc_comptable/objects/<model("qc_comptable.qc_comptable"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('qc_comptable.object', {
#             'object': obj
#         })