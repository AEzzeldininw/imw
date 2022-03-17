# -*- coding: utf-8 -*-
from odoo import http

# class ImwCustomization(http.Controller):
#     @http.route('/imw__customization/imw__customization/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/imw__customization/imw__customization/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('imw__customization.listing', {
#             'root': '/imw__customization/imw__customization',
#             'objects': http.request.env['imw__customization.imw__customization'].search([]),
#         })

#     @http.route('/imw__customization/imw__customization/objects/<model("imw__customization.imw__customization"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('imw__customization.object', {
#             'object': obj
#         })