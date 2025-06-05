import logging
from odoo import api, fields, models

_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    display_sqm = fields.Boolean(string='Display Square Meter Price')

    def _get_combination_info(self, combination=False, product_id=False, add_qty=1, parent_combination=False, only_template=False):
        combination_info = super()._get_combination_info(
            combination=combination,
            product_id=product_id,
            add_qty=add_qty,
            parent_combination=parent_combination,
            only_template=only_template
        )

        # Get the current website and its pricelist
        website = self.env['website'].get_current_website()
        pricelist = website.pricelist_id

        _logger.info(f'Getting combination info for template {self.name}')
        _logger.info(f'Product ID: {product_id}')
        _logger.info(f'Combination: {combination}')

        if product_id:
            product = self.env['product.product'].browse(product_id)
            price = product.list_price
            
            # Apply pricelist if available
            if pricelist:
                price = pricelist._get_product_price(product, 1.0, currency=website.currency_id)
            
            # Get taxes
            taxes = product.taxes_id.filtered(lambda t: t.company_id == self.env.company)
            if taxes:
                fpos = website.fiscal_position_id
                if fpos:
                    taxes = fpos.map_tax(taxes)
                price = taxes.compute_all(price, website.currency_id, 1.0, product)['total_included']

            # Calculate price per sqm
            sqm = 0
            for record in product.product_template_attribute_value_ids:
                if record.product_attribute_value_id.attribute_id.is_sqm:
                    sqm = record.product_attribute_value_id.sqm
                    break
            
            combination_info['price_per_sqm'] = price / sqm if sqm else 0
            _logger.info(f'Calculated price_per_sqm for product {product.name}: {combination_info["price_per_sqm"]}')
        else:
            # Get the first variant's price per sqm
            first_variant = self.product_variant_ids[:1]
            if first_variant:
                combination_info['price_per_sqm'] = first_variant.price_per_sqm
                _logger.info(f'Using first variant price_per_sqm: {first_variant.price_per_sqm}')
            else:
                combination_info['price_per_sqm'] = 0.0
                _logger.info('No variants found, setting price_per_sqm to 0')

        return combination_info

class ProductProduct(models.Model):
    _inherit = 'product.product'

    price_per_sqm = fields.Float(string='Price per Squaremeter', compute='_compute_price_per_sqm')
    display_sqm = fields.Boolean(related='product_tmpl_id.display_sqm')

    @api.depends('list_price', 'product_template_attribute_value_ids')
    def _compute_price_per_sqm(self):
        for item in self:
            sqm = 0
            _logger.info(f'Computing price_per_sqm for product {item.name}')
            
            for record in item.product_template_attribute_value_ids:
                _logger.info(f'Checking attribute: {record.attribute_id.name}, is_sqm: {record.attribute_id.is_sqm}')
                if record.product_attribute_value_id.attribute_id.is_sqm:
                    sqm = record.product_attribute_value_id.sqm
                    _logger.info(f'Found sqm value: {sqm}')
                    break
            
            if sqm:
                # Get the price directly from the product first
                price = item.list_price
                _logger.info(f'Initial price: {price}')
                
                # Get website
                website = self.env['website'].get_current_website()
                
                # Get the pricelist
                pricelist = website.pricelist_id
                if pricelist:
                    price = pricelist._get_product_price(item, 1.0, currency=website.currency_id)
                    _logger.info(f'Price after pricelist: {price}')
                
                # Get taxes
                taxes = item.taxes_id.filtered(lambda t: t.company_id == self.env.company)
                if taxes:
                    fpos = website.fiscal_position_id
                    if fpos:
                        taxes = fpos.map_tax(taxes)
                    price_taxed = taxes.compute_all(price, website.currency_id, 1.0, item)['total_included']
                    _logger.info(f'Price after taxes: {price_taxed}')
                    price = price_taxed
                
                # Calculate price per sqm
                item.price_per_sqm = price / sqm if sqm else 0
                _logger.info(f'Final price_per_sqm: {item.price_per_sqm}')
            else:
                item.price_per_sqm = 0
                _logger.info('No sqm value found, setting price_per_sqm to 0')


class ProductAttribute(models.Model):
    _inherit = 'product.attribute'

    is_sqm = fields.Boolean(string='Is Square Meter')


class ProductAttributeValue(models.Model):
    _inherit = 'product.attribute.value'

    sqm = fields.Float(string='Square Meter')


class PricelistItem(models.Model):
    _inherit = 'product.pricelist.item'

    price_per_sqm = fields.Float(
        string='Price per Squaremeter', 
        related='product_id.price_per_sqm', 
        readonly=True
    )


class Pricelist(models.Model):
    _inherit = 'product.pricelist'

    def _compute_price_rule(self, products, quantity, **kwargs):
        """Inherit to handle price per square meter in pricelist rules"""
        results = super()._compute_price_rule(products, quantity, **kwargs)
        return results
