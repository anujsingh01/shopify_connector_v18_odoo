# -*- coding: utf-8 -*-
from odoo import models, fields, api
import shopify
from urllib.parse import urlparse

class ShopifySale(models.Model):
    _inherit = 'sale.order'
    _description = 'sale order through shopify'

    risk_ids = fields.One2many("shopify.order.risk", "odoo_order_id") 
    is_risky_order  = fields.Boolean()
    updated_in_shopify = fields.Boolean()
    shopify_order_id = fields.Char()
    shopify_instance_id = fields.Many2one("shopify.instance.ept", string="Shopify Instance")

class ShopifyOrderRisk(models.Model):
    _name = "shopify.order.risk"
    
    source = fields.Char()
    score = fields.Float()
    risk_id = fields.Char()
    recommendation = fields.Selection([('cancel', 'This order should be cancelled by the merchant'), ('investigate', 'This order might be fraudulent and needs further investigation'), ('accept', 'This check found no indication of fraud')])
    odoo_order_id = fields.Many2one(
        comodel_name='sale.order',
        string='Order',
        help='Properties',
        required=False,  # Set to True if the field is required
        readonly=False,  # Set to True if the field should be read-only
        store=True,  # Set to False if the field should not be stored
        index=True,  # Set to True if the field should be indexed
        copy=True,  # Set to False if the field should not be copied
        tracking=True,  # Set to True to enable ordered tracking
        ondelete='set null',  # Specify behavior on deletion
        domain=[]  # Define domain if needed
    )
    name = fields.Char(string="Order Id")
    
    


class StockPickingOrder(models.Model):
    _inherit = "stock.picking"
    
    is_shopify_delivery_order = fields.Boolean()
    

class StockMove(models.Model):
    _inherit = "account.move"
    
    shopify_instance_id = fields.Many2one("shopify.instance.ept", string="Shopify Instance")
    

class ResPartner(models.Model):
    _inherit = "res.partner"
    
    is_shopify_customer = fields.Boolean()
    shopify_customer_id = fields.Char(string="Shopify Customer Id")
    shopify_instance_id = fields.Many2one("shopify.instance.ept", string="Shopify Instance")

class StockLocation(models.Model):
    _inherit = "stock.location"
    
    shopify_location_id = fields.Char(string="Shopify Stock Location Id")    
    shopify_instance_id = fields.Many2one("shopify.instance.ept", string="Shopify Instance")


class prodcutprodcut(models.Model):
    _inherit = "product.product"
    
    shopify_varient_pk_id = fields.Char(string="Shopify varient Id")      
    inventory_item_id= fields.Char(string="Shopify inventory item Id")    


class ShopifyProductInstanceExp(models.Model):
    _name = 'shopify.product.instance.exp'
    _description = 'Product Export Instance'

    shopify_instance_id = fields.Many2one('shopify.instance.ept', string="Shopify Instance")

    def product_instance_selected_for_exp(self):
        # self.is_update
        self.env['product.template'].export_product(self.shopify_instance_id)


class Product(models.Model):
    _inherit = 'product.template'

    shopify_instance_id = fields.Many2one('shopify.instance.ept', ondelete='cascade')

    def export_product(self, instance_id, sync=True):
        selected_ids = self.env.context.get('active_ids', [])
        products_ids = self.sudo().search([('id', 'in', selected_ids)])
        # print("instance_id............", instance_id, "products_ids.................", products_ids)

        url = instance_id.shopify_host
        domain = urlparse(url).netloc

        SHOP_URL = f"https://{instance_id.shopify_api_key}:{instance_id.shopify_password}@{domain}/admin/api/2024-10"
        shopify.ShopifyResource.set_site(SHOP_URL)

        for products in products_ids:
            product_product = self.env['product.product'].sudo().search([('product_tmpl_id', '=', products.id)])

            product_title= products.name
            product_body_html = f"<strong>{products.description}!</strong>"
            product_vendor = instance_id.name
            product_product_type = products.categ_id.name

            attributes= products.attribute_line_ids
            product_options=[]
            if attributes:
                for attribute in attributes:
                    var_values=[]
                    for values in attribute.value_ids:
                        var_values.append(values.name)
                    product_options.append({"name":attribute.attribute_id.name ,"values": var_values})  

            print("product_options....................",product_options)      
            product_variants=[]
            varient_tag=1
            for product_var in product_product:
                options={}
                options_value=1
                
                if product_var.product_template_variant_value_ids:

                    for optio in product_var.product_template_variant_value_ids:

                        options["option" + f"{options_value}"] = optio.product_attribute_value_id.name
                        options_value += 1

                    import random
                    random_number = random.randint(1000, 9999)
                    joined_string = "_".join(options.values()) + f"_{random_number}"
                    options["sku"] = joined_string
                    options["price"] = product_var.lst_price
                    options["inventory_quantity"] = 50
                    options["inventory_management"] = "shopify"
                    variant = shopify.Variant(options)
                    product_variants.append(variant)   

                    product_var.write({"default_code": joined_string })


                else:
                    product_title= products.name
                    product_body_html = f"<strong>{products.description}!</strong>"
                    product_vendor = instance_id.name
                    product_product_type = products.categ_id.name
                    product_price=products.list_price
                    product_options=[]
                    product_variants = [shopify.Variant({
                            "price": product_price,                # Price for the product
                            "sku": product_title,       # SKU for the product
                            "inventory_quantity": 50,        # Inventory quantity
                            "inventory_management": "shopify", # Enable inventory tracking
                        })]
                    
                    product_var.write({"default_code": product_title })

            try:
                product = shopify.Product()
                # Set product details
                product.title = product_title
                product.body_html = product_body_html
                product.vendor = product_vendor
                product.product_type = product_product_type
                product.options = product_options
                # Add the variant to the product
                product.variants = product_variants
                # Save the product
                product.save()
                # Check for errors
                if product.errors:
                    print("Errors occurred:", product.errors.full_messages())
                else:

                    print(f"Product '{product.title}' created successfully with inventory tracking and SKU!")
                    # Extract product and variant details
                    variant_id = product.variants
                    for vare in variant_id:
                        print(f"Variant ID: {vare.id}")
                        print(f"Variant SKU: {vare.sku}")

                        # Find the product.product records where product_tmpl_id = 1
                        prod_es = self.env['product.product'].sudo().search([('default_code', '=', vare.sku)])
                        if prod_es:
                            # # Update fields for the found product(s)
                            prod_es.write({
                                'shopify_varient_pk_id': vare.id,  # Replace with the actual field name and the new value you want to set
                                "inventory_item_id":vare.inventory_item_id
                                # Add more fields to update as needed
                            })


            except Exception as e:
                print(f"Error creating product: {e}")

