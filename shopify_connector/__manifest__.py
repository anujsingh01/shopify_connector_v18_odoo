# -*- coding: utf-8 -*-
{
    'name': "Shopify Connector",
    'summary': "The Odoo to Shopify connector enables seamless integration for managing products, stock, prices, and images between Odoo and Shopify. It supports exporting and updating product details, stock levels, prices, and order statuses, as well as publishing or unpublishing products. Shopify updates are instantly reflected in Odoo via webhooks, including new orders, product changes, and order status updates. Additionally, it facilitates importing products, customer details, orders, and Shopify payout transactions into Odoo for efficient reconciliation and management.",
    'description': """
        The Odoo to Shopify connector enables seamless integration for managing products, stock, prices, and images between Odoo and Shopify. It supports exporting and updating product details, stock levels, prices, and order statuses, as well as publishing or unpublishing products. Shopify updates are instantly reflected in Odoo via webhooks, including new orders, product changes, and order status updates. Additionally, it facilitates importing products, customer details, orders, and Shopify payout transactions into Odoo for efficient reconciliation and management.
    """,
    'author': "Inwizards Software Technology",
    'website': "https://www.inwizards.com/",
    'category': 'Uncategorized',
    'version': '0.1',
    'price' : '149',
    'currency' : 'USD', 

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'account', 'stock','product'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'demo/demo.xml',
        'views/dashboard.xml',
        'views/sale_order.xml',
        'views/product.xml',
        'views/operation.xml',
        'views/logs.xml',
        'views/shopify_instance.xml',
        'views/menu_items.xml',
        'views/product_template_views.xml',
    ],
    'images': ['static/description/banner.png'],
    'assets': {
        'web.assets_backend': [
            "shopify_connector/static/src/component/shopify_connector/js/shopify_dashboard_client.js",
            "shopify_connector/static/src/component/shopify_connector/xml/shopify_dashboard_client.xml",
            "https://cdn.jsdelivr.net/npm/bootstrap@4.6.2/dist/css/bootstrap.min.css",
            "shopify_connector/static/src/component/shopify_connector/css/index.css",
        ]
    },
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

