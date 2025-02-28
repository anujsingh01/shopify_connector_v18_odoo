from odoo import models,api, fields, _
import ast
import requests
import base64
import shopify
from urllib.parse import urlparse
import ast
from odoo.exceptions import UserError
from datetime import date


class MyCustomException(Exception):
    pass


class ShopifyOrderDataQueueEPT(models.Model):
    _name = 'shopify.order.data.queue.ept'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Shopify Order Data Queue'

    
    name = fields.Char(string='Name')
    order_data_queue_line_ids = fields.One2many('shopify.order.data.queue.line.ept', 'shopify_order_data_queue_id', string='Order Data Queue Line')
    order_queue_line_cancel_record = fields.Integer(string='Cancel Records')
    order_queue_line_done_record = fields.Integer(string='Done Records')
    order_queue_line_draft_record = fields.Integer(string='Draft Records')
    order_queue_line_fail_record = fields.Integer(string='Fail Records')
    order_queue_line_total_record = fields.Integer(string='Total Records')
    queue_process_count = fields.Integer(string='Queue Process Times')
    queue_type = fields.Selection([('shipped', 'Shipped Order Queue'), ('unshipped', '	Unshipped Order Queue')], string='Queue Type')
    running_status = fields.Char(string='Running Status')
    shopify_instance_id = fields.Many2one('shopify.instance.ept', string='Instance')
    shopify_order_common_log_lines_ids = fields.One2many('common.log.lines.ept', 'queue_id', string='Shopify Order Common Log Lines')
    state = fields.Selection([('draft', 'Draft'), ('partially_completed', 'Partially Completed'), ('completed', 'Completed'),('failed', 'Failed')],string='State')
    is_action_require = fields.Boolean()
    is_process_queue = fields.Boolean()
    create_date = fields.Datetime(string="Created On", default=fields.Datetime.now)
    created_by = fields.Selection([('import', 'By Manually Import Process'), ('webhook', 'By Webhook'), ('scheduled_action', 'By Scheduled Action')], string="Created By")
    
    def process_queue_manually(self):
        try: 
          print("queue_type........",self.queue_type) 

          CheckSetting = self.env['res.config.settings'].search([("shopify_instance_id", '=', self.shopify_instance_id.id)],order="id desc",limit=1)
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
                            'message': 'Please Select Odoo default sequence in setting section for import order from shopify !',
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

          
          shopify_order = self.env['shopify.order.data.queue.line.ept'].search([("shopify_order_data_queue_id", '=',self.id)])
          success_count=0
          failed_count=0
          

          for orderdata in shopify_order:
                try:
                    ord_data = ast.literal_eval(orderdata.order_data)
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
                                "shopify_instance_id": self.shopify_instance_id.id
                            })
                        else:
                            pass

                    shopify_order_id= ord_data["id"]  
                    line_items= ord_data["line_items"]   

                    financial_status=ord_data["financial_status"]
                    fulfillment_status=ord_data["fulfillment_status"]

                    shopify_order_exist = self.env['sale.order'].search([("shopify_order_id", '=',shopify_order_id)], limit=1)
                    shopify_order_exist=''
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
                        "shopify_instance_id": self.shopify_instance_id.id,
                                        }
                        
                        
                        sale_order = self.env['sale.order'].sudo().create(sale_order_data)
                        
                        invoice_data = {
                            'move_type': 'out_invoice',
                            'partner_id': sale_order.partner_id.id,
                            'invoice_origin': sale_order.name,
                            'l10n_in_state_id': sale_order.partner_id.state_id.id,  # Place of Supply
                            'shopify_instance_id': self.shopify_instance_id.id,
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
                                print("account_move..........",account_move)
                                
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
                                print("account_payment..........",account_payment)
                                account_payment.sudo().action_post()
                                lines = self.env['account.move.line'].sudo().search([('name', '=', invoice.name)])
                                print("lines..........",lines)
                                for line in lines:
                                    if amount_total <= 0:
                                        break
                                    if line.amount_residual <= amount_total:
                                        remaining_amount = amount_total - line.amount_residual
                                        # Create partial reconciliation
                                        reconcile_vals = {
                                            'debit_move_id': line.id,
                                            'credit_move_id':108,
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
                            print("....................",e)

                        #####################################################################################################

                    success_count+=1

                    orderdata.write({
                            "state":"done",
                            })


                except Exception as e:
                   failed_count+=1      
                   print(".......................",e)
                   custoemr_queue_data= self.env['common.log.lines.ept'].create({
                            'order_ref': e,
                            "shopify_instance_id": self.shopify_instance_id.id,
                            "message":e,
                            # "shopify_customer_data_queue_line_id":self.id
                      
                        })
                   
                   orderdata.write({
                            "state":"done",
                            })
          self.write({
                     "order_queue_line_done_record":success_count,
                     "order_queue_line_fail_record":failed_count,
                     "state":"partially_completed",
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
            print(".......................0009",e)
            custoemr_queue_data= self.env['common.log.lines.ept'].create({
                            'order_ref': e,
                            "shopify_instance_id": self.shopify_instance_id.id,
                            "message":e,
                            # "shopify_customer_data_queue_line_id":self.id
                      
                        })
            
            self.write({
                            "state":"failed",
                            }) 
            
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
        



    def set_to_completed(self):
         print("self,,,....",self)
         self.write({
                     "state":"completed",
                     "running_status":"completed"
                    })  
          
         return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Success!',
                        'message': "Unshipped order process completed successfully!",
                        'type': 'success',  # 'success', 'warning', 'danger', 'info'
                        'sticky': False,  # Set to True to make the notification persistent
                    }
                }

    def _get_country_id(self, country_name):
        """Get country ID from name."""
        country = self.env['res.country'].search([('name', '=', country_name)], limit=1)
        return country.id if country else False

    def _get_state_id(self, state_name):
        """Get state ID from name."""
        state = self.env['res.country.state'].search([('name', '=', state_name)], limit=1)
        return state.id if state else False  
    
    
class ShopifyOrderDataQueueLineEpt(models.Model):
    _name = 'shopify.order.data.queue.line.ept'
    _description = 'Shopify Order Data Queue Line'

   
    customer_email = fields.Char(string="Customer Email")
    customer_name = fields.Char(string="Customer Name")
    name = fields.Char(string="Name")
    order_data = fields.Text(string="Order Data")
    processed_at = fields.Datetime(string="Processed At")
    sale_order_id = fields.Many2one('sale.order', string="Sale Order")
    shopify_instance_id = fields.Many2one('shopify.instance.ept', string="Instance")
    shopify_order_common_log_lines_ids = fields.One2many('common.log.lines.ept', 'shopify_order_data_queue_line_id', string="Shopify Order Common Log Lines")
    shopify_order_data_queue_id = fields.Many2one('shopify.order.data.queue.ept', string="Shopify Order Data Queue")
    shopify_order_id = fields.Char(string="Shopify Order")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('failed', 'Failed'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ], string="State", default='draft')
    
    queue_id = fields.Many2one("shopify.order.data.queue.ept", string="Queue")
    
class CommonLogLinesEpt(models.Model):
    _name = 'common.log.lines.ept'
    _description = 'Common Log Lines'
    _inherit = ['mail.thread']
   
    default_code = fields.Char(string="SKU")
    shopify_instance_id = fields.Many2one('shopify.instance.ept', string="Shopify Instance")
    shopify_order_data_queue_line_id = fields.Many2one('shopify.order.data.queue.line.ept', string="Shopify Order Queue Line")
    shopify_order_data_queue__id = fields.Many2one('shopify.order.data.queue.ept', string="Shopify Order Queue data")
    shopify_payout_report_line_id = fields.Many2one('shopify.payout.report.line', string="Shopify Payout Report Line")
    shopify_product_data_queue_line_id = fields.Many2one('shopify.product.data.queue.line.ept', string="Shopify Product Queue Line")
    queue_id = fields.Many2one("shopify.order.data.queue.ept", string="Queue")
    write_date = fields.Datetime(string="Last Updated On", default=fields.Datetime.now)
    order_ref = fields.Char()
    model_id= fields.Many2one("ir.model", string="Model")
    shopify_product_data_queue_id = fields.Many2one(
    'shopify.product.data.queue.ept', 
    string='Product Data Queue'
    )
    message = fields.Text()
    shopify_customer_data_queue_line_id = fields.Many2one("shopify.customer.data.queue.line.ept")
    shopify_export_data_queue_line_id = fields.Many2one("shopify.export.stock.queue.ept")
    shopify_export_stock_queue_line_id = fields.Many2one("shopify.export.stock.queue.line.ept")
    

class ShopifyProductDataQueue(models.Model):
    _name = 'shopify.product.data.queue.ept'
    _description = 'Shopify Product Data Queue'
    _inherit = ['mail.thread']

    
    name = fields.Char(string='Name', required=True,
                          readonly=True, default=lambda self: _('New'))
    common_log_lines_ids = fields.One2many('common.log.lines.ept', 'shopify_product_data_queue_id', string='Common Log Lines')
    created_by = fields.Selection([
        ('import', 'By Import Process'),
        ('webhook', 'By Webhook')],
        string='Created By'
    )
    is_action_require = fields.Boolean(string='Is Action Require')
    is_process_queue = fields.Boolean(string='Is Processing Queue')
    product_data_queue_lines = fields.One2many('shopify.product.data.queue.line.ept', 'product_data_queue_id', string='Product Queue Lines')
    queue_line_cancel_records = fields.Integer(compute="compute_queue_line_cancel_records", string='Cancelled Records')
    queue_line_done_records = fields.Integer(compute="compute_queue_line_done_records", string='Done Records')
    queue_line_draft_records = fields.Integer(compute="compute_queue_line_draft_records", string='Draft Records')
    queue_line_fail_records = fields.Integer(compute="compute_queue_line_fail_records", string='Fail Records')
    queue_line_total_records = fields.Integer(compute="compute_queue_line_total_records", string='Total Records')
    
    queue_process_count = fields.Integer(string='Queue Process Times')
    running_status = fields.Char(string='Running Status')
    shopify_instance_id = fields.Many2one('shopify.instance.ept', string='Instance')
    skip_existing_product = fields.Boolean(string='Do Not Update Existing Products')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('partially_completed', 'Partially Completed'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
        ],
        string='State'
    )
    
    
    def compute_queue_line_fail_records(self):
        self.queue_line_fail_records = len([rec for rec in self.product_data_queue_lines if rec.state == 'failed'])
    
    def compute_queue_line_draft_records(self):
        self.queue_line_draft_records = len([rec for rec in self.product_data_queue_lines if rec.state == 'draft'])
        
    def compute_queue_line_done_records(self):
        self.queue_line_done_records = len([rec for rec in self.product_data_queue_lines if rec.state == 'done'])
        
    def compute_queue_line_cancel_records(self):
        self.queue_line_cancel_records = len([rec for rec in self.product_data_queue_lines if rec.state == 'cancel'])
    
    @api.model_create_multi
    def create(self, vals):
        vals[0]['name'] = self.env['ir.sequence'].next_by_code('my_sequence_code')
        res = super(ShopifyProductDataQueue, self).create(vals)
        return res
    
    def compute_queue_line_total_records(self):
        self.queue_line_total_records = len(self.product_data_queue_lines)
        
        
    def fetch_and_save_image(self, url, product):
        """
        Fetches an image from the provided URL, converts it to binary,
        and saves it in the 'image_binary' field.
        """
        try:
            # Fetch the image from the URL
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # Raise an error for bad status codes

            # Encode the image content in base64
            image_binary = base64.b64encode(response.content)

            # Save the image in the 'image_binary' field
            product.write({'image_1920': image_binary})

            return True
        except requests.exceptions.RequestException as e:
            # Handle exceptions (e.g., network errors, invalid URL)
            self.env.cr.rollback()  # Rollback transaction in case of error
            raise ValueError(f"Error fetching image: {e}")
        
        
    def process_queue_manually(self):
        try:
            self.state = "partially_completed"
            for prodjson in self.product_data_queue_lines:
                if prodjson.state != "done":
                    try:
                        shopify_json = ast.literal_eval(prodjson.synced_product_data)
                        tag_list = []   
                        tags = shopify_json.get('tags')

                        for tag in tags.split(","):
                            available_tag = self.env["shopify.tags"].search([('name', '=', tag)], limit=1)
                            if available_tag:
                                tag_list.append(available_tag.id)
                            else:
                                create_tag = self.env["shopify.tags"].create({
                                    "name": tag
                                })
                                tag_list.append(create_tag.id)

                        image_url = shopify_json.get("image", None)
                        if image_url:
                            image_url = image_url.get("src", None)
                            response = requests.get(image_url, timeout=10)
                            response.raise_for_status()
                            image_base64 = base64.b64encode(response.content).decode('utf-8')
                        
                        product_tmpl = self.env["product.template"].create({
                            "name": shopify_json.get('title'),
                            "image_1920" : image_base64 if image_url else False ,
                            "is_storable" : True,
                            "shopify_instance_id": self.shopify_instance_id.id
                        })
                        
                        shopify_product_template_ept_dict = {
                            "name": shopify_json.get('title'),
                            "shopify_instance_id": self.shopify_instance_id.id,
                            "shopify_tmpl_id": str(shopify_json.get('id')),
                            "exported_in_shopify": True,
                            "website_published": "unpublished",
                            "tag_ids": [(6, 0, tag_list)],
                            "total_variants_in_shopify": len(shopify_json.get('variants')),
                            "product_tmpl_id": product_tmpl.id,
                        }

                        shopify_tmpl_id = self.env["shopify.product.template.ept"].create(shopify_product_template_ept_dict)
                        print("======================== shopify template id ============================", shopify_tmpl_id.id)

                        for shopify_variant in shopify_json.get("options"):
                            value_list = []
                            attribute_id = self.env["product.attribute"].create({
                                "name": shopify_variant.get('name')
                            })
                            for val in shopify_variant.get("values"):
                                product_att_val = self.env["product.attribute.value"].create({"name": val, "attribute_id" : attribute_id.id})
                                value_list.append(product_att_val.id)
                            product_tmpl.attribute_line_ids = [(0, 0, {"attribute_id" : attribute_id.id,"value_ids" :  [(6,0,value_list)]})]
                        
                        variant_list = []
                        
                        for variant, product in zip(shopify_json.get('variants', []), product_tmpl.product_variant_ids):
                            try :
                                if  variant.get('sku'):
                                    variant_list.append((0, 0, {
                                        "name": shopify_json.get('title'),
                                        "shopify_instance_id": self.shopify_instance_id.id,
                                        "variant_id": variant.get('id'),
                                        "sequence": variant.get('position'),
                                        "exported_in_shopify": True,
                                        "default_code": variant.get('sku'),
                                        "inventory_item_id": variant.get('inventory_item_id'),
                                        "taxable": variant.get('taxable'),
                                        "inventory_management": variant.get('inventory_management'),
                                        "shopify_template_id": shopify_tmpl_id.id,
                                        "product_id":product.id,
                                    }))
                                    product.shopify_varient_pk_id = variant.get('id')
                                    product.inventory_item_id = variant.get('inventory_item_id')
                                    product.default_code = variant.get('sku')

                                else:
                                    raise MyCustomException(f"SKU not present in variant id {variant.get('id')} {shopify_json.get('title')} ")
                            except Exception as e :
                                # prodjson.state = "failed"
                                self.write({
                                    "common_log_lines_ids": [(0,0,{
                                        'order_ref': e,
                                        "shopify_instance_id": self.shopify_instance_id.id,
                                        "message":e,
                                        "shopify_product_data_queue_id":self.id,
                                        "shopify_product_data_queue_line_id" : prodjson.id
                                    })]
                                })
                            
                        print("value list ", value_list, "attribute_id ",attribute_id.id,"..............",variant_list)
                        if variant_list:
                            shopify_tmpl_id.write({"shopify_product_ids": variant_list })
                            prodjson.state = "done"
                        else :
                            prodjson.state = "failed"
                            shopify_tmpl_id.unlink()
                            product_tmpl.unlink()
                            continue
                            
                            
                        shopify_templ_img_list  = [] 
                        for img in shopify_json.get("images"):
                            image_url = img.get("src", None)
                            response = requests.get(image_url, timeout=10)
                            response.raise_for_status()
                            image_base64 = base64.b64encode(response.content).decode('utf-8')
                            
                            shopify_variant_ids = img.get("variant_ids")
                            variant_id = None
                            if shopify_variant_ids:
                                variant_id = self.env["shopify.product.product.ept"].search([("variant_id", "=", shopify_variant_ids[-1])], limit=1)
                        
                            product_id = self.env["product.product"].search([("product_tmpl_id", "=", product_tmpl.id)])[-1]
                            
                            shopify_common_id = self.env["common.product.image.ept"].create({
                                "image" :image_base64,
                                "url": image_url,
                                "name": shopify_json.get('title'),
                                "template_id" : product_tmpl.id,
                                "product_id" : product_id.id if product_id else None
                            })
                        
                            shopify_templ_img_list.append((0,0,{
                            "image" :image_base64,
                            "url": image_url,
                            "shopify_image_id": img.get("id"),
                            "shopify_variant_id" : variant_id.id if variant_id else None,
                            "odoo_image_id" : shopify_common_id.id
                            }))
                        
                        shopify_tmpl_id.write({"shopify_image_ids": shopify_templ_img_list})
                        
                    except Exception as e:
                        prodjson.state = "failed"
                        self.write({
                            "common_log_lines_ids": [(0,0,{
                                'order_ref': e,
                                "shopify_instance_id": self.shopify_instance_id.id,
                                "message":e,
                                "shopify_product_data_queue_id":self.id,
                                "shopify_product_data_queue_line_id" : prodjson.id
                            })]
                        })
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
            
    
    def set_to_completed(self):
        self.state = "completed"
        self.is_process_queue = False

