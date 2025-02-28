from odoo import models, fields, _
import shopify
from urllib.parse import urlparse
from odoo.exceptions import UserError
import requests
import json
from datetime import date
import uuid 

class ShopifyProcessImportExport(models.TransientModel):
    _name = 'shopify.process.import.export'
    _description = 'Shopify Process Import Export'
    
    
    cron_process_notification = fields.Text('Shopify Note')
    csv_file = fields.Binary('Csv File')
    export_stock_from = fields.Datetime('Export Stock From')
    file_name = fields.Char('File Name')
    import_products_based_on_date = fields.Selection([
        ('create_date', 'Create Date'),
        ('update_date', 'Update Date')
    ], 'Import Based On')
    is_auto_validate_inventory = fields.Boolean('Auto Validate Inventory')
    is_hide_operation_execute_button = fields.Boolean('Is Hide Operation Execute Button')
    is_import_draft_product = fields.Boolean('Import Draft Products')
    orders_from_date = fields.Datetime('From Date')
    orders_to_date = fields.Datetime('To Date')
    payout_end_date = fields.Date('End Date')
    payout_start_date = fields.Date('Start Date')
    shopify_instance_id = fields.Many2one('shopify.instance.ept', 'Instance')
    shopify_instance_ids = fields.Many2many('shopify.instance.ept',  'Instances')
    shopify_is_publish = fields.Selection([
        ('publish_product_web', 'Publish Web Only'),
        ('publish_product_global', 'Publish Web and POS'),
        ('unpublish_product', 'Unpublish'),
    ], 'Publish In Website ?')
    shopify_is_set_basic_detail = fields.Boolean('Set Basic Detail ?')
    shopify_is_set_image = fields.Boolean('Set Image ?')
    shopify_is_set_price = fields.Boolean('Set Price ?')
    shopify_is_set_stock = fields.Boolean('Set Stock ?')
    shopify_is_update_basic_detail = fields.Boolean('Update Basic Detail ?')
    shopify_is_update_price = fields.Boolean('Set Price ?')
    shopify_operation = fields.Selection([
            ('sync_product_by_remote_ids', 'Import Specific Product(s)'),
            ('sync_product', 'Import Products'),
            ('import_customers', 'Import Customers'),
            ('import_unshipped_orders', 'Import Unshipped Orders'),
            ('import_shipped_orders', 'Import Shipped Orders'),
            # ('import_buy_with_prime_orders', 'Import Buy with Prime Orders'),
            ('import_cancel_orders', 'Import Cancel Orders'),
            ('import_orders_by_remote_ids', 'Import/Update Specific Order(s)'),
            ('update_order_status', 'Export Shippment Information/Update Order Status'),
            ('import_stock', 'Import Stock'),
            ('export_stock', 'Export Stock'),
            ('import_location', 'Import Locations'),
            # ('import_products_from_csv', 'Map Products'),
            # ('import_payout_report', 'Import Payout Report')
    ], 'Operation')
    shopify_order_ids = fields.Text('Order Ids')
    shopify_template_ids = fields.Text('Template Ids')
    shopify_video_embed_code = fields.Html('Shopify Video Embed Code')
    shopify_video_url = fields.Char('Video URL')
    skip_existing_product = fields.Boolean('Do Not Update Existing Products')
    active = fields.Boolean()
    
    
    def sync_product(self):
        
        url = self.shopify_instance_id.shopify_host
        domain = urlparse(url).netloc
        
        SHOP_URL = f"https://{self.shopify_instance_id.shopify_api_key}:{self.shopify_instance_id.shopify_password}@{domain}/admin/api/2024-10"
        shopify.ShopifyResource.set_site(SHOP_URL)
        # try:
        if not self.is_import_draft_product:
            if self.import_products_based_on_date == "create_date":
                products = shopify.Product.find(created_at_min=self.orders_from_date, created_at_max=self.orders_to_date)
            elif self.import_products_based_on_date == "update_date":
                products = shopify.Product.find(updated_at_min=self.orders_from_date, updated_at_max=self.orders_to_date)
        else:
            if self.import_products_based_on_date == "create_date":
                products = shopify.Product.find(created_at_min=self.orders_from_date, created_at_max=self.orders_to_date, status='draft')
            elif self.import_products_based_on_date == "update_date":
                products = shopify.Product.find(updated_at_min=self.orders_from_date, updated_at_max=self.orders_to_date, status='draft')
        
        shopify_list = []
        
        for product in products:
            # product_obj = self.env["    .ept"].search([("shopify_tmpl_id", "=", str(product.id))])
            product_obj = self.env["shopify.product.template.ept"].search([("shopify_tmpl_id", "=", str(product.id))])
            if self.skip_existing_product and  not product_obj:
                shopify_list.append((0, 0, {"product_data_id": str(product.id),"name" : product.title, "shopify_instance_id":self.shopify_instance_id.id, "state" : "draft", "synced_product_data": product.to_dict(), "shopify_image_import_state": "done" if len(product.images) else "pending"}))
            elif not self.skip_existing_product:
                shopify_list.append((0, 0, {"product_data_id": str(product.id),"name" : product.title, "shopify_instance_id":self.shopify_instance_id.id, "state" : "draft", "synced_product_data": product.to_dict(), "shopify_image_import_state": "done" if len(product.images) else "pending"}))
                
        shopify_tmpl_dict = {
            "shopify_instance_id":self.shopify_instance_id.id,
            "skip_existing_product": self.skip_existing_product,
            "state": "draft",
            "product_data_queue_lines" : shopify_list
        }
        self.env["shopify.product.data.queue.ept"].create(shopify_tmpl_dict)
            
        # except Exception as e:
        #     print("Error occurred:", e)   

        
    def import_customers(self):

        # Initialize Shopify session
        url = self.shopify_instance_id.shopify_host
        domain = urlparse(url).netloc

        SHOP_URL = f"https://{self.shopify_instance_id.shopify_api_key}:{self.shopify_instance_id.shopify_password}@{domain}/admin"
        shopify.ShopifyResource.set_site(SHOP_URL)

        unique_id = str(uuid.uuid4())
        custoemr_queue_data= self.env['shopify.customer.data.queue.ept'].create({
                            'name': unique_id,
                            "shopify_instance_id": self.shopify_instance_id.id,
                            "record_created_from": "import_process"
                        })

        try:
            customers = shopify.Customer.find()
            customer_list=[]
            for customer in customers:
                try:
                    customer_data= customer.to_dict()
                    id = customer_data.get('id', None)
                    first_name = customer_data.get('first_name', '')
                    last_name = customer_data.get('last_name', '')
                    customer_data_line =self.env['shopify.customer.data.queue.line.ept'].create({
                            'name': first_name +" "+ last_name,
                            "shopify_customer_data_id": id,
                            "shopify_instance_id": self.shopify_instance_id.id,
                            "shopify_synced_customer_data": customer_data,
                            "state": "draft",
                            "synced_customer_queue_id": custoemr_queue_data.id
                        })
                    customer_list.append(customer_data_line)
                except Exception as e:
                    print("Error occurred:", e)   
                    custoemr_queue_data= self.env['common.log.lines.ept'].create({
                            'order_ref': e,
                            "shopify_instance_id": self.shopify_instance_id.id,
                            "message":e,
                            "shopify_customer_data_queue_line_id":custoemr_queue_data.id
                           
                        })
            
            custoemr_queue_data.write({
                        "total_record_count": len(customer_list),
                        "draft_state_count":len(customer_list),
                        "state":"draft",
                        "is_process_queue":True,
                        "is_action_require":True,
                        "draft_state_count":0,
                        "running_status":"Draft"
                        
                    })        

            print(f"Created new customer:",customer_list)  
            return {"message":"Shopify Customer imported successfully!", "type": "success","title": "Success!"}    

        except Exception as e:

            print("Error occurred:", e)
            custoemr_queue_data= self.env['common.log.lines.ept'].create({
                            'order_ref': e,
                            "shopify_instance_id": self.shopify_instance_id.id,
                            "message":e,
                            "shopify_customer_data_queue_line_id":custoemr_queue_data.id
                      
                        })
            return {"message":"Shopify Customer not imported successfully Please check log entry.", "type": "danger","title": "Error!"}   


    def import_unshipped_orders(self):
        # Initialize Shopify session
        url = self.shopify_instance_id.shopify_host
        from_date = self.orders_from_date
        print("from_date............",from_date)

        CheckSetting = self.env['res.config.settings'].search([("shopify_instance_id", '=', self.shopify_instance_id.id)],order="id desc",limit=1)
        if not CheckSetting:
            return {"message":"Please configure Order Configuration in setting section for import order from shopify .", "type": "danger","title": "Error!"}   

        if CheckSetting.shopify_import_order_after_date:
            # print("Set order date..............",CheckSetting.shopify_import_order_after_date)
            print("set date.......",CheckSetting.shopify_import_order_after_date)
            if self.orders_from_date > CheckSetting.shopify_import_order_after_date:
                pass
            else:
              return {"message":"Your Import order date is smaller than your shopify import order after data , If want to import please change in setting section. ", "type": "danger","title": "Error!"}
            
        else:
            pass
            
        to_date = self.orders_to_date
        created_at_min = from_date.isoformat()
        created_at_max = to_date.isoformat()
        domain = urlparse(url).netloc
        
        SHOP_URL = f"https://{self.shopify_instance_id.shopify_api_key}:{self.shopify_instance_id.shopify_password}@{domain}/admin"
        shopify.ShopifyResource.set_site(SHOP_URL)

        unique_id = str(uuid.uuid4())

        try:
            # # Fetch order details.
            shopifyorders = shopify.Order.find(
                    fulfillment_status="unshipped",
                    created_at_min=created_at_min,
                    created_at_max=created_at_max
                )

            order_list=[]
            if not shopifyorders:
                return {"message":"No Shopify order found between this range !", "type": "success","title": "Success!"}   
            
            order_queue_data= self.env['shopify.order.data.queue.ept'].create({
                            'name': unique_id,
                            "shopify_instance_id": self.shopify_instance_id.id,
                            "created_by": "import",
                            "queue_type":"unshipped"
                        })

            for orders in shopifyorders:
                try:
                    order_data= orders.to_dict()
                    id = order_data["id"]
                    order_name=order_data["name"]

                    order_data_line =self.env['shopify.order.data.queue.line.ept'].create({
                            'name': order_name,
                            "shopify_order_id": id,
                            "shopify_instance_id": self.shopify_instance_id.id,
                            "order_data": order_data,
                            "state": "draft",
                            "shopify_order_data_queue_id": order_queue_data.id
                        })
                    order_list.append(order_data_line)

                except Exception as e:
                    print("Error occurred:", e)   
                    custoemr_queue_data= self.env['common.log.lines.ept'].create({
                            'order_ref': e,
                            "shopify_instance_id": self.shopify_instance_id.id,
                            "message":e,
                            "shopify_order_data_queue__id":order_data_line.id
                           
                        })
            
            order_queue_data.write({
                        "order_queue_line_total_record": len(order_list),
                        "order_queue_line_draft_record":len(order_list),
                        "state":"draft",
                        "is_process_queue":True,
                        "is_action_require":True,
                        "running_status":"Draft"
                        
                    })        

            return {"message":"Shopify order imported successfully!", "type": "success","title": "Success!"}    

        except Exception as e:

            print("Error occurred:", e)
            custoemr_queue_data= self.env['common.log.lines.ept'].create({
                            'order_ref': e,
                            "shopify_instance_id": self.shopify_instance_id.id,
                            "message":e,
                            "shopify_order_data_queue__id":order_queue_data.id
                      
                        })
            return {"message":"Shopify order not imported successfully Please check log entry.", "type": "danger","title": "Error!"}   
        
    def import_shipped_orders(self):

        # Initialize Shopify session
        url = self.shopify_instance_id.shopify_host
        from_date = self.orders_from_date
        to_date = self.orders_to_date

        created_at_min = from_date.isoformat()
        created_at_max = to_date.isoformat()
        domain = urlparse(url).netloc

        CheckSetting = self.env['res.config.settings'].search([("shopify_instance_id", '=', self.shopify_instance_id.id)],order="id desc",limit=1)
        if not CheckSetting:
            return {"message":"Please configure Order Configuration in setting section for import order from shopify .", "type": "danger","title": "Error!"}   

        if CheckSetting.shopify_import_order_after_date:
            # print("Set order date..............",CheckSetting.shopify_import_order_after_date)
            print("set date.......",CheckSetting.shopify_import_order_after_date)
            if self.orders_from_date > CheckSetting.shopify_import_order_after_date:
                pass
            else:
              return {"message":"Your Import order date is smaller than your shopify import order after data , If want to import please change in setting section. ", "type": "danger","title": "Error!"}

        else:
            pass

        SHOP_URL = f"https://{self.shopify_instance_id.shopify_api_key}:{self.shopify_instance_id.shopify_password}@{domain}/admin"
        shopify.ShopifyResource.set_site(SHOP_URL)

        unique_id = str(uuid.uuid4())

        try:

            shopifyorders = shopify.Order.find(
                    status="closed",
                    created_at_min=created_at_min,
                    created_at_max=created_at_max
                )
            order_list=[]
            if not shopifyorders:
                return {"message":"No Shopify order found between this range !", "type": "success","title": "Success!"}   
            
            
            
            order_queue_data= self.env['shopify.order.data.queue.ept'].create({
                            'name': unique_id,
                            "shopify_instance_id": self.shopify_instance_id.id,
                            "created_by": "import",
                            "queue_type":"shipped"
                        })

            for orders in shopifyorders:
                try:
                    order_data= orders.to_dict()
                    id = order_data["id"]
                    order_name=order_data["name"]

                    cancel_reason= order_data["cancel_reason"]

                    if  cancel_reason == None: 
                        
                        order_data_line =self.env['shopify.order.data.queue.line.ept'].create({
                                'name': order_name,
                                "shopify_order_id": id,
                                "shopify_instance_id": self.shopify_instance_id.id,
                                "order_data": order_data,
                                "state": "draft",
                                "shopify_order_data_queue_id": order_queue_data.id
                            })
                        order_list.append(order_data_line)
                except Exception as e:
                    print("Error occurred:", e)   
                    custoemr_queue_data= self.env['common.log.lines.ept'].create({
                            'order_ref': e,
                            "shopify_instance_id": self.shopify_instance_id.id,
                            "message":e,
                            "shopify_order_data_queue__id":order_data_line.id
                           
                        })
            
            order_queue_data.write({
                        "order_queue_line_total_record": len(order_list),
                        "order_queue_line_draft_record":len(order_list),
                        "state":"draft",
                        "is_process_queue":True,
                        "is_action_require":True,
                        "running_status":"Draft"
                        
                    })        

            return {"message":"Shopify order imported successfully!", "type": "success","title": "Success!"}    

        except Exception as e:

            print("Error occurred:", e)
            custoemr_queue_data= self.env['common.log.lines.ept'].create({
                            'order_ref': e,
                            "shopify_instance_id": self.shopify_instance_id.id, 
                            "message":e,
                            "shopify_order_data_queue__id":order_queue_data.id
                      
                        })
            return {"message":"Shopify order not imported successfully Please check log entry.", "type": "danger","title": "Error!"}   

    def import_buy_with_prime_orders(self):
        pass

    def import_cancel_orders(self):

        url = self.shopify_instance_id.shopify_host
        from_date = self.orders_from_date
        to_date = self.orders_to_date
        created_at_min = from_date.isoformat()
        created_at_max = to_date.isoformat()

        CheckSetting = self.env['res.config.settings'].search([("shopify_instance_id", '=', self.shopify_instance_id.id)],order="id desc",limit=1)
        if not CheckSetting:
            return {"message":"Please configure Order Configuration in setting section for import order from shopify .", "type": "danger","title": "Error!"}   

        if CheckSetting.shopify_import_order_after_date:
            # print("Set order date..............",CheckSetting.shopify_import_order_after_date)
            print("set date.......",CheckSetting.shopify_import_order_after_date)
            if self.orders_from_date > CheckSetting.shopify_import_order_after_date:
                pass
            else:
              return {"message":"Your Import order date is smaller than your shopify import order after data , If want to import please change in setting section. ", "type": "danger","title": "Error!"}

        else:
            pass

        domain = urlparse(url).netloc
        SHOP_URL = f"https://{self.shopify_instance_id.shopify_api_key}:{self.shopify_instance_id.shopify_password}@{domain}/admin"
        shopify.ShopifyResource.set_site(SHOP_URL)
        unique_id = str(uuid.uuid4())

        try:
            shopifyorders = shopify.Order.find(
                    status="cancelled",
                    created_at_min=created_at_min,
                    created_at_max=created_at_max
                )

            if not shopifyorders:
                return {"message":"No Shopify order found between this range !", "type": "success","title": "Success!"}   
            
            for orders in shopifyorders:
                ord_data= orders.to_dict()
                id = ord_data["id"]
                try:
                    if ord_data["customer"]:
                        customerdata=ord_data["customer"]
                        customer_id =customerdata["id"]
                        email=customerdata["email"]
                        first_name=customerdata["first_name"]
                        last_name=customerdata["last_name"] 
                        phone=customerdata["phone"] 
                        address1=customerdata["default_address"]["address1"]
                        address2=customerdata["default_address"]["address2"]
                        city=customerdata["default_address"]["city"]
                        country=customerdata["default_address"]["country_name"]
                        zip_code=customerdata["default_address"]["zip"]
                        state_code=customerdata["default_address"]["province_code"]
                        country_code=customerdata["default_address"]["country_code"]
                        shopify_customer = self.env['res.partner'].search([("shopify_customer_id", '=',customer_id)], limit=1)
                        if not shopify_customer:
                            shopify_customer=self.env['res.partner'].create({
                                'name': first_name +" "+ last_name,
                                'email': email,
                                'phone': phone,
                                'street': address1,
                                'street2': address2,
                                'city': city,
                                'zip': zip_code,
                                'state_id': self._get_state_id(customerdata["default_address"]["province"]),
                                'country_id': self._get_country_id(country),
                                "shopify_customer_id": customer_id,
                                "is_shopify_customer": True,
                                'customer_rank': 1,
                            })
                        else:
                            pass

                    shopify_order_id= ord_data["id"]  
                    line_items= ord_data["line_items"]   

                    shopify_order_exist = self.env['sale.order'].search([("shopify_order_id", '=',shopify_order_id)], limit=1)
                    print("shopify_order_exist.....",shopify_order_exist)
                    
                    if not shopify_order_exist:
                        sale_order_line = []
                        for i in line_items:

                            pr_data = [0,0,{'product_id': 2,'product_uom_qty': i['current_quantity']  }]
                            sale_order_line.append(pr_data)
                            
                        sale_order_data = {

                        'user_id':2,    
                        'payment_term_id':1,
                        'partner_id': shopify_customer.id,  # ID of the partner/customer
                        'order_line': sale_order_line,
                        "shopify_order_id": shopify_order_id,
                        "state":"cancel"
                        }
                        
                        sale_order = self.env['sale.order'].sudo().create(sale_order_data)
                        invoice_data = {
                            'move_type': 'out_invoice',
                            'partner_id': sale_order.partner_id.id,
                            'invoice_origin': sale_order.name,
                            "state":"cancel",
                            'l10n_in_state_id': sale_order.partner_id.state_id.id,  # Place of Supply
                            'invoice_line_ids': [
                                (0, 0, {
                                    'product_id': line.product_id.id,
                                    'quantity': line.product_uom_qty,
                                    'price_unit': line.price_unit,
                                })
                                for line in sale_order.order_line
                            ]
                        }

                        invoice = self.env['account.move'].sudo().create(invoice_data)
                        sale_order.write({'invoice_ids': [(4, invoice.id)]})
                        # Fetch required fields from account.move.line
                        account_move_lines = self.env['account.move.line'].sudo().search_read(
                            [('move_id', '=', invoice.id), ('display_type', '=', "product")],
                            ['id']
                        )
                        # Fetch required fields from sale.order.line
                        sale_order_lines = self.env['sale.order.line'].sudo().search_read(
                            [('order_id', '=', sale_order.id)],
                            ['id']
                        )
                        # Zip the data to merge
                        merged_data = [
                            {"Account_id": acc_line['id'], "order_id": order_line['id']}
                            for acc_line, order_line in zip(account_move_lines, sale_order_lines)
                        ]
                        # Bulk insertion
                        if merged_data:
                            query = """
                                INSERT INTO sale_order_line_invoice_rel (invoice_line_id, order_line_id)
                                VALUES {}
                            """.format(", ".join("(%s, %s)" % (values["Account_id"], values["order_id"]) for values in merged_data))

                            # Execute the query
                            self.env.cr.execute(query)
                            # Commit the transaction
                            self.env.cr.commit()

                        # sale_order.action_confirm()   #conform sales order 
                        # invoice.action_post()  #conform invoice 

                        ####################################  create payment ############################################

                except Exception as e:

                    custoemr_queue_data= self.env['common.log.lines.ept'].create({
                                'order_ref': e,
                                "shopify_instance_id": self.shopify_instance_id.id,
                                "message":e
                            })   
        
            return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'title': 'Success!',
                            'message': "Unshipped order created successfully!",
                            'type': 'success',  # 'success', 'warning', 'danger', 'info'
                            'sticky': False,  # Set to True to make the notification persistent
                        }
                    }    
        
        except Exception as e:
                print("...................",e)

    def _get_country_id(self, country_name):
        """Get country ID from name."""
        country = self.env['res.country'].search([('name', '=', country_name)], limit=1)
        return country.id if country else False 

    def _get_state_id(self, state_name):
        """Get state ID from name."""
        state = self.env['res.country.state'].search([('name', '=', state_name)], limit=1)
        return state.id if state else False             

    def import_orders_by_remote_ids(self):
        Shopify_order_ids = self.shopify_order_ids.split(",")
        Shopify_order_ids = [order_id.strip() for order_id in Shopify_order_ids]
        for order in Shopify_order_ids:
            url = self.shopify_instance_id.shopify_host
            domain = urlparse(url).netloc
            SHOP_URL = f"https://{self.shopify_instance_id.shopify_api_key}:{self.shopify_instance_id.shopify_password}@{domain}/admin"
            shopify.ShopifyResource.set_site(SHOP_URL)

            try:
                order = shopify.Order.find(order)  # This retrieves the order by its ID's
                if order:

                    OrderDetailData=order.to_dict()

                    shopify_order_status = self.env['sale.order'].search([("shopify_order_id", '=',OrderDetailData["id"])], limit=1)
                    print(".........shopify_order_status.............",shopify_order_status)

                    if OrderDetailData["cancelled_at"] != None:
                        if shopify_order_status.state != "cancel":
                            shopify_order_status.write({
                                    "state":"cancel"
                                })   
                            invoice_order_status = self.env['account.move'].search([("invoice_origin", '=',shopify_order_status.name)], limit=1)
                            invoice_order_status.write({
                                    "state":"cancel"
                                })   

                    else:

                        if OrderDetailData["fulfillment_status"] == "fulfilled":
                            # Fetch the related delivery order (stock.picking)
                            picking = self.env['stock.picking'].search([('origin', '=', shopify_order_status.name), ('state', '!=', 'done')], limit=1)
                            if picking:
                                # Loop through stock moves in the picking
                                for move in picking.move_ids_without_package:  # or use move_ids if package is involved
                                    for move_line in move.move_line_ids:  # Loop through stock.move.line
                                        move_line.quantity = move.product_uom_qty  # Set qty_done on stock.move.line

                                # Confirm, assign, and validate the picking
                                picking.action_confirm()  # Confirm the picking
                                picking.action_assign()   # Assign the picking
                                picking.button_validate()  # Validate the picking

                        try: 
                            # if self.queue_type == "shipped" or financial_status == "paid":
                            
                            if OrderDetailData["financial_status"] == "paid":

                                # print(shopify_order_exist.name)
                                invoice = self.env['account.move'].search([('invoice_origin','=',shopify_order_status.name),('move_type','=',"entry")], limit=1)
                                # print(invoice)
                                if not invoice:

                                    invoice=self.env['account.move'].search([('invoice_origin','=',shopify_order_status.name),('move_type','=',"out_invoice")], limit=1)

                                    today = date.today()
                                    amount_total=invoice.amount_total

                                    move_vals = {
                                        'date': str(today),
                                        'state': 'draft',
                                        'ref': invoice.name,
                                        'move_type': 'entry',  # Ensure the move type is correct
                                        # 'to_check': False,
                                        'journal_id': 1,  # Update with the correct journal ID
                                        'company_id': invoice.company_id.id,  # Update with your company ID
                                        'currency_id': invoice.currency_id.id,  # Update with the correct currency ID
                                        'is_move_sent': False,
                                        'invoice_user_id': 2,
                                    }
                                    account_move = self.env['account.move'].sudo().create(move_vals)

                                    # Step 2: Create the payment record
                                    payment_vals = {
                                        'move_id': account_move.id,
                                        'amount': amount_total,
                                        'create_date': str(today),
                                        'payment_type': 'inbound',  # Payment type (e.g., inbound for customer payments)
                                        'partner_type': 'customer',  # Partner type (e.g., customer)
                                        'currency_id': invoice.currency_id.id,  # Update with correct currency ID
                                        'partner_id': account_move.partner_id.id,  # Add the customer ID here
                                    }
                                    account_payment = self.env['account.payment'].sudo().create(payment_vals)
                                    account_payment.sudo().action_post()
                                    lines = self.env['account.move.line'].sudo().search([('name', '=', invoice.name)])
                                    for line in lines:
                                        if amount_total <= 0:
                                            break

                                        if line.amount_residual <= amount_total:
                                            remaining_amount = amount_total - line.amount_residual
                                            # Create partial reconciliation
                                            reconcile_vals = {
                                                'debit_move_id': line.id,
                                                'credit_move_id': account_payment.move_id.line_ids.filtered(lambda l: l.credit > 0).id,
                                                'amount': line.amount_residual,
                                                'debit_amount_currency': line.amount_residual,
                                                'credit_amount_currency': line.amount_residual,
                                            }
                                            self.env['account.partial.reconcile'].sudo().create(reconcile_vals)
                                            line.sudo().write({
                                                'reconciled': True,
                                                'amount_residual': 0,
                                                'amount_residual_currency': 0,
                                            })
                                            amount_total = remaining_amount
                                        else:
                                            balanced_amount = line.amount_residual - amount_total
                                            # Create partial reconciliation
                                            reconcile_vals = {
                                                'debit_move_id': line.id,
                                                'credit_move_id': account_payment.move_id.line_ids.filtered(lambda l: l.credit > 0).id,
                                                'amount': amount_total,
                                                'debit_amount_currency': amount_total,
                                                'credit_amount_currency': amount_total,
                                            }
                                            self.env['account.partial.reconcile'].sudo().create(reconcile_vals)
                                            line.sudo().write({
                                                'amount_residual': balanced_amount,
                                                'amount_residual_currency': balanced_amount,
                                            })
                                            amount_total = 0

                        except Exception as e:

                            custoemr_queue_data= self.env['common.log.lines.ept'].create({
                            'order_ref': e,
                            "shopify_instance_id": self.shopify_instance_id.id,
                            "message":e
                        })    

                else:
                    custoemr_queue_data= self.env['common.log.lines.ept'].create({
                            'order_ref': e,
                            "shopify_instance_id": self.shopify_instance_id.id,
                            "message":e
                        })
                    
            except Exception as e:
                custoemr_queue_data= self.env['common.log.lines.ept'].create({
                            'order_ref': e,
                            "shopify_instance_id": self.shopify_instance_id.id,
                            "message":e
                        })



    def update_order_status(self):
        url = self.shopify_instance_id.shopify_host
        domain = urlparse(url).netloc
        SHOP_URL = f"https://{self.shopify_instance_id.shopify_api_key}:{self.shopify_instance_id.shopify_password}@{domain}"
        access_token = self.shopify_instance_id.shopify_password
        sale_orders = self.env["sale.order"].search([("updated_in_shopify", "=", False)])
        
        order_id_list = []
        unpaid_invoice = True
        for sale in sale_orders:
            if len(sale.invoice_ids) == 1:
                if not sale.invoice_ids[0].amount_residual :
                    sale.updated_in_shopify = True
                    order_id_list.append({sale.shopify_order_id: sale.invoice_ids[0].amount_total})
                    # print("invoice data ", sale.invoice_ids[0].read())
            else:
                for invoice in sale.invoice_ids:
                    # print("invoice data ", invoice.read())
                    if invoice.amount_residual:
                        unpaid_invoice = False
                        break
                    
                if unpaid_invoice:
                    sale.updated_in_shopify = True
                    order_id_list.append({sale.shopify_order_id: sale.invoice_ids[0].amount_total})
                    
        
        for order in order_id_list:
            for order_id, amount in order.items():
                # print("order id", order_id, "Amount ", amount)
                
                url = self.shopify_instance_id.shopify_host
                domain = urlparse(url).netloc
                
                payment_endpoint = f'/admin/api/2024-10/orders/{order_id}/transactions.json'
                payment_url = f'{SHOP_URL}{payment_endpoint}'
                
                headers = {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'X-Shopify-Access-Token': access_token
                }

                payment_data = {
                    "transaction": {
                        "kind": "capture",
                        "status": "success",
                        "amount": amount # Set this to the amount that needs to be marked as paid
                    }
                }

                # Make the POST request to create the payment
                payment_response = requests.post(payment_url, headers=headers, data=json.dumps(payment_data))

            # Check the response for payment creation
            if payment_response.status_code == 201:
                print(f"Payment for order {order_id} successfully created.")
            else:
                print(f"Error creating payment: {payment_response.status_code} - {payment_response.text}")

    def import_stock(self):

        url = self.shopify_instance_id.shopify_host
        domain = urlparse(url).netloc

        SHOP_URL = f"https://{self.shopify_instance_id.shopify_api_key}:{self.shopify_instance_id.shopify_password}@{domain}/admin"
        shopify.ShopifyResource.set_site(SHOP_URL)
        location_record = self.env['shopify.location.ept'].search([("instance_id","=",self.shopify_instance_id.id)])
        for location in location_record:
            inventory_levels = shopify.InventoryLevel.find(location_ids=location.shopify_location_id)
            for inventory in inventory_levels:
                product_id = self.env['product.product'].search([('inventory_item_id', '=',inventory.to_dict()["inventory_item_id"])], limit=1)
                qty_data=inventory.to_dict()["available"]

                if product_id:

                    stock_line = self.env['stock.quant'].search([('product_id', '=',product_id.id)])
                    if stock_line:
                        for qty in stock_line:
                            if qty.location_id.id == product_id.property_stock_inventory.id :
                                
                                quantity= f"-{qty_data}"
                                qty.write({"quantity":quantity})
                            else:
                                qty.write({"quantity":inventory.to_dict()["available"]})

                    else:
                        wh_stock_location = self.env['stock.location'].search([('name', 'in',['Stock','Inventory adjustment'])])
                        
                        # To check the results
                        if wh_stock_location:
                            for location in wh_stock_location:
                                   
                                if location.name == "Stock":
                                    dataset= self.env['stock.quant'].create({
                                            'product_id': product_id.id,
                                            'location_id': location.id,
                                            'quantity': qty_data,
                                            'company_id':wh_stock_location.company_id.id
                                        })
                                else:
                                    quantity= f"-{qty_data}"
                                    dataset= self.env['stock.quant'].create({
                                            'product_id': product_id.id,
                                            'location_id': location.id,
                                            'quantity': quantity,
                                            'company_id':wh_stock_location.company_id.id
                                        })


    def export_stock(self):
        try:
            print("...............",self.export_stock_from)
            shopify_location_record = self.env['shopify.location.ept'].search([("instance_id","=",self.shopify_instance_id.id)])
            for locations in shopify_location_record:

                print("locations............",locations.shopify_location_id)
                url = self.shopify_instance_id.shopify_host
                domain = urlparse(url).netloc

                SHOP_URL = f"https://{self.shopify_instance_id.shopify_api_key}:{self.shopify_instance_id.shopify_password}@{domain}/admin"
                shopify.ShopifyResource.set_site(SHOP_URL)

                try:
                    # Define the inventory details

                    wh_stock_location = self.env['stock.location'].search([('name','=','Stock')])
                    odoo_stock_quant = self.env['stock.quant'].search([("location_id","=",wh_stock_location.id)])
                    for produdct_stock in odoo_stock_quant:
                        print("...............",produdct_stock.product_id.inventory_item_id ,"......",locations.shopify_location_id,".........",produdct_stock.quantity )
                        inventory_item_id = produdct_stock.product_id.inventory_item_id  # Replace with your actual inventory item ID
                        location_id = locations.shopify_location_id # Replace with your actual location ID
                        new_available_quantity = int(produdct_stock.quantity) # Replace with the new quantity
                        shopify.InventoryLevel.set(inventory_item_id=inventory_item_id, location_id=location_id, available=new_available_quantity)

                except Exception as e:
                    print("Error occurred:", e)
            
            return {"message":f"Shopify stock  imported successfully! ", "type": "success","title": "Success!"}
        
        except Exception as e:
            custoemr_queue_data= self.env['common.log.lines.ept'].create({
                            'order_ref': e,
                            "shopify_instance_id": self.shopify_instance_id.id,
                            "message":e
                        })
            return {"message":f"Shopify stock not imported successfully due to {e} ", "type": "danger","title": "Error!"}  

    def import_location(self):
        try: 
            url = self.shopify_instance_id.shopify_host
            domain = urlparse(url).netloc

            SHOP_URL = f"https://{self.shopify_instance_id.shopify_api_key}:{self.shopify_instance_id.shopify_password}@{domain}/admin"
            shopify.ShopifyResource.set_site(SHOP_URL)
            locations = shopify.Location.find()

            for location in locations:
                location_record = self.env['shopify.location.ept'].search([('name', '=', location.name),("instance_id","=",self.shopify_instance_id.id)], limit=1)

                stock_warehouse = self.env['stock.warehouse'].search([('id', '=',1)], limit=1)

                if not location_record:
                    location_record=self.env['shopify.location.ept'].create({
                        'name': location.name,
                        'instance_id':self.shopify_instance_id.id,
                        "active":True,
                        "shopify_location_id": location.id,
                        "export_stock_warehouse_ids":[(6, 0, [stock_warehouse.id])], 
                        "import_stock_warehouse_id":stock_warehouse.id,
                    })

                # stock_location = self.env['stock.location'].search([('shopify_location_id', '=', location.id),("shopify_instance_id","=",self.shopify_instance_id.id)], limit=1)
                # if not stock_location:
                #     stock_location=self.env['stock.location'].create({
                #         'name': location.name,
                #         'shopify_instance_id':self.shopify_instance_id.id,
                #         "shopify_location_id": location.id
                #     }) 
            return {"message":"Shopify location imported successfully!", "type": "success","title": "Success!"}        


        except Exception as e:
            custoemr_queue_data= self.env['common.log.lines.ept'].create({
                            'order_ref': e,
                            "shopify_instance_id": self.shopify_instance_id.id,
                            "message":e
                        })
            return {"message":"Shopify location not imported  successfully Please check log entry.", "type": "danger","title": "Error!"}   


    def import_products_from_csv(self):
        pass

    def import_payout_report(self):
        pass
    
    def sync_product_by_remote_ids(self):
        url = self.shopify_instance_id.shopify_host
        domain = urlparse(url).netloc
        
        SHOP_URL = f"https://{self.shopify_instance_id.shopify_api_key}:{self.shopify_instance_id.shopify_password}@{domain}/admin/api/2024-10"
        shopify.ShopifyResource.set_site(SHOP_URL)
        template_ids = self.shopify_template_ids
        if template_ids:
            shopify_list = []
            for template_id in template_ids.split(","):
                product_id = str(template_id)
                if product_id:
                    product = shopify.Product.find(product_id)
                    shopify_list.append((0, 0, {"product_data_id": str(product.id),"name" : product.title, "shopify_instance_id":self.shopify_instance_id.id, "state" : "draft", "synced_product_data": product.to_dict(), "shopify_image_import_state": "done" if len(product.images) else "pending"}))
                    
            shopify_tmpl_dict = {
                "shopify_instance_id":self.shopify_instance_id.id,
                "state": "draft",
                "product_data_queue_lines" : shopify_list
            }
            self.env["shopify.product.data.queue.ept"].create(shopify_tmpl_dict)   
    
    def shopify_execute(self):
        if self.shopify_operation == "sync_product_by_remote_ids":
            
            self.sync_product_by_remote_ids()
        
        if self.shopify_operation == "sync_product":
            self.sync_product()

        if self.shopify_operation == "import_customers":
            data=self.import_customers()
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': data["title"],
                    'message': data["message"],
                    'type': data["type"],  # 'success', 'warning', 'danger', 'info'
                    'sticky': False,  # Set to True to make the notification persistent
                    'next': {'type': 'ir.actions.act_window_close'},  # Close the wizard after notification
                    }
                }

        if self.shopify_operation == "import_unshipped_orders":
            data=self.import_unshipped_orders()
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': data["title"],
                    'message': data["message"],
                    'type': data["type"],  # 'success', 'warning', 'danger', 'info'
                    'sticky': False,  # Set to True to make the notification persistent
                    'next': {'type': 'ir.actions.act_window_close'},  # Close the wizard after notification
                    }
                }

        if self.shopify_operation == "import_shipped_orders":
            data=self.import_shipped_orders()
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': data["title"],
                    'message': data["message"],
                    'type': data["type"],  # 'success', 'warning', 'danger', 'info'
                    'sticky': False,  # Set to True to make the notification persistent
                    'next': {'type': 'ir.actions.act_window_close'},  # Close the wizard after notification
                    }
                }

        if self.shopify_operation == "import_buy_with_prime_orders":
            self.import_buy_with_prime_orders()

        if self.shopify_operation == "import_cancel_orders":
            self.import_cancel_orders()

        if self.shopify_operation == "import_orders_by_remote_ids":
            self.import_orders_by_remote_ids()

        if self.shopify_operation == "update_order_status":
            self.update_order_status()

        if self.shopify_operation == "import_stock":
            self.import_stock()
            return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Success!',
                        'message': "Import stock successfully!",
                        'type': 'success',  # 'success', 'warning', 'danger', 'info'
                        'sticky': False,  # Set to True to make the notification persistent
                        'next': {'type': 'ir.actions.act_window_close'},  # Close the wizard after notification
                    }
                }

        if self.shopify_operation == "export_stock":
            data=self.export_stock()
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': data["title"],
                    'message': data["message"],
                    'type': data["type"],  # 'success', 'warning', 'danger', 'info'
                    'sticky': False,  # Set to True to make the notification persistent
                    'next': {'type': 'ir.actions.act_window_close'},  # Close the wizard after notification
                    }
                }

        if self.shopify_operation == "import_location":
            data=self.import_location()

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': data["title"],
                    'message': data["message"],
                    'type': data["type"],  # 'success', 'warning', 'danger', 'info'
                    'sticky': False,  # Set to True to make the notification persistent
                    'next': {'type': 'ir.actions.act_window_close'},  # Close the wizard after notification
                    }
                }

        if self.shopify_operation == "import_products_from_csv":
            self.import_products_from_csv()

        if self.shopify_operation == "import_payout_report":
            self.import_payout_report()
