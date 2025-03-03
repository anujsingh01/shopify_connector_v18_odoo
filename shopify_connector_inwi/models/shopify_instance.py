from odoo import models, fields, api
import shopify
from urllib.parse import urlparse
from datetime import datetime, timedelta
import ast
import uuid 

class ShopifyInstanceEpt(models.Model):
    _name = "shopify.instance.ept"
    _description = "Shopify Instance Configuration"

    name = fields.Char(string="Name", required=True)
    Force_transfer_move_of_buy_with_prime_orders = fields.Boolean()
    add_new_product_order_webhook = fields.Boolean()
    auto_create_product_category = fields.Boolean()
    auto_fulfill_gift_card_order = fields.Boolean()
    auto_import_product  = fields.Boolean()
    auto_import_shipped_order = fields.Boolean()
    create_shopify_customers_webhook = fields.Boolean()
    create_shopify_orders_webhook = fields.Boolean()
    create_shopify_products_webhook = fields.Boolean()
    credit_note_register_payment = fields.Boolean()
    credit_tax_account_id = fields.Many2one("account.account", string="Credit Tax Account")
    
    shopify_host = fields.Char(string="Host")
    shopify_api_key = fields.Char(string="API Key")
    shopify_password = fields.Char(string="Password")
    shopify_shared_secret = fields.Char(string="Secret Key")
    shopify_store_time_zone = fields.Char(string="Store Time Zone")
    
    active = fields.Boolean(string="Active", default=True)
    color = fields.Integer(string="Color Index")
    shopify_company_id = fields.Many2one('res.company', string="Company")
    shopify_pricelist_id = fields.Many2one('product.pricelist', string="Pricelist")
    shopify_product_uom_id = fields.Many2one('uom.uom', string="Unit of Measure")
    shopify_lang_id = fields.Many2one('res.lang', string="Language")
    shopify_section_id = fields.Many2one('crm.team', string="Sales Team")
    shopify_activity_type_id = fields.Many2one('mail.activity.type', string="Activity Type")
    
    # Date and Time Fields
    create_date = fields.Datetime(string="Created On", readonly=True)
    shopify_last_date_customer_import = fields.Datetime(string="Last Customer Import")
    shopify_last_date_product_import = fields.Datetime(string="Last Product Import")
    shopify_last_date_update_stock = fields.Datetime(string="Last Stock Update")
    
    # Boolean Fields
    is_shopify_digest = fields.Boolean(string="Set Shopify Digest?")
    apply_tax_in_order = fields.Selection(
        [('odoo_tax', 'Odoo Default Tax Behaviour'), ('create_shopify_tax', 'Create new tax If Not Found')],
        string="Apply Tax In Order"
    )
    
    # Many2one Relationships
    credit_note_payment_journal = fields.Many2one('account.journal', string="Credit Note Payment Journal")
    shopify_analytic_account_id = fields.Many2one('account.analytic.account', string="Analytic Account")
    # shopify_api_key = fields.Char()
    # shopify_company_id = fields.Many2one("res.company")
    
    
    # Many2many Relationships
    shopify_order_status_ids = fields.Many2many(
        'import.shopify.order.status', string="Shopify Import Order Status"
    )
    buy_with_prime_tag_ids = fields.Many2many(
        'shopify.tags', string="Tags for Import Buy with Prime Orders"
    )
    product_ids = fields.One2many("shopify.product.template.ept", "shopify_instance_id")
    refund_adjustment_product_id = fields.Many2one("product.product")
    refund_order_webhook = fields.Boolean()
    return_picking_order = fields.Boolean()
    ship_order_webhook = fields.Boolean()
    shipping_product_id = fields.Many2one("product.product")
    shopify_activity_type_id = fields.Many2one("mail.activity.type")
    
    
    # Many2one Relationships for Product Fields
    custom_service_product_id = fields.Many2one('product.product', string="Custom Service Product")
    custom_storable_product_id = fields.Many2one('product.product', string="Custom Storable Product")
    gift_card_product_id = fields.Many2one('product.product', string="Gift Card Product")
    discount_product_id = fields.Many2one('product.product', string="Discount")
    duties_product_id = fields.Many2one('product.product', string="Duties")
    delivery_fee_name = fields.Char()
    forcefully_reserve_stock_webhook = fields.Boolean()
    import_buy_with_prime_shopify_order = fields.Boolean()
    import_customer_as_company = fields.Boolean()
    import_order_after_date = fields.Datetime()
    invoice_tax_account_id = fields.Many2one("account.account")
    is_delivery_fee = fields.Boolean()
    is_delivery_multi_warehouse = fields.Boolean()
    is_instance_create_from_onboarding_panel = fields.Boolean()
    is_shopify_create_schedule = fields.Boolean()
    last_buy_with_prime_order_import_date = fields.Datetime()
    last_cancel_order_import_date = fields.Datetime()
    last_date_order_import = fields.Datetime()
    last_shipped_order_import_date = fields.Datetime()
    order_visible_currency = fields.Boolean()
    payout_last_import_date = fields.Date()
    
    
    # Additional Customizations
    notify_customer = fields.Boolean(string="Notify Customer about Update Order Status?")
    is_use_default_sequence = fields.Boolean(string="Use Odoo Default Sequence?")
    is_onboarding_configurations_done = fields.Boolean(string="Is Onboarding Configurations Done")
    
    
    shopify_compare_pricelist_id = fields.Many2one(
        comodel_name='product.pricelist', 
        string='Compare At Pricelist'
    )
    shopify_date_deadline = fields.Integer(
        string='Deadline Lead Days'
    )
    shopify_default_pos_customer_id = fields.Many2one(
        comodel_name='res.partner', 
        string='Default POS Customer'
    )
    shopify_host = fields.Char(
        string='Host'
    )
    shopify_instance_product_category = fields.Many2one(
        comodel_name='product.category', 
        string='Default Product Category'
    )
    shopify_is_use_analytic_account = fields.Boolean(
        string='Shopify Is Use Analytic Account'
    )
    shopify_lang_id = fields.Many2one(
        comodel_name='res.lang', 
        string='Language'
    )
    shopify_last_date_customer_import = fields.Datetime(
        string='Last Customer Import'
    )
    shopify_last_date_product_import = fields.Datetime(
        string='Last Product Import'
    )
    shopify_last_date_update_stock = fields.Datetime(
        string='Last Stock Update'
    )
    shopify_order_data = fields.Text(
        string='Shopify Order Data'
    )
    shopify_order_prefix = fields.Char(
        string='Order Prefix'
    )
    shopify_order_status_ids = fields.Many2many(
        comodel_name='import.shopify.order.status', 
        string='Shopify Import Order Status'
    )
    shopify_password = fields.Char(
        string='Password'
    )
    shopify_pricelist_id = fields.Many2one(
        comodel_name='product.pricelist', 
        string='Pricelist'
    )
    shopify_product_uom_id = fields.Many2one(
        comodel_name='uom.uom', 
        string='Unit of Measure'
    )
    shopify_section_id = fields.Many2one(
        comodel_name='crm.team', 
        string='Sales Team'
    )
    shopify_settlement_report_journal_id = fields.Many2one(
        comodel_name='account.journal', 
        string='Payout Report Journal'
    )
    shopify_shared_secret = fields.Char(
        string='Secret Key'
    )
    shopify_stock_field = fields.Many2one(
        comodel_name='ir.model.fields', 
        string='Stock Field'
    )
    shopify_store_time_zone = fields.Char(
        string='Store Time Zone'
    )
    shopify_sync_product_with = fields.Selection(
        selection=[('sku', 'Internal Reference(SKU)'), ('barcode', 'Barcode'),('sku_or_barcode', 'Internal Reference or Barcode')],
        string='Sync Product With'
    )
    shopify_user_ids = fields.Many2many(
    comodel_name='res.users',
    string='Responsible User'
    )

    shopify_warehouse_id = fields.Many2one(
        comodel_name='stock.warehouse',
        string='Warehouse'
    )

    stock_validate_for_return = fields.Boolean(
        string='Want to Validate Return Picking'
    )

    sync_product_with_images = fields.Boolean(
        string='Sync Images?'
    )

    tip_product_id = fields.Many2one(
        comodel_name='product.product',
        string='Tip'
    )

    transaction_line_ids = fields.One2many(comodel_name='shopify.payout.account.config.ept', inverse_name='shopify_instance_id', string='Transaction Line')

    update_category_in_odoo_product = fields.Boolean(
        string='Update Category in Odoo Product?'
    )

    update_qty_order_webhook = fields.Boolean(
        string='Want to Update Quantity?'
    )

    update_qty_to_invoice_order_webhook = fields.Boolean(
        string='Want Changes to Invoice as per Update Quantity?'
    )

    webhook_ids = fields.One2many(
        comodel_name='shopify.webhook.ept',
        inverse_name='shopify_instance_id',
        string='Webhooks'
    )
    
    def shopify_test_connection(self):
        url = self.shopify_host
        domain = urlparse(url).netloc

        SHOP_URL = f"https://{self.shopify_api_key}:{self.shopify_password}@{domain}/admin"
        shopify.ShopifyResource.set_site(SHOP_URL)
        try:
            shop = shopify.Shop.current()
            if shop.to_dict():
                print("Connection successful!")
                SHOP_URL = f"{SHOP_URL}/api/2024-10"
                shopify.ShopifyResource.set_site(SHOP_URL)
                try:
                    # Fetch list of locations
                    locations = shopify.Location.find()
                    for location in locations:

                        location_record = self.env['shopify.location.ept'].search([('name', '=', location.name),("instance_id","=",self.id)], limit=1)
                        print("location_record....",location_record)
                        stock_warehouse = self.env['stock.warehouse'].search([('id', '=',1)], limit=1)
                        print("stock_warehouse....",stock_warehouse)

                        if not location_record:
                            location_record=self.env['shopify.location.ept'].create({
                                'name': location.name,
                                'instance_id':self.id,
                                "active":True,
                                "shopify_location_id": location.id,
                                "export_stock_warehouse_ids":[(6, 0, [stock_warehouse.id])], #[(6, 0, [stock_warehouse.id])]
                                "import_stock_warehouse_id":stock_warehouse.id,
                            })

                        # add location data in database from hear...
                    message= f'Shopify {shop.to_dict()["name"]} connected successfully!',

                except Exception as e:
                    message= f'Shopify {shop.to_dict()["name"]} connected successfully but location not found !',
                
                ############  check Auto Workflow ##########################

                try:
                    sales_journal = self.env['account.journal'].search([('type', '=', 'sale')], limit=1)
                    if not sales_journal:
                        return {
                            'type': 'ir.actions.client',
                            'tag': 'display_notification',
                            'params': {
                                'title': 'Error!',
                                'message': 'No sales journal found. Please configure a sales journal first.',
                                'type': 'danger',
                                'sticky': False,
                            }
                        }
                except Exception as e:
                    pass      

                try:
                    # Check for existing workflow process entry
                    existing_record = self.env['sale.workflow.process.ept'].search([('name', '=', 'Automatic Validation')], limit=1)
                    if not existing_record:
                        existing_record= self.env['sale.workflow.process.ept'].create({
                            'name': 'Automatic Validation',
                            'sale_journal_id': sales_journal.id,
                            'picking_policy': 'one',
                        })
                        message= f'Shopify {shop.to_dict()["name"]} connected successfully!',
                
                except Exception as e:
                    pass 
                   
                ################################ check payment gateways ############################## 
                try:
                    # Check for existing workflow process entry
                    payment_record = self.env['shopify.payment.gateway.ept'].search([('name', '=', 'manual'),("shopify_instance_id","=",self.id)], limit=1)
                    if not payment_record:
                        payment_record=self.env['shopify.payment.gateway.ept'].create({
                            'name': 'manual',
                            'code':"manual",
                            'shopify_instance_id': self.id,
                            "active":True

                        })

                except Exception as e:
                    pass
                   
                ########################################  sale.auto.workflow.configuration.ept    #############################################

                try:
                    # Check for existing workflow process entry
                    workflow_confg = self.env['sale.auto.workflow.configuration.ept'].search([('payment_gateway_id', '=', payment_record.id),("shopify_instance_id","=",self.id)], limit=1)
                    shopify_order_status = self.env['import.shopify.order.status'].search([('name', '=', "Unshipped")], limit=1)
                    if not shopify_order_status:
                            shopify_order_status=self.env['import.shopify.order.status'].create({
                                'name': "Unshipped",
                                "status":"True",
                            })
                            
                    if not workflow_confg:
                        self.env['sale.auto.workflow.configuration.ept'].create({
                            'payment_gateway_id': payment_record.id,
                            'shopify_instance_id': self.id,
                            "active":True,
                            "auto_workflow_id":existing_record.id,
                            "financial_status": 'paid',
                            "payment_term_id": 1,
                            "shopify_order_payment_status":shopify_order_status.id

                        })

                except Exception as e:
                    print(".........",e)

                #####################################################################################

                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Success!',
                        'message': message,
                        'type': 'success',  # 'success', 'warning', 'danger', 'info'
                        'sticky': False,  # Set to True to make the notification persistent
                    }
                }
            else:

                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Warning!',
                        'message': 'Connection unsuccessful. Please check your details.',
                        'type': 'warning',
                        'sticky': False,
                    }
                }
            
        except Exception as e:

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Error!',
                    'message': f'Error occurred: {e}',
                    'type': 'danger',
                    'sticky': False,
                }
            }


    def open_reset_credentials_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Reset Credentials',
            'res_model': 'reset.credentials',
            'view_mode': 'form',
            'target': 'new',  # Ensures the popup behavior
            'context': {
                'default_instance_id': self.id,  # Pass the current instance ID
            },
        }
    
    def cron_configuration_action(self):
        """Open Shopify Scheduled Action form with existing record if available, else create new."""
        self.ensure_one()  # Ensure only one record is processed at a time
        existing_record = self.env['shopify.scheduled.action'].search([('instance_id', '=', self.id)], limit=1)

        return {
            'type': 'ir.actions.act_window',
            'name': 'Shopify Scheduled Action',
            'res_model': 'shopify.scheduled.action',
            'view_mode': 'form',
            'res_id': existing_record.id if existing_record else False,  # Open existing or create new
            'target': 'new',  # Open as popup
            'context': {
                'default_instance_id': self.id,  # Pass instance ID
            },
        }

    
    def action_redirect_to_ir_cron(self):
        pass
    
    def action_shopify_active_archive_instance(self):
        pass
    
    def refresh_webhooks(self):
        pass

    # def get_active_instances(self, period="all",instanceId=None):  
    #     print("period........",period,instanceId)
    #     instance_update = self.env['shopify.instance.ept'].sudo().search_read([("active", "=", True)])

    #     today = datetime.today()
    #     start_date = None
    #     if period == "week":
    #         start_date = today - timedelta(days=today.weekday())  # Start of current week
    #         print("start_date........",start_date)

    #     elif period == "month":
    #         start_date = today.replace(day=1)  # Start of current month
    #         print("start_date........",start_date)

    #     elif period == "year":
    #         start_date = today.replace(month=1, day=1)  # Start of current year
    #         print("start_date........",start_date)

    #     elif period == "today":
    #         start_date = today  # Start of current year
    #         print("start_date........",start_date)    

    #     for data_adition in instance_update:
    #         data_adition["product_template_count"] = self.env['product.template'].sudo().search_count([("shopify_instance_id", "=", data_adition["id"])])
    #         data_adition["sale_order_count"] = self.env['sale.order'].sudo().search_count([("shopify_instance_id", "=", data_adition["id"])])
    #         data_adition["customer_count"] = self.env['res.partner'].sudo().search_count([("shopify_instance_id", "=", data_adition["id"])])

    #         domain = [("shopify_instance_id", "=", data_adition["id"])]
    #         if start_date:
    #             domain.append(("date_order", ">=", start_date.strftime("%Y-%m-%d")))

    #         sales_orders = self.env['sale.order'].sudo().search(domain)
    #         print("sales_orders......",sales_orders)
    #         if sales_orders:
    #             currency= sales_orders[0]["currency_id"].symbol
    #         else:
    #             currency='' 
            
    #         # Prepare sales data
    #         sales_data = {
    #             "dates": [order.date_order.strftime("%d-%m") for order in sales_orders],
    #             "values": [order.amount_total for order in sales_orders]
    #         }

    #         SaleOrder = self.env['sale.order'].sudo()

    #         # Aggregate sum and average of total_amount field
    #         result = SaleOrder.read_group(
    #             domain=[("shopify_instance_id", "=", data_adition["id"])],  # Filter condition
    #             fields=["amount_total:sum"],  # Sum and Average computation
    #             groupby=[]
    #         )
            
    #         # # Extract values from result
    #         total_sales = result[0].get("amount_total", 0.0)  # Sum of total_amount  
    #         if total_sales == False:
    #             total_sales=0

    #         if result:
    #             amount_total=result[0].get("amount_total",0.0)
    #             __count=result[0].get("__count",0.0)

    #             if amount_total != False:
    #                 average_sales_order=amount_total / __count
    #             else:
    #                 average_sales_order=0.0

    #         data_adition["sales_data"] = sales_data
    #         data_adition["total_sales"] = total_sales
    #         data_adition["currency"] = currency  
    #         data_adition["average_sales_orders"] = average_sales_order  

    #     return instance_update if instance_update else None

    


    def get_active_instances(self, instancesData=[]):  

        instance_update = self.env['shopify.instance.ept'].sudo().search_read([("active", "=", True)])
        if not instance_update:
            instance_update=[]
            return instance_update

        for data_adition in instance_update:
            start_date = None
            if instancesData :
                period = get_period(instancesData, data_adition)
                if period:
                    today = fields.Date.today()
                    if period == "week":
                        start_date = today - timedelta(days=today.weekday())  # Start of current week
                    elif period == "month":
                        start_date = today.replace(day=1)  # Start of current month
                    elif period == "year":
                        start_date = today.replace(month=1, day=1)  # Start of current year
                    elif period == "today":
                        start_date = today  # Today's date

                    

            data_adition["product_template_count"] = self.env['product.template'].sudo().search_count([
                ("shopify_instance_id", "=", data_adition["id"])
            ])
            data_adition["sale_order_count"] = self.env['sale.order'].sudo().search_count([
                ("shopify_instance_id", "=", data_adition["id"])
            ])
            data_adition["customer_count"] = self.env['res.partner'].sudo().search_count([
                ("shopify_instance_id", "=", data_adition["id"])
            ])

            # Create a domain filter
            domain = [("shopify_instance_id", "=", data_adition["id"])]
            if start_date:
                    domain.append(("date_order", ">=", start_date))
            sales_orders = self.env['sale.order'].sudo().search(domain)
            # print("sales_orders.............",sales_orders)

            # Get currency symbol if sales_orders exist
            currency = sales_orders[0].currency_id.symbol if sales_orders else ''

            # Prepare sales data
            sales_data = {
                "dates": [order.date_order.strftime("%d-%m") for order in sales_orders],
                "values": [order.amount_total for order in sales_orders]
            }
            # print("sales_data...........",sales_data)

            SaleOrder = self.env['sale.order'].sudo()

            # Aggregate sum and count of total_amount field
            result = SaleOrder.read_group(
                domain=domain,  # Use domain with date filter
                fields=["amount_total:sum"],
                groupby=[]
            )
            # Extract total sales
            total_sales = result[0].get("amount_total", 0.0) if result else 0.0
            if total_sales == False:
                total_sales=0


            # Calculate average sales order
            order_count = result[0].get("__count", 1) if result else 1  # Avoid division by zero
            average_sales_order = total_sales / order_count if order_count else 0.0

            # Store computed values
            data_adition["sales_data"] = sales_data
            data_adition["total_sales"] = total_sales
            data_adition["currency"] = currency  
            data_adition["average_sales_orders"] = average_sales_order  

        return instance_update if instance_update else []
    