class ShopifyProductDataQueueLine(models.Model):
    _name = 'shopify.product.data.queue.line.ept'
    _description = 'Shopify Product Data Queue Line'

    common_log_lines_ids = fields.One2many('common.log.lines.ept', 'shopify_product_data_queue_line_id', string='Common Log Lines')
    last_process_date = fields.Datetime(string='Last Process Date')
    name = fields.Char(string='Product')
    product_data_id = fields.Char(string='Product Data')
    product_data_queue_id = fields.Many2one(
        'shopify.product.data.queue.ept',
        string='Product Data Queue',
        ondelete='cascade'
    )
    shopify_image_import_state = fields.Selection([
        ('pending', 'Pending'),
        ('done', 'Done')],
        string='Shopify Image Import State'
    )
    shopify_instance_id = fields.Many2one('shopify.instance.ept', string='Instance')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
        ('failed', 'Failed'),
        ('cancel', 'Cancelled')],
        string='State'
    )
    synced_product_data = fields.Text(string='Synced Product Data')
    message = fields.Text()
    
    def replace_product_response(self):
        # import pdb;pdb.set_trace()
        url = self.shopify_instance_id.shopify_host
        domain = urlparse(url).netloc
        
        SHOP_URL = f"https://{self.shopify_instance_id.shopify_api_key}:{self.shopify_instance_id.shopify_password}@{domain}/admin/api/2024-10"
        shopify.ShopifyResource.set_site(SHOP_URL)

        product_id = str(self.product_data_id)
        if product_id:
            product = shopify.Product.find(product_id)
            self.synced_product_data = product.to_dict()
            print("replace_response", self.synced_product_data)

