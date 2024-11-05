from odoo import api, fields, models

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    display_sqm = fields.Boolean(string='Display Square Meter Price')

    def _get_combination_info(self, combination=False, product_id=False, add_qty=1, parent_combination=False, only_template=False):
        """Inherit to add price_per_sqm to the combination info"""
        combination_info = super()._get_combination_info(
            combination=combination,
            product_id=product_id,
            add_qty=add_qty,
            parent_combination=parent_combination,
            only_template=only_template
        )

        if product_id:
            product = self.env['product.product'].browse(product_id)
            combination_info['price_per_sqm'] = product.price_per_sqm
        
        return combination_info


class ProductProduct(models.Model):
    _inherit = 'product.product'

    price_per_sqm = fields.Float(string='Price per Squaremeter', compute='_compute_price_per_sqm')
    display_sqm = fields.Boolean(related='product_tmpl_id.display_sqm')

    def _compute_price_per_sqm(self):
        """Compute the price per square meter including proper tax calculation"""
        for item in self:
            sqm = 0
            for record in item.product_template_attribute_value_ids:
                if record.product_attribute_value_id.attribute_id.is_sqm:
                    sqm = record.product_attribute_value_id.sqm
                    break
            
            if sqm:
                # Get combination info which includes proper tax calculation
                combination_info = item.product_tmpl_id._get_combination_info(
                    product_id=item.id,
                    add_qty=1,
                    only_template=False,
                )
                
                # Use the properly calculated price from combination_info
                # This price already includes taxes based on Odoo's configuration
                price = combination_info['price']
                
                # Calculate price per sqm
                item.price_per_sqm = price / sqm if sqm else 0
            else:
                item.price_per_sqm = 0


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
        
        # The price calculation is now handled in _compute_price_per_sqm
        # through the combination_info mechanism
        return results