def get_period(instances, data):
        for instance in instances:
            if instance['id'] == data['id']:
                return instance['period']
        return None


class ResetCredentials(models.Model):
    _name = 'reset.credentials'
    _description = 'Reset Credentials'
    
    instance_id = fields.Many2one('shopify.instance.ept', string='Shopify Instance', required=True)
    host = fields.Char(string='Host', required=True)
    api_key = fields.Char(string='API Key', required=True)
    access_token = fields.Char(string='Access Token', required=True)
    secret_key = fields.Char(string='Secret Key', required=True)


    @api.model
    def default_get(self, fields):
        res = super(ResetCredentials, self).default_get(fields)
        if self.env.context.get('default_instance_id'):
            res['instance_id'] = self.env.context['default_instance_id']
        return res

    def action_test_connection(self):

        url = self.host
        domain = urlparse(url).netloc
        print(self.host,self.api_key, self.access_token , self.secret_key)
        try:

            SHOP_URL = f"https://{self.api_key}:{self.access_token}@{domain}/admin"
            shopify.ShopifyResource.set_site(SHOP_URL)
            shop = shopify.Shop.current()
            if shop.to_dict():
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Success!',
                        'message': 'Connection tested successfully!',
                        'type': 'success',
                        'sticky': False,
                    }
                }
            else:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Error!',
                        'message': 'Data is invalid !',
                        'type': 'danger',
                        'sticky': False,
                        }
                    }
        except Exception as e:
            return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Error!',
                        'message': 'Data is invalid !',
                        'type': 'danger',
                        'sticky': False,
                        }
                    }


    def action_save_credentials(self):
        # Ensure the instance_id is set
        if not self.instance_id:
            raise ValueError("No Shopify Instance ID found.")

        # Access the instance and save credentials
        instance = self.instance_id.id

        instance_update = self.env['shopify.instance.ept'].sudo().search([('id', '=', instance)])
        if instance_update:
            # # Update fields for the found product(s)
            instance_update.write({
                'shopify_host': self.host,  # Replace with the actual field name and the new value you want to set
                "shopify_api_key":self.api_key,
                "shopify_password":self.access_token,
                "shopify_shared_secret": self.secret_key
            })
            print("update successfully!")


        return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Success!',
                    'message': 'Data updated successfully!',
                    'type': 'success',
                    'sticky': False,  # Set to True to make the notification persistent
                    'next': {'type': 'ir.actions.act_window_close'},  # Close the wizard after notification
                    }
                }