class ShopifyCustomerDataQueue(models.Model):
    _name = 'shopify.customer.data.queue.ept'
    _description = 'Shopify Customer Data Queue'
    _inherit = ['mail.thread']

    
    cancel_state_count = fields.Integer(string='Cancel State Count')
    common_log_lines_ids = fields.One2many('common.log.lines.ept', 'queue_id', string='Common Log Lines')
    done_state_count = fields.Integer(string='Done State Count')
    draft_state_count = fields.Integer(string='Draft State Count')
    fail_state_count = fields.Integer(string='Fail State Count')
    is_action_require = fields.Boolean(string='Is Action Require')
    is_process_queue = fields.Boolean(string='Is Processing Queue')
    
    name = fields.Char(string='Name')
    queue_process_count = fields.Integer(string='Queue Process Count')
    record_created_from = fields.Selection([
        ('webhook', 'From Webhook'),
        ('import_process', 'From Import Process')],
        string='Record Created From'
    )
    running_status = fields.Char(string='Running Status')
    shopify_instance_id = fields.Many2one('shopify.instance.ept', string='Instance')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('partially_completed', 'Partially Completed'),
        ('completed', 'Completed'),
        ('failed', 'Failed')],
        string='State'
    )
    synced_customer_queue_line_ids = fields.One2many('shopify.customer.data.queue.line.ept', 'synced_customer_queue_id', string='Customers')
    total_record_count = fields.Integer(string='Total Records Count')

    def customer_data_adding_process(self):
         
        try: 
          
          shopify_customer = self.env['shopify.customer.data.queue.line.ept'].search([("synced_customer_queue_id", '=',self.id)])
          success_count=0
          failed_count=0
          for customerdata in shopify_customer:
                try:
                    customer_data = ast.literal_eval(customerdata.shopify_synced_customer_data)
                    id = customer_data.get('id', None)
                    first_name = customer_data.get('first_name', '')
                    last_name = customer_data.get('last_name', '')
                    email = customer_data.get('email', '')
                    phone = customer_data.get('phone') or customer_data['default_address'].get('phone')
                    address = customer_data.get('default_address', {})
                    shopify_customer = self.env['res.partner'].search([("shopify_customer_id", '=',id)], limit=1)
                    if not shopify_customer:
                        self.env['res.partner'].create({
                            'name': first_name +" "+ last_name,
                            'email': email,
                            'phone': phone,
                            'street': customer_data['default_address'].get('address1', ''),
                            'street2': customer_data['default_address'].get('address2', ''),
                            'city': customer_data['default_address'].get('city', ''),
                            'state_id': self._get_state_id(customer_data['default_address'].get('province', '')),
                            'zip': customer_data['default_address'].get('zip', ''),
                            'country_id': self._get_country_id(customer_data['default_address'].get('country', '')),
                            'customer_rank': 1,  # Mark as customer
                            "shopify_customer_id": id,
                            "is_shopify_customer": True,
                            "shopify_instance_id": self.shopify_instance_id.id
                        })
                    else:
                        shopify_customer.write({
                            'name': first_name +" "+last_name,
                            'email': email,
                            'phone': phone,
                            'street': customer_data['default_address'].get('address1', ''),
                            'street2': customer_data['default_address'].get('address2', ''),
                            'city': customer_data['default_address'].get('city', ''),
                            'state_id': self._get_state_id(customer_data['default_address'].get('province', '')),
                            'zip': customer_data['default_address'].get('zip', ''),
                            'country_id': self._get_country_id(customer_data['default_address'].get('country', '')),
                            "is_shopify_customer": True
                        })
                        success_count+=1

                        customerdata.write({
                            "state":"done",
                            })   
                except Exception as e:
                   failed_count+=1      
                   custoemr_queue_data= self.env['common.log.lines.ept'].create({
                            'order_ref': e,
                            "shopify_instance_id": self.shopify_instance_id.id,
                            "message":e,
                            "shopify_customer_data_queue_line_id":self.id
                      
                        })
                   
                   customerdata.write({
                            "state":"failed",
                            }) 
                   
          self.write({
                     "done_state_count":success_count,
                     "fail_state_count":failed_count,
                     "state":"partially_completed",
                    })   
          
          return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Success!',
                        'message': "Process Queue manually successfully!",
                        'type': 'success',  # 'success', 'warning', 'danger', 'info'
                        'sticky': False,  # Set to True to make the notification persistent
                    }
                }
        except Exception as e:

            custoemr_queue_data= self.env['common.log.lines.ept'].create({
                            'order_ref': e,
                            "shopify_instance_id": self.shopify_instance_id.id,
                            "message":e,
                            "shopify_customer_data_queue_line_id":self.id
                        })
            
            self.write({
                            "state":"failed",
                            }) 
            
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
    
    def _get_country_id(self, country_name):
        """Get country ID from name."""
        country = self.env['res.country'].search([('name', '=', country_name)], limit=1)
        return country.id if country else False

    def _get_state_id(self, state_name):
        """Get state ID from name."""
        state = self.env['res.country.state'].search([('name', '=', state_name)], limit=1)
        return state.id if state else False   
    

    def customer_data_completed_process(self):
         print("self,,,....",self)
         self.write({
                     "state":"completed",
                     "running_status":"completed"
                    })  
         return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Success!',
                        'message': "Customer data process completed successfully!",
                        'type': 'success',  # 'success', 'warning', 'danger', 'info'
                        'sticky': False,  # Set to True to make the notification persistent
                    }
                }
   

