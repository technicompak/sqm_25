# __manifest__.py
{
    'name': 'Pricelist Price per Squaremeter',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Adds price per square meter to product variants and displays it on the website.',
    'author': 'Your Name',
    'depends': ['base', 'website_sale', 'product'],
    'data': [
        'views/product_template_view.xml',
        # 'templates/website_sale_template.xml',
    ],

    'assets': {
        'web.assets_frontend': [
            'pricelist_sqmeter/static/src/js/website_sale.js',
        ],

    },
    'installable': True,
    'application': False,
}