class ShopifyScheduledAction(models.Model):
    _name = 'shopify.scheduled.action'
    _description = 'Scheduled Actions for Shopify Integration'

    name = fields.Char(string="Name")
    # Order Information
    instance_id = fields.Many2one('shopify.instance.ept', string='Shopify Instance', required=True)

    import_order = fields.Boolean(string="Import Order")
    import_order_interval_type = fields.Selection([
        ('minutes', 'Minutes'), ('hours', 'Hours'), ('days', 'Days'),
        ('weeks', 'Weeks'), ('months', 'Months')
    ], string="Interval Type")
    import_order_number = fields.Integer(string="Interval Number", default=0)
    import_order_next_execution = fields.Datetime(string="Next Execution Date")
    import_order_assigned_user = fields.Many2one('res.users', string="Assigned User", default=lambda self: self.env.user)

    import_shipped_order = fields.Boolean(string="Import Shipped Order")
    import_shipped_order_interval_type = fields.Selection([
        ('minutes', 'Minutes'), ('hours', 'Hours'), ('days', 'Days'),
        ('weeks', 'Weeks'), ('months', 'Months')
    ], string="Interval Type")
    import_shipped_order_number = fields.Integer(string="Interval Number", default=0)
    import_shipped_order_next_execution = fields.Datetime(string="Next Execution Date")
    import_shipped_order_assigned_user = fields.Many2one('res.users', string="Assigned User", default=lambda self: self.env.user)

    update_order_status = fields.Boolean(string="Update Order Shipping Status")
    update_order_status_interval_type = fields.Selection([
        ('minutes', 'Minutes'), ('hours', 'Hours'), ('days', 'Days'),
        ('weeks', 'Weeks'), ('months', 'Months')
    ], string="Interval Type")
    update_order_status_number = fields.Integer(string="Interval Number", default=0)
    update_order_status_next_execution = fields.Datetime(string="Next Execution Date")
    update_order_status_assigned_user = fields.Many2one('res.users', string="Assigned User", default=lambda self: self.env.user)

    import_cancel_order = fields.Boolean(string="Import Cancel Order")
    import_cancel_order_interval_type = fields.Selection([
        ('minutes', 'Minutes'), ('hours', 'Hours'), ('days', 'Days'),
        ('weeks', 'Weeks'), ('months', 'Months')
    ], string="Interval Type")
    import_cancel_order_number = fields.Integer(string="Interval Number", default=0)
    import_cancel_order_next_execution = fields.Datetime(string="Next Execution Date")
    import_cancel_order_assigned_user = fields.Many2one('res.users', string="Assigned User", default=lambda self: self.env.user)

    import_buy_prime_order = fields.Boolean(string="Import Buy with Prime Order")
    import_buy_prime_order_interval_type = fields.Selection([
        ('minutes', 'Minutes'), ('hours', 'Hours'), ('days', 'Days'),
        ('weeks', 'Weeks'), ('months', 'Months')
    ], string="Interval Type")
    import_buy_prime_order_number = fields.Integer(string="Interval Number", default=0)
    import_buy_prime_order_next_execution = fields.Datetime(string="Next Execution Date")
    import_buy_prime_order_assigned_user = fields.Many2one('res.users', string="Assigned User", default=lambda self: self.env.user)

    # Stock Information
    export_stock = fields.Boolean(string="Export Stock")
    export_stock_interval_type = fields.Selection([
        ('minutes', 'Minutes'), ('hours', 'Hours'), ('days', 'Days'),
        ('weeks', 'Weeks'), ('months', 'Months')
    ], string="Interval Type")
    export_stock_number = fields.Integer(string="Interval Number", default=0)
    export_stock_next_execution = fields.Datetime(string="Next Execution Date")
    export_stock_assigned_user = fields.Many2one('res.users', string="Assigned User", default=lambda self: self.env.user)

    # Payout Report Information
    import_payout_report = fields.Boolean(string="Auto Import Payout Report")
    import_payout_report_interval_type = fields.Selection([
        ('minutes', 'Minutes'), ('hours', 'Hours'), ('days', 'Days'),
        ('weeks', 'Weeks'), ('months', 'Months')
    ], string="Interval Type")
    import_payout_report_number = fields.Integer(string="Interval Number", default=0)
    import_payout_report_next_execution = fields.Datetime(string="Next Execution Date")
    import_payout_report_assigned_user = fields.Many2one('res.users', string="Assigned User", default=lambda self: self.env.user)

    process_bank_statement = fields.Boolean(string="Auto Process Bank Statement")
    process_bank_statement_interval_type = fields.Selection([
        ('minutes', 'Minutes'), ('hours', 'Hours'), ('days', 'Days'),
        ('weeks', 'Weeks'), ('months', 'Months')
    ], string="Interval Type")
    process_bank_statement_number = fields.Integer(string="Interval Number", default=0)
    process_bank_statement_next_execution = fields.Datetime(string="Next Execution Date")
    process_bank_statement_assigned_user = fields.Many2one('res.users', string="Assigned User", default=lambda self: self.env.user)

    # Product Information
    import_product = fields.Boolean(string="Import Product")
    import_product_interval_type = fields.Selection([
        ('minutes', 'Minutes'), ('hours', 'Hours'), ('days', 'Days'),
        ('weeks', 'Weeks'), ('months', 'Months')
    ], string="Interval Type")
    import_product_number = fields.Integer(string="Interval Number", default=0)
    import_product_next_execution = fields.Datetime(string="Next Execution Date")
    import_product_assigned_user = fields.Many2one('res.users', string="Assigned User", default=lambda self: self.env.user)

    cron_id = fields.Many2one('ir.cron', string="Cron Job")  # Store related cron job

    @api.model
    def default_get(self, fields_list):
        """Pre-fill instance_id when opening form."""
        defaults = super().default_get(fields_list)
        context = self.env.context
        if 'default_instance_id' in context:
            defaults['instance_id'] = context['default_instance_id']

        return defaults

    @api.model_create_multi
    def create(self, vals_list):
        """Ensure only one record per instance_id and create/update cron."""
        context = self.env.context

        for vals in vals_list:
            if 'instance_id' not in vals:
                vals['instance_id'] = context.get('default_instance_id')  # Add instance_id if missing

            instance_id = vals.get('instance_id')
            existing_record = self.search([('instance_id', '=', instance_id)], limit=1)

            if existing_record:
                print("Updating existing record for instance_id:", instance_id)
                existing_record.write(vals)
                existing_record._update_or_create_cron()  # Ensure cron is updated
                return existing_record  # Return updated record instead of creating a new one
            
        record = super().create(vals_list)
        record._update_or_create_cron()  # Ensure cron is created
        return record
    
    def write(self, vals):
        """Ensure cron is updated when modifying scheduled actions."""
        result = super().write(vals)
        for record in self:
            record._update_or_create_cron()  # Ensure cron updates when settings change   
        return result
    
    def _update_or_create_cron(self):
        """Create or update cron jobs for scheduled Shopify tasks and delete deactivated duplicates."""

        cron_env = self.env['ir.cron']
        cron_tasks = [
            ('import_order', 'Import Orders', 'import_order_next_execution', 'import_order_interval_type', 'import_order_number', 'run_import_order'),
            ('import_shipped_order', 'Import Shipped Orders', 'import_shipped_order_next_execution', 'import_shipped_order_interval_type', 'import_shipped_order_number', 'run_import_shipped_order'),
            ('update_order_status', 'Update Order Status', 'update_order_status_next_execution', 'update_order_status_interval_type', 'update_order_status_number', 'run_update_order_status'),
            ('import_cancel_order', 'Import cancel Order', 'import_cancel_order_next_execution', 'import_cancel_order_interval_type', 'import_cancel_order_number', 'run_import_cancel_order'),
            # ('import_buy_prime_order', 'Import buy prime Order', 'import_buy_prime_order_next_execution', 'import_buy_prime_order_interval_type', 'import_buy_prime_order_number', 'run_import_buy_prime_order'),

            ('export_stock', 'Export stock', 'export_stock_next_execution', 'export_stock_interval_type', 'export_stock_number', 'run_export_stock_number'),
            # ('import_payout_report', 'Import payout report', 'import_payout_report_next_execution', 'import_payout_report_interval_type', 'import_payout_report_number', 'run_import_payout_report'),
            # ('process_bank_statement', 'process abnk statement', 'process_bank_statement_next_execution', 'process_bank_statement_interval_type', 'process_bank_statement_number', 'run_process_bank_statement_number'),
            ('import_product', 'Import product', 'import_product_next_execution', 'import_product_interval_type', 'import_product_number', 'run_import_product'),
        ]

        for field, name, next_exec_field, interval_type_field, interval_number_field, method_name in cron_tasks:
            cron_name = f"Shopify {name} - Instance {self.instance_id.id}"

            # Find all crons with the same name 
            existing_crons = cron_env.search([
                ('name', '=', cron_name),
                ('model_id', '=', self.env.ref('shopify_connector_inwi.model_shopify_scheduled_action').id)
            ])

            cron_values = {
                'name': cron_name,
                'model_id': self.env.ref('shopify_connector_inwi.model_shopify_scheduled_action').id,
                'state': 'code',
                'code': f"model.{method_name}()",
                'user_id': self.env.user.id,
                'interval_number': getattr(self, interval_number_field),
                'interval_type': getattr(self, interval_type_field),
                'active': getattr(self, field),  # Activate or deactivate cron
                'numbercall': 0,  # Repeat indefinitely
                # 'doall': True,  # Execute missed jobs

            }

            if existing_crons:
                active_cron = existing_crons.filtered(lambda c: c.active)
                inactive_crons = existing_crons.filtered(lambda c: not c.active)

                if active_cron:
                    # Update only the first active cron found
                    active_cron[0].write(cron_values)
                else:
                    # If no active cron exists, activate the first found cron and update it
                    existing_crons[0].write(cron_values)

                # Delete all inactive duplicate crons
                if inactive_crons:
                    inactive_crons.unlink()
            else:
                # Create a new cron only if none exist
                cron_env.create(cron_values)



    # .................................   Import order cron job sheduling  ......................

    @api.model
    def run_import_order(self):
        """Cron job function to run Import Order"""
        tasks = self.search([('import_order', '=', True)])
        for task in tasks:
            task._import_order()
            task._update_next_execution('import_order_next_execution', 'import_order_interval_type', 'import_order_number')

    def _import_order(self):
        """Actual logic for importing orders (replace with real Shopify API call)."""
        print(f"Importing Orders for Instance {self.instance_id.name}")     
        dataset=import_order_cron_job(self)


    
    # ......................  Import shipped order  cron job sheduling .........................

    @api.model
    def run_import_shipped_order(self):
        """Cron job function to run Import Shipped Order"""
        tasks = self.search([('import_shipped_order', '=', True)])
        for task in tasks:
            task._import_shipped_order()
            task._update_next_execution('import_shipped_order_next_execution', 'import_shipped_order_interval_type', 'import_shipped_order_number')

    def _import_shipped_order(self):
        """Actual logic for importing shipped orders"""
        print(f"Importing Shipped Orders for Instance {self.instance_id.name}") 
        dataset=import_order_cron_job(self)

    #............................. run update order status cron job sheduling ..........................    

    @api.model
    def run_update_order_status(self):
        """Cron job function to run Import Shipped Order"""
        tasks = self.search([('update_order_status', '=', True)])
        for task in tasks:
            task._update_order_status()
            task._update_next_execution('update_order_status_next_execution', 'update_order_status_interval_type', 'update_order_status_number')

    def _update_order_status(self):
        """Actual logic for importing shipped orders"""
        print(f"Importing update order status for Instance {self.instance_id.name}") 
        dataset=import_order_cron_job(self)

    # ............................  run import cancel status    ....................................  

    @api.model
    def run_import_cancel_order(self):
        """Cron job function to run Import Shipped Order"""
        tasks = self.search([('import_cancel_order', '=', True)])
        for task in tasks:
            task._update_cancel_order()
            task._update_next_execution('import_cancel_order_next_execution', 'import_cancel_order_interval_type', 'import_cancel_order_number')

    def _update_cancel_order(self):
        """Actual logic for importing shipped orders"""
        print(f"Importing cancel order status for Instance {self.instance_id.name}") 
        dataset=import_cancel_orders_cron_job(self)

    #  ............................. import buy prime order .....................

    @api.model
    def run_import_buy_prime_order(self):
        """Cron job function to run Import Shipped Order"""
        tasks = self.search([('import_buy_prime_order', '=', True)])
        for task in tasks:
            task._import_buy_prime_order()
            task._update_next_execution('import_buy_prime_order_next_execution', 'import_buy_prime_order_interval_type', 'import_buy_prime_order_number')

    def _import_buy_prime_order(self):
        """Actual logic for importing shipped orders"""
        print(f"Importing buy prime  order status for Instance {self.instance_id.name}") 

    # ..................................... .Export stock cron job......... .. .......

    @api.model
    def run_export_stock_number(self):
        """Cron job function to run Import Shipped Order"""
        tasks = self.search([('export_stock', '=', True)])
        for task in tasks:
            task._export_stock()
            task._update_next_execution('export_stock_next_execution', 'export_stock_interval_type', 'export_stock_number')

    def _export_stock(self):
        """Actual logic for importing shipped orders"""
        print(f"export stock status for Instance {self.instance_id.name}") 
        try: 
            shopify_location_record = self.env['shopify.location.ept'].search([("instance_id","=",self.instance_id.id)])
            for locations in shopify_location_record:

                print("locations............",locations.shopify_location_id)
                url = self.instance_id.shopify_host
                domain = urlparse(url).netloc

                SHOP_URL = f"https://{self.instance_id.shopify_api_key}:{self.instance_id.shopify_password}@{domain}/admin"
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
                        print("export product stock successfully !")

                except Exception as e:
                    print("Error occurred:", e)
                return {"message":f"Shopify stock  imported successfully! ", "type": "success","title": "Success!"}
        
        except Exception as e:
            custoemr_queue_data= self.env['common.log.lines.ept'].create({
                            'order_ref': e,
                            "shopify_instance_id": self.instance_id.id,
                            "message":e
                        })
            return {"message":f"Shopify stock not imported successfully due to {e} ", "type": "danger","title": "Error!"}  

    # ................................... Import payout report crom job ...........................

    @api.model
    def run_import_payout_report(self):
        """Cron job function to run Import Shipped Order"""
        tasks = self.search([('import_payout_report', '=', True)])
        for task in tasks:
            task._payout_report()
            task._update_next_execution('import_payout_report_next_execution', 'import_payout_report_interval_type', 'import_payout_report_number')

    def _payout_report(self):
        """Actual logic for importing shipped orders"""
        print(f"export payout for Instance {self.instance_id.name}") 

    # ........................run process bank statement number..................................

    @api.model
    def run_process_bank_statement_number(self):
        """Cron job function to run Import Shipped Order"""
        tasks = self.search([('process_bank_statement', '=', True)])
        for task in tasks:
            task._run_process_bank_statement()
            task._update_next_execution('process_bank_statement_next_execution', 'process_bank_statement_interval_type', 'process_bank_statement_number')

    def _run_process_bank_statement(self):
        """Actual logic for importing shipped orders"""
        print(f"import run process bank statement  for Instance {self.instance_id.name}") 

    # ..........................   Import product............................................

    @api.model
    def run_import_product(self):
        """Cron job function to run Import Shipped Order"""
        tasks = self.search([('import_product', '=', True)])
        for task in tasks:
            task._import_product()
            task._update_next_execution('import_product_next_execution', 'import_product_interval_type', 'import_product_number')

    def _import_product(self):
        """Actual logic for importing shipped orders"""
        print(f"import product for Instance {self.instance_id.name}")     
    
    ####################################################################################

    def _update_next_execution(self, next_exec_field, interval_type_field, interval_number_field):
        """Update the next execution date for a scheduled task."""
        if getattr(self, next_exec_field) and getattr(self, interval_type_field) and getattr(self, interval_number_field):
            delta = timedelta(**{getattr(self, interval_type_field): getattr(self, interval_number_field)})
            setattr(self, next_exec_field, datetime.now() + delta)        

    def action_save_credentials(self):
        pass