class ShopifyCustomerDataQueueLine(models.Model):
    _name = 'shopify.customer.data.queue.line.ept'
    _description = 'Shopify Customer Data Queue Line'

    common_log_lines_ids = fields.One2many(
        'common.log.lines.ept', 
        'shopify_customer_data_queue_line_id', 
        string='Common Log Lines'
    )
    last_process_date = fields.Datetime(string='Last Process Date')
    name = fields.Char(string='Customer')
    shopify_customer_data_id = fields.Text(string='Customer ID')
    shopify_instance_id = fields.Many2one(
        'shopify.instance.ept', 
        string='Instance'
    )
    shopify_synced_customer_data = fields.Char(string='Shopify Synced Data')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('failed', 'Failed'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
        ],
        string='State', default='draft'
    )
    synced_customer_queue_id = fields.Many2one(
        'shopify.customer.data.queue.ept', 
        string='Shopify Customer'
    )
    

class ShopifyExportStockQueueEpt(models.Model):
    _name = 'shopify.export.stock.queue.ept'
    _description = 'Shopify Export Stock Queue'

    
    activity_state = fields.Selection(
       [('overdue', 'overdue'), ('today', 'Today'), ('planned','Planned')],
        string='Activity State'
    )
    common_log_lines_ids = fields.One2many('common.log.lines.ept', 'shopify_export_data_queue_line_id', string='Common Log Lines')  
    created_by = fields.Selection(
        [('import', 'By Import Process'), ('webhook', 'By Webhook')],
        string='Created By'
    )
    ###################################
    export_stock_queue_line_ids = fields.One2many('shopify.export.stock.queue.line.ept', 'export_stock_queue_id', string='Export Stock Queue Lines')
    ##############################
    is_action_require = fields.Boolean(string='Is Action Require')
    is_process_queue = fields.Boolean(string='Is Processing Queue')
    name = fields.Char(string='Name')
    queue_line_cancel_records = fields.Integer(string='Cancelled Records')
    queue_line_done_records = fields.Integer(string='Done Records')
    queue_line_draft_records = fields.Integer(string='Draft Records')
    queue_line_fail_records = fields.Integer(string='Fail Records')
    queue_line_total_records = fields.Integer(string='Total Records')
    queue_process_count = fields.Integer(string='Queue Process Times')
    running_status = fields.Char(string='Running Status')
    shopify_instance_id = fields.Many2one('shopify.instance.ept', string='Instance') 
    state = fields.Selection(
        [
        ('partially_completed', 'Partially Completed'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('draft', 'Draft')
        ],
        string='State'
    )
    
    


class ShopifyExportStockQueueLineEpt(models.Model):
    _name = 'shopify.export.stock.queue.line.ept'
    _description = 'Shopify Export Stock Queue Line'

    
    activity_state = fields.Selection(
        [('overdue', 'overdue'), ('today', 'Today'), ('planned','Planned')],
        string='Activity State'
    )
    common_log_lines_ids = fields.One2many('common.log.lines.ept', 'shopify_export_stock_queue_line_id', string='Common Log Lines') 
    export_stock_queue_id = fields.Many2one('shopify.export.stock.queue.ept', string='Export Stock Queue')  # Link to the parent queue
    
    inventory_item_id = fields.Char(string='Inventory Item')
    last_process_date = fields.Datetime(string='Last Process Date')
    location_id = fields.Char(string='Location')
    
    name = fields.Char(string='Name')
    quantity = fields.Integer(string='Quantity')
    shopify_instance_id = fields.Many2one('shopify.instance.ept', string='Instance')  # Modify 'shopify.instance.model' as needed
    shopify_product_id = fields.Many2one('shopify.product.product.ept', string='Product')  # Modify 'shopify.product.model' as needed
    state = fields.Selection(
        [('done', 'Done'), ('cancel', 'Cancelled'),
         ('failed', 'Failed'), ('draft', 'Draft')],
        string='State'
    )
  

  