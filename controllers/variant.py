# Part of Odoo. See LICENSE file for full copyright and licensing details

import json

from odoo.http import request, route, Controller
from odoo.addons.website_sale.controllers.variant import WebsiteSaleVariantController


class CustomWebsiteSaleVariantController(WebsiteSaleVariantController):

    @route('/website_sale/get_combination_info', type='json', auth='public', methods=['POST'], website=True)
    def get_combination_info_website(
        self, product_template_id, product_id, combination, add_qty, parent_combination=None,
        **kwargs
    ):
        product_template = request.env['product.template'].browse(
            product_template_id and int(product_template_id))

        combination_info = product_template._get_combination_info(
            combination=request.env['product.template.attribute.value'].browse(combination),
            product_id=product_id and int(product_id),
            add_qty=add_qty and float(add_qty) or 1.0,
            parent_combination=request.env['product.template.attribute.value'].browse(parent_combination),
        )

        # Pop data only computed to ease server-side computations.
        for key in ('product_taxes', 'taxes', 'currency', 'date'):
            combination_info.pop(key)

        product_info = request.env['product.product'].browse(product_id)
        min_price_sqm = product_info.price_per_sqm if product_info else None
        combination_info['min_price_sqm'] = min_price_sqm or None
        combination_info['display_sqm'] = product_info.display_sqm or False
        if request.website.product_page_image_width != 'none' and not request.env.context.get('website_sale_no_images', False):
            combination_info['carousel'] = request.env['ir.ui.view']._render_template(
                'website_sale.shop_product_images',
                values={
                    'product': product_template,
                    'product_variant': request.env['product.product'].browse(combination_info['product_id']),
                    'website': request.env['website'].get_current_website(),
                },
            )
        product_product = request.env['product.product'].browse(combination_info.get('product_id'))
        combination_info['price_per_sqm'] = product_product.price_per_sqm
        return combination_info