class ShopifyWebhookEpt(models.Model):
    _name = 'shopify.webhook.ept'
    _description = 'Shopify Webhook'

    
    delivery_url = fields.Text(
        string='Delivery URL'
    )
    
    shopify_instance_id = fields.Many2one(
        comodel_name='shopify.instance.ept',
        string='Shopify Instance',
        help="Webhook created by this Shopify Instance"
    )
    state = fields.Selection(
        selection=[
            ('active', 'Active'),
            ('inactive', 'Inactive')
        ],
        string='State'
    )
    webhook_action = fields.Selection(
        selection=[
        ('products/update', 'When Product is Updated'),
        ('products/create', 'When Product is Created'),
        ('products/delete', 'When Product is Delete'),
        ('orders/updated', 'When Order is Created/Updated'),
        ('customers/create', 'When Customer is Created'),
        ('customers/update', 'When Customer is Updated')],
        string='Webhook Action'
    )
    webhook_id = fields.Char(
        string='Webhook ID in Shopify'
    )
    webhook_name = fields.Char(
        string='Name'
    )
    
    
class ShopifyPayoutAccountConfigEpt(models.Model):
    _name = "shopify.payout.account.config.ept"
    
    name = fields.Char()
    shopify_instance_id = fields.Many2one("shopify.instance.ept")
    account_id = fields.Many2one("account.account")
    transaction_type = fields.Selection([
    ('reserve', 'Reserve'),
    ('adjustment', 'Adjustment'),
    ('credit', 'Credit'),
    ('dispute', 'Dispute'),
    ('debit', 'Debit'),
    ('payout', 'Payout'),
    ('payout_failure', 'Payout Failure'),
    ('payout_cancellation', 'Payout Cancellation'),
    ('fees', 'Fees'),
    ('shopify_collective_debit_reversal', 'Shopify Collective Debit Reversal')
    ], string="Balance Transaction Type")
    
    
