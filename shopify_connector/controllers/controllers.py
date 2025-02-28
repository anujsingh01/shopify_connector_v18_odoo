# -*- coding: utf-8 -*-
# from odoo import http


# class ShopifyConnector(http.Controller):
#     @http.route('/shopify_connector/shopify_connector', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/shopify_connector/shopify_connector/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('shopify_connector.listing', {
#             'root': '/shopify_connector/shopify_connector',
#             'objects': http.request.env['shopify_connector.shopify_connector'].search([]),
#         })

#     @http.route('/shopify_connector/shopify_connector/objects/<model("shopify_connector.shopify_connector"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('shopify_connector.object', {
#             'object': obj
#         })

