from odoo import models, fields
from datetime import datetime

class ShopifyProductTemplateEpt(models.Model):
    _name = 'shopify.product.template.ept'
    _description = 'Shopify Product Template'
    
    
    active = fields.Boolean(default=True)
    description = fields.Text()
    created_at = fields.Datetime(default=fields.Datetime.now)
    updated_at = fields.Datetime(default=fields.Datetime.now)
    exported_in_shopify = fields.Boolean(
        string='Exported In Shopify',
        help='Indicates whether the product is exported to Shopify.'
    )
    name = fields.Char(
        string='Name',
        required=True,
        help='The name of the product.'
    )
    product_tmpl_id = fields.Many2one(
        comodel_name='product.template',
        string='Product Template',
        help='Related product template.'
    )
    published_at = fields.Datetime(
        string='Published At',
        help='The date and time when the product was published on Shopify.'
    )
    shopify_image_ids = fields.One2many(
        'shopify.product.image.ept',
        'shopify_template_id',
        string='Shopify Images',
        help='Images associated with the Shopify product.'
    )
    shopify_instance_id = fields.Many2one(
        comodel_name='shopify.instance.ept',
        string='Instance',
        help='The Shopify instance associated with this product.'
    )
    shopify_product_category = fields.Many2one(
        comodel_name='product.category',
        string='Product Category',
        help='Category of the Shopify product.'
    )
    shopify_product_ids = fields.One2many(
        comodel_name='shopify.product.product.ept',
        inverse_name='shopify_template_id',
        string='Products',
        help='Products associated with this Shopify template.'
    )
    shopify_tmpl_id = fields.Char(
        string='Shopify Template ID',
        help='The Shopify template ID.'
    )
    tag_ids = fields.Many2many(
        comodel_name='shopify.tags',
        string='Tags',
        help='Tags associated with the Shopify product.'
    )
    template_suffix = fields.Char(
        string='Template Suffix',
        help='Template suffix for Shopify products.'
    )
    total_sync_variants = fields.Integer(
        compute="compute_number_variant",
        string='Total Synced Variants',
        help='Total number of synced variants.'
    )
    total_variants_in_shopify = fields.Integer(
        string='Total Variants',
        help='Total number of variants in Shopify.'
    )
    updated_at = fields.Datetime(
        string='Updated At',
        help='The date and time when the product was last updated.'
    )
    website_published = fields.Selection(
        selection=[('unpublished', 'Unpublished'), ('published_web', 'Published in Web Only'), ('published_global', 'Published in Web and POS')],
        string='Published?',
        help='Indicates whether the product is published on the website.'
    )
    
    def compute_number_variant(self):
       self.total_sync_variants =  len(self.shopify_product_ids)
    
    def write(self, vals):
        res = super(ShopifyProductTemplateEpt, self).write(vals)
        for rec in self:
            if rec.updated_at and  str(rec.updated_at)[:19] != str(datetime.now())[:19]:
                rec.updated_at = datetime.now()
            else:
                if not rec.updated_at:
                    rec.updated_at = datetime.now()
        return res
    
    def shopify_publish_unpublish_product(self):
        pass
    
    
    def action_product_ref_redirect(self):
        pass


class ShopifyProductImageEpt(models.Model):
    _name = 'shopify.product.image.ept'
    _description = 'Shopify Product Image'

    image = fields.Binary(
        string='Image',
        help='The image file associated with the product.'
    )
    odoo_image_id = fields.Many2one(
        comodel_name='common.product.image.ept',
        string='Odoo Image',
        help='Reference to the image stored in Odoo.'
    )
    sequence = fields.Integer(
        string='Sequence',
        help='Sequence number for ordering images.'
    )
    shopify_image_id = fields.Char(
        string='Shopify Image ID',
        help='The unique identifier for the image in Shopify.'
    )
    shopify_template_id = fields.Many2one(
        comodel_name='shopify.product.template.ept',
        string='Shopify Template',
        help='The Shopify product template associated with this image.',
        ondelete='cascade'
    )
    shopify_variant_id = fields.Many2one(
        comodel_name='shopify.product.product.ept',
        string='Shopify Variant',
        help='The Shopify product variant associated with this image.'
    )
    url = fields.Char(
        string='URL',
        help='The URL of the image in Shopify.'
    )
    
class CommonProductImageEpt(models.Model):
    _name = 'common.product.image.ept'
    _description = 'Common Product Image'

    image = fields.Binary(
        string='Image',
        help='The binary file of the product image.'
    )
    name = fields.Char(
        string='Name',
        help='The name or description of the image.'
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
        help='Reference to the product associated with this image.',
        ondelete='cascade'
    )
    sequence = fields.Integer(
        string='Sequence',
        help='Sequence number for ordering the images.'
    )
    template_id = fields.Many2one(
        comodel_name='product.template',
        string='Product Template',
        help='Reference to the product template associated with this image.'
    )
    url = fields.Char(
        string='Image URL',
        help='The URL of the product image.'
    )
    
    
class ShopifyProductProductEpt(models.Model):
    _name = 'shopify.product.product.ept'
    _description = 'Shopify Product Product EPT'

    active = fields.Boolean(string='Active', default=True)
    check_product_stock = fields.Selection([
        ('continue', 'Allow'),
        ('deny', 'Denied')
    ], string='Sale out of stock products?')
    default_code = fields.Char(string='Default Code')
    exported_in_shopify = fields.Boolean(string='Exported In Shopify')
    fix_stock_type = fields.Selection([
        ('fix', 'Fix'),
        ('percentage', 'Percentage')
    ], string='Fix Stock Type')
    fix_stock_value = fields.Float(string='Fix Stock Value')
    fixed_stock_export = fields.Boolean(string='Fixed Stock Export')
    fixed_stock_export_value = fields.Float(string='Fixed Stock Export Value')
    inventory_item_id = fields.Char(string='Inventory Item')
    inventory_management = fields.Selection([
        ('shopify', 'Shopify tracks this product Inventory'),
        ('Dont track Inventory', 'Dont track Inventory')
    ], string='Inventory Management')
    last_stock_update_date = fields.Datetime(string='Last Stock Update Date')
    name = fields.Char(string='Title')
    product_id = fields.Many2one('product.product', string='Product')
    sequence = fields.Integer(string='Position')
    shopify_image_ids = fields.One2many('shopify.product.image.ept', 'shopify_variant_id', string='Shopify Image')
    shopify_instance_id = fields.Many2one('shopify.instance.ept', string='Instance')
    shopify_template_id = fields.Many2one('shopify.product.template.ept', string='Shopify Template', ondelete='cascade')
    taxable = fields.Boolean(string='Taxable')
    variant_id = fields.Char(string='Variant')
    created_at = fields.Datetime()
    updated_at = fields.Datetime()

 
class ShopifyTag(models.Model):
    _name = "shopify.tags"
     
    name = fields.Char()
    sequence = fields.Integer() 
     