class ImportShopifyOrderStatus(models.Model):
    _name = "import.shopify.order.status"         
    
    name = fields.Char()
    status = fields.Char()
    
class SaleWorkflowProcessEpt(models.Model):
    _name = 'sale.workflow.process.ept'
    _description = 'Sale Workflow Process'

    # Fields based on your provided list
    
    create_invoice = fields.Boolean(string="Create & Validate Invoice")
    inbound_payment_method_id = fields.Many2one('account.payment.method', string="Debit Method")
    invoice_date_is_order_date = fields.Boolean(string="Force Accounting Date")
    journal_id = fields.Many2one('account.journal', string="Payment Journal")
    name = fields.Char(string="Name")
    picking_policy = fields.Selection([
        ('direct', 'Deliver each product when available'),
        ('one', 'Deliver all products at once'),
    ], string="Shipping Policy")
    register_payment = fields.Boolean(string="Register Payment")
    sale_journal_id = fields.Many2one('account.journal', string="Sales Journal")
    validate_order = fields.Boolean(string="Confirm Quotation")



class ShopifyPaymentGatewayEpt(models.Model):
    _name = 'shopify.payment.gateway.ept'
    _description = 'Shopify Payment Gateway'

    active = fields.Boolean()
    code = fields.Char()
    name = fields.Char()
    shopify_instance_id = fields.Many2one("shopify.instance.ept", string="Instance")
    
    
class SaleAutoWorkflowConfigurationEpt(models.Model):
    _name = 'sale.auto.workflow.configuration.ept'
    _description = 'Sale Auto Workflow Configuration'

    active = fields.Boolean(string="Active", default=True)
    auto_workflow_id = fields.Many2one('sale.workflow.process.ept', string="Auto Workflow")
    financial_status = fields.Selection([
    ('pending', 'The finances are pending'),
    ('authorized', 'The finances have been authorized'),
    ('partially_paid', 'The finances have been partially paid'),
    ('paid', 'The finances have been paid'),
    ('partially_refunded', 'The finances have been partially refunded'),
    ('refunded', 'The finances have been refunded'),
    ('voided', 'The finances have been voided')
    ]   , string="Financial Status")
    payment_gateway_id = fields.Many2one('shopify.payment.gateway.ept', string="Payment Gateway")
    payment_term_id = fields.Many2one('account.payment.term', string="Payment Term")
    shopify_instance_id = fields.Many2one('shopify.instance.ept', string="Instance")
    shopify_order_payment_status = fields.Many2one('import.shopify.order.status', string="Shopify Order Status")
    

class ShopifyLocationEpt(models.Model):
    _name = 'shopify.location.ept'
    _description = 'Shopify Location'

    active = fields.Boolean(string="Active", default=True)
    export_stock_warehouse_ids = fields.Many2many(
        'stock.warehouse', string="Warehouses"
    )
    import_stock_warehouse_id = fields.Many2one(
        'stock.warehouse', string="Warehouse"
    )
    instance_id = fields.Many2one(
        'shopify.instance.ept', string="Instance"
    )
    is_primary_location = fields.Boolean(string="Is Primary Location")
    legacy = fields.Boolean(string="Is Legacy Location")
    name = fields.Char(string="Name", required=True)
    shopify_instance_company_id = fields.Many2one(
        'res.company', string="Company"
    )
    shopify_location_id = fields.Char(string="Shopify Location")
    warehouse_for_order = fields.Many2one(
        'stock.warehouse', string="Warehouse in Order"
    )


class ShopifySettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # Boolean Fields
    force_transfer_move_of_buy_with_prime_orders = fields.Boolean(string="Force Transfer")
    add_new_product_order_webhook = fields.Boolean(string="Want to Add New Product")
    auto_create_product_category = fields.Boolean(string="Auto Create Product Category?")
    auto_fulfill_gift_card_order = fields.Boolean(string="Automatically fulfill only the gift cards of the order")
    auto_import_product = fields.Boolean(string="Auto Create Product if not found?")
    import_buy_with_prime_shopify_order = fields.Boolean(string="Import Buy with Prime Orders")
    import_customer_as_company = fields.Boolean(string="Import customer as a Company")
    is_delivery_fee = fields.Boolean(string="Are you selling for Colorado State(US)")
    is_delivery_multi_warehouse = fields.Boolean(string="Is Delivery from Multiple warehouse?")
    is_shopify_create_schedule = fields.Boolean(string="Create Schedule activity?")
    is_shopify_digest = fields.Boolean(string="Is Shopify Digest")
    order_visible_currency = fields.Boolean(string="Import order in customer visible currency?")
    refund_order_webhook = fields.Boolean(string="Want to refund order")
    return_picking_order = fields.Boolean(string="Want to return picking")
    ship_order_webhook = fields.Boolean(string="Want to ship order")
    shopify_is_use_analytic_account = fields.Boolean(string="Shopify Is Use Analytic Account")
    shopify_is_use_default_sequence = fields.Boolean(string="Use Odoo Default Sequence in Shopify Orders")
    shopify_notify_customer = fields.Boolean(string="Notify Customer about Update Order Status?")
    shopify_set_sales_description_in_product = fields.Boolean(string="Use Sales Description of Odoo Product for Shopify")
    shopify_sync_product_with_images = fields.Boolean(string="Sync/Import Images?")
    show_net_profit_report = fields.Boolean(string="Show Net Profit Report")
    stock_validate_for_return = fields.Boolean(string="Want to validate return picking")
    update_qty_order_webhook = fields.Boolean(string="Want to update Quantity")
    update_qty_to_invoice_order_webhook = fields.Boolean(string="Want changes to invoice as per update Quantity")
    use_default_terms_and_condition_of_odoo = fields.Boolean(string="Use Default Terms & Condition of Odoo")

    # Many2one Fields
    buy_with_prime_tag_ids = fields.Many2many('shopify.tags', string="Tags for import buy with prime orders")
    buy_with_prime_warehouse_id = fields.Many2one('stock.warehouse', string="Shopify Warehouse for Buy with Prime")
    credit_note_payment_journal = fields.Many2one('account.journal', string="Credit Note Payment Journal")
    shopify_activity_type_id = fields.Many2one('mail.activity.type', string="Shopify Activity Type")
    shopify_analytic_account_id = fields.Many2one('account.analytic.account', string="Shopify Analytic Account")
    shopify_company_id = fields.Many2one('res.company', string="Shopify Instance Company")
    shopify_compare_pricelist_id = fields.Many2one('product.pricelist', string="Compare At Pricelist")
    shopify_credit_tax_account_id = fields.Many2one('account.account', string="Credit Note Tax Account for Shopify Tax")
    shopify_default_pos_customer_id = fields.Many2one('res.partner', string="Default POS Customer")
    shopify_instance_id = fields.Many2one('shopify.instance.ept', string="Shopify Instance")
    shopify_instance_product_category = fields.Many2one('product.category', string="Default Product Category")
    shopify_invoice_tax_account_id = fields.Many2one('account.account', string="Invoice Tax Account For Shopify Tax")
    shopify_lang_id = fields.Many2one('res.lang', string="Shopify Instance Language")
    shopify_pricelist_id = fields.Many2one('product.pricelist', string="Shopify Pricelist")
    shopify_product_uom_id = fields.Many2one('uom.uom', string="Unit of Measure")
    shopify_section_id = fields.Many2one('crm.team', string="Shopify Sales Team")
    shopify_settlement_report_journal_id = fields.Many2one('account.journal', string="Payout Report Journal")
    shopify_stock_field = fields.Many2one('ir.model.fields', string="Stock Field")
    shopify_warehouse_id = fields.Many2one('stock.warehouse', string="Shopify Warehouse")

    # Char Fields
    delivery_fee_name = fields.Char(string="Delivery Fee Name")
    shopify_order_prefix = fields.Char(string="Order Prefix")

    # Selection Fields
    shopify_apply_tax_in_order = fields.Selection(
        [('odoo_tax', 'Odoo Default Tax Behaviour'), ('create_shopify_tax', 'Create New Tax If Not Found')],
        string="Shopify Apply Tax In Order"
    )
    shopify_sync_product_with = fields.Selection(
        [('sku', 'Internal Reference(SKU)'), ('barcode', 'Barcode'), ('sku_or_barcode', 'Internal Reference(SKU) and Barcode')],
        string="Sync Product With"
    )

    # Datetime, Integer, and Date Fields
    shopify_import_order_after_date = fields.Datetime(string="Shopify Import Order After Date")
    shopify_date_deadline = fields.Integer(string="Deadline Lead Days for Shopify")
    shopify_payout_last_date_import = fields.Date(string="Import Payout Reports")
    
    create_shopify_products_webhook = fields.Boolean()
    create_shopify_customers_webhook = fields.Boolean()
    create_shopify_orders_webhook = fields.Boolean()
    forcefully_reserve_stock_webhook = fields.Boolean()
    credit_note_register_payment  = fields.Boolean()
    customer_order_webhook = fields.Boolean()
    shopify_order_status_ids = fields.Many2many("import.shopify.order.status")
    Force_transfer_move_of_buy_with_prime_orders = fields.Boolean()
    shopify_user_ids = fields.Many2many("res.users")


    @api.onchange('shopify_instance_id')
    def _onchange_instance_id(self):
        # if self.shopify_instance_id:
            # print(".........................",self.shopify_instance_id)
            ShopifySettings = self.env['res.config.settings'].search([('shopify_instance_id', '=', self.shopify_instance_id.id)], order='id desc',limit=1)
            print("ShopifySettings....................",ShopifySettings)

            self.shopify_warehouse_id = ShopifySettings.shopify_warehouse_id.id
            self.shopify_lang_id = ShopifySettings.shopify_lang_id.id
            self.force_transfer_move_of_buy_with_prime_orders= ShopifySettings.force_transfer_move_of_buy_with_prime_orders
            self.add_new_product_order_webhook=ShopifySettings.add_new_product_order_webhook
            self.auto_create_product_category=ShopifySettings.auto_create_product_category
            self.auto_fulfill_gift_card_order=ShopifySettings.auto_fulfill_gift_card_order
            self.auto_import_product=ShopifySettings.auto_import_product
            self.import_buy_with_prime_shopify_order=ShopifySettings.import_buy_with_prime_shopify_order
            self.import_customer_as_company=ShopifySettings.import_customer_as_company
            self.is_delivery_fee=ShopifySettings.is_delivery_fee
            self.is_delivery_multi_warehouse=ShopifySettings.is_delivery_multi_warehouse
            self.is_shopify_create_schedule=ShopifySettings.is_shopify_create_schedule
            self.is_shopify_digest=ShopifySettings.is_shopify_digest
            self.order_visible_currency=ShopifySettings.order_visible_currency
            self.refund_order_webhook=ShopifySettings.refund_order_webhook
            self.return_picking_order=ShopifySettings.return_picking_order
            self.ship_order_webhook=ShopifySettings.ship_order_webhook
            self.shopify_is_use_analytic_account = ShopifySettings.shopify_is_use_analytic_account
            self.shopify_is_use_default_sequence = ShopifySettings.shopify_is_use_default_sequence
            self.shopify_notify_customer = ShopifySettings.shopify_notify_customer
            self.shopify_set_sales_description_in_product = ShopifySettings.shopify_set_sales_description_in_product
            self.shopify_sync_product_with_images = ShopifySettings.shopify_sync_product_with_images
            self.show_net_profit_report = ShopifySettings.show_net_profit_report
            self.stock_validate_for_return = ShopifySettings.stock_validate_for_return
            self.update_qty_order_webhook = ShopifySettings.update_qty_order_webhook
            self.update_qty_to_invoice_order_webhook = ShopifySettings.update_qty_to_invoice_order_webhook
            self.use_default_terms_and_condition_of_odoo = ShopifySettings.use_default_terms_and_condition_of_odoo
            self.create_shopify_products_webhook = ShopifySettings.create_shopify_products_webhook
            self.create_shopify_customers_webhook = ShopifySettings.create_shopify_customers_webhook
            self.create_shopify_orders_webhook = ShopifySettings.create_shopify_orders_webhook
            self.forcefully_reserve_stock_webhook = ShopifySettings.forcefully_reserve_stock_webhook
            self.credit_note_register_payment = ShopifySettings.credit_note_register_payment
            self.customer_order_webhook = ShopifySettings.customer_order_webhook
            self.delivery_fee_name = ShopifySettings.delivery_fee_name
            self.shopify_order_prefix = ShopifySettings.shopify_order_prefix
            self.shopify_import_order_after_date = ShopifySettings.shopify_import_order_after_date
            self.shopify_date_deadline = ShopifySettings.shopify_date_deadline
            self.shopify_payout_last_date_import = ShopifySettings.shopify_payout_last_date_import
            self.Force_transfer_move_of_buy_with_prime_orders = ShopifySettings.Force_transfer_move_of_buy_with_prime_orders

            self.buy_with_prime_tag_ids = [(6, 0, ShopifySettings.buy_with_prime_tag_ids.ids)]


            self.buy_with_prime_warehouse_id = ShopifySettings.buy_with_prime_warehouse_id.id
            self.credit_note_payment_journal = ShopifySettings.credit_note_payment_journal.id
            self.shopify_activity_type_id = ShopifySettings.shopify_activity_type_id.id
            self.shopify_analytic_account_id = ShopifySettings.shopify_analytic_account_id.id
            self.shopify_company_id = ShopifySettings.shopify_company_id.id
            self.shopify_compare_pricelist_id = ShopifySettings.shopify_compare_pricelist_id.id
            self.shopify_credit_tax_account_id = ShopifySettings.shopify_credit_tax_account_id.id
            self.shopify_default_pos_customer_id = ShopifySettings.shopify_default_pos_customer_id.id
            self.shopify_instance_product_category = ShopifySettings.shopify_instance_product_category.id
            self.shopify_invoice_tax_account_id = ShopifySettings.shopify_invoice_tax_account_id.id
            self.shopify_pricelist_id = ShopifySettings.shopify_pricelist_id.id
            self.shopify_product_uom_id = ShopifySettings.shopify_product_uom_id.id
            self.shopify_section_id = ShopifySettings.shopify_section_id.id
            self.shopify_settlement_report_journal_id = ShopifySettings.shopify_settlement_report_journal_id.id
            self.shopify_stock_field = ShopifySettings.shopify_stock_field.id
            self.shopify_apply_tax_in_order = ShopifySettings.shopify_apply_tax_in_order
            self.shopify_sync_product_with = ShopifySettings.shopify_sync_product_with
            self.shopify_order_status_ids = [(6, 0, ShopifySettings.shopify_order_status_ids.ids)]
            self.shopify_user_ids =[(6, 0, ShopifySettings.shopify_user_ids.ids)]   


            # Fetch related data from the selected instance
    
    
    def download_shopify_net_profit_report_module(self):
        print("..... download_shopify_net_profit_report_module")
        pass
    
    def shopify_test_connection(self):
        print("..... shopify_test_connection")
        pass
    
    def open_reset_credentials_wizard(self):
        print("..... open_reset_credentials_wizard")
        pass
    
    def cron_configuration_action(self):
        print("..... cron_configuration_action")
        pass
    
    def action_redirect_to_ir_cron(self):
        print("..... action_redirect_to_ir_cron")
        pass
    
    def action_shopify_active_archive_instance(self):
        print("..... action_shopify_active_archive_instance")
        pass
    
    def refresh_webhooks(self):
        print("..... refresh_webhooks")
        pass
    


def import_order_cron_job(self):
        try: 

          CheckSetting = self.env['res.config.settings'].search([("shopify_instance_id", '=', self.instance_id.id)],order="id desc",limit=1)
          print("CheckSetting..........",CheckSetting)
          if CheckSetting:
              if not CheckSetting.shopify_order_status_ids:
                  return {                                                                                  
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'title': 'Error!',
                            'message': 'Please Select Order Status in setting section for import order from shopify !',
                            'type': 'danger',
                            'sticky': False,
                            }
                        }
              if not CheckSetting.shopify_is_use_default_sequence:
                   return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'title': 'Error!',
                            'message': 'Please Select Odoo sequence in setting section for import order from shopify !',
                            'type': 'danger',
                            'sticky': False,
                            }
                        }
              
              if not CheckSetting.shopify_apply_tax_in_order:

                  return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'title': 'Error!',
                            'message': 'Please Select Tax Configuration in setting section for import order from shopify !',
                            'type': 'danger',
                            'sticky': False,
                            }
                        }
                  
                  
          else:

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Error!',
                    'message': 'Please configure Order Configuration in setting section for import order from shopify ! ',
                    'type': 'danger',
                    'sticky': False,
                    }
                }
            
          ######################################################################################
          url = self.instance_id.shopify_host
          

            # Get the current date and time
          current_date = datetime.now()

            # Get the date two days before
          two_days_before = current_date - timedelta(days=5)

            # Format the dates as required
          formatted_current_date = current_date.strftime("%Y-%m-%d %H:%M:%S")
          formatted_two_days_before = two_days_before.strftime("%Y-%m-%d %H:%M:%S")

          print("Current Date:", formatted_current_date)
          print("Two Days Before:", formatted_two_days_before)

          domain = urlparse(url).netloc
        
          SHOP_URL = f"https://{self.instance_id.shopify_api_key}:{self.instance_id.shopify_password}@{domain}/admin"
          print("SHOP_URL....",SHOP_URL)
          shopify.ShopifyResource.set_site(SHOP_URL)

        #   shopifyorders = shopify.Order.find(
        #             status=any,
        #             created_at_min=formatted_current_date,
        #             created_at_max=formatted_two_days_before
        #         )
          shopifyorders = shopify.Order.find(limit=5)
          # #####################################################################################  

          #kunal
          print("shopifyorders.......",shopifyorders)
          for orderdata in shopifyorders:
                try:
                    ord_data = orderdata.to_dict()
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
                                'state_id': _get_state_id(customerdata["default_address"]["province"]),
                                'country_id': _get_country_id(country),
                                "shopify_customer_id": customer_id,
                                "is_shopify_customer": True,
                                'customer_rank': 1,
                                "shopify_instance_id": self.instance_id.id
                            })
                        else:
                            pass

                    shopify_order_id= ord_data["id"]  
                    line_items= ord_data["line_items"]   

                    financial_status=ord_data["financial_status"]
                    print(".......",financial_status)
                    fulfillment_status=ord_data["fulfillment_status"]
                    print(".......",fulfillment_status)

                    shopify_order_exist = self.env['sale.order'].search([("shopify_order_id", '=',shopify_order_id)], limit=1)
                    if not shopify_order_exist:
                        ########################################################################################### price  
                        sale_order_line = []
                        for i in line_items:
                            shopify_varient_id= i["variant_id"] 
                            print("shopify_varient_id............",shopify_varient_id)
                            varient_id = self.env['product.product'].search([("shopify_varient_pk_id", '=',shopify_varient_id)], limit=1)
                            print("......varient_id",varient_id)
                            pr_data = [0,0,{'product_id': varient_id.id,'product_uom_qty': i['current_quantity'],'price_unit': i['price']}]
                            sale_order_line.append(pr_data)
                            
                        sale_order_data = {
                        'user_id':2,    
                        'payment_term_id':1,
                        'partner_id': shopify_customer.id,  # ID of the partner/customer
                        'order_line': sale_order_line,
                        "shopify_order_id": shopify_order_id, # instance id
                        "shopify_instance_id": self.instance_id.id
                                        }
                        
                        sale_order = self.env['sale.order'].sudo().create(sale_order_data)
                        
                        invoice_data = {
                            'move_type': 'out_invoice',
                            'partner_id': sale_order.partner_id.id,
                            'invoice_origin': sale_order.name,
                            'l10n_in_state_id': sale_order.partner_id.state_id.id,  # Place of Supply
                            'shopify_instance_id': self.instance_id.id,
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

                        sale_order.action_confirm()   #conform sales order 
                        invoice.action_post()  #conform invoice 

                        ####################################  create payment ############################################
                        #when queue type is shipped then  payment registered.
                        # Validate delivery order if fulfillment_status is 'fulfilled'
                        if fulfillment_status == "fulfilled":
                            # Fetch the related delivery order (stock.picking)
                            picking = self.env['stock.picking'].search([('origin', '=', sale_order.name), ('state', '!=', 'done')], limit=1)
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
                            if financial_status == "paid":
                                today = datetime.today().date()
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
                            print("....................",e)

                    else:

                        if fulfillment_status == "fulfilled":
                            # Fetch the related delivery order (stock.picking)
                            picking = self.env['stock.picking'].search([('origin', '=', shopify_order_exist.name), ('state', '!=', 'done')], limit=1)
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
                            
                            if financial_status == "paid":

                                # print(shopify_order_exist.name)
                                invoice = self.env['account.move'].search([('invoice_origin','=',shopify_order_exist.name),('move_type','=',"entry")], limit=1)
                                # print(invoice)
                                if not invoice:

                                    invoice=self.env['account.move'].search([('invoice_origin','=',shopify_order_exist.name),('move_type','=',"out_invoice")], limit=1)
                                    
                                    today = datetime.today().date()
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
                            print("....................",e)

                        #####################################################################################################

                except Exception as e:
                   print(".......................",e)
                   custoemr_queue_data= self.env['common.log.lines.ept'].create({
                            'order_ref': e,
                            "shopify_instance_id": self.instance_id.id,
                            "message":e,
                            # "shopify_customer_data_queue_line_id":self.id
                      
                        })
                   

        except Exception as e:
            print(".......................0009",e)
            custoemr_queue_data= self.env['common.log.lines.ept'].create({
                            'order_ref': e,
                            "shopify_instance_id": self.instance_id.id,
                            "message":e,
                            # "shopify_customer_data_queue_line_id":self.id
                      
                        })


def import_cancel_orders_cron_job(self):

        url = self.instance_id.shopify_host

        CheckSetting = self.env['res.config.settings'].search([("shopify_instance_id", '=', self.instance_id.id)],order="id desc",limit=1)
        if not CheckSetting:
            return {"message":"Please configure Order Configuration in setting section for import order from shopify .", "type": "danger","title": "Error!"}   

        domain = urlparse(url).netloc
        SHOP_URL = f"https://{self.instance_id.shopify_api_key}:{self.instance_id.shopify_password}@{domain}/admin"
        shopify.ShopifyResource.set_site(SHOP_URL)
        unique_id = str(uuid.uuid4())


        current_date = datetime.now()
        # Get the date two days before
        two_days_before = current_date - timedelta(days=5)
        # Format the dates as required
        formatted_current_date = current_date.strftime("%Y-%m-%d %H:%M:%S")
        formatted_two_days_before = two_days_before.strftime("%Y-%m-%d %H:%M:%S")

        print("Current Date:", formatted_current_date)
        print("Two Days Before:", formatted_two_days_before)

        try:
            shopifyorders = shopify.Order.find(
                    status="cancelled"
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
                                'state_id': _get_state_id(customerdata["default_address"]["province"]),
                                'country_id': _get_country_id(country),
                                "shopify_customer_id": customer_id,
                                "is_shopify_customer": True,
                                'customer_rank': 1,
                                 "shopify_instance_id": self.instance_id.id
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
                            shopify_varient_id= i["variant_id"]
                            varient_id = self.env['product.product'].search([("shopify_varient_pk_id", '=',shopify_varient_id)], limit=1)
                            pr_data = [0,0,{'product_id': varient_id.id,'product_uom_qty': i['current_quantity'] ,'price_unit': i['price']} ]
                            sale_order_line.append(pr_data)
                            
                        sale_order_data = {

                        'user_id':2,    
                        'payment_term_id':1,
                        'partner_id': shopify_customer.id,  # ID of the partner/customer
                        'order_line': sale_order_line,
                        "shopify_order_id": shopify_order_id,
                        "state":"cancel",
                         "shopify_instance_id": self.instance_id.id
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
                                "shopify_instance_id": self.instance_id.id,
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

