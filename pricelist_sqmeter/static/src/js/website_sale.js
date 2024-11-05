/** @odoo-module **/

import VariantMixin from "@website_sale/js/sale_variant_mixin";
import publicWidget from "@web/legacy/js/public/public_widget";
import { renderToFragment } from "@web/core/utils/render";
import "@website_sale/js/website_sale";
import { markup } from "@odoo/owl";

publicWidget.registry.WebsiteSale.include({
    _onChangeCombination: function (ev, $parent, combination) {
        this._super.apply(this, arguments);
        var self = this;
        
        // Get price elements
        var $price = $parent.find(".oe_price:first .oe_currency_value");
        var $sqmPriceElement = $parent.find(".price_per_sqm .oe_currency_value");
        var $default_price = $parent.find(".oe_default_price:first .oe_currency_value");
        var $optional_price = $parent.find(".oe_optional:first .oe_currency_value");
        
        // Update regular price
        $price.text(self._priceToStr(combination.price));
        
        // Update price per square meter if it exists in the combination info
        if (combination.price_per_sqm !== undefined && $sqmPriceElement.length) {
            $sqmPriceElement.text(self._priceToStr(combination.price_per_sqm));
            $sqmPriceElement.closest('.price_per_sqm').removeClass('d-none');
        } else {
            $sqmPriceElement.closest('.price_per_sqm').addClass('d-none');
        }

        // Handle discounted prices
        if (combination.has_discounted_price && !combination.compare_list_price) {
            $default_price
                .closest('.oe_website_sale')
                .addClass("discount");
            $optional_price
                .closest('.oe_optional')
                .removeClass('d-none')
                .css('text-decoration', 'line-through');
            $default_price.parent().removeClass('d-none');
        } else {
            $default_price
                .closest('.oe_website_sale')
                .removeClass("discount");
            $optional_price.closest('.oe_optional').addClass('d-none');
            $default_price.parent().addClass('d-none');
        }

        // Rest of your existing code...
        var isCombinationPossible = true;
        if (typeof combination.is_combination_possible !== "undefined") {
            isCombinationPossible = combination.is_combination_possible;
        }
        this._toggleDisable($parent, isCombinationPossible);

        $parent
            .find('.product_id')
            .first()
            .val(combination.product_id || 0)
            .trigger('change');

        $parent
            .find('.product_display_name')
            .first()
            .text(combination.display_name);

        $parent
            .find('.js_raw_price')
            .first()
            .text(combination.price_per_sqm)
            .trigger('change');

        this.handleCustomValues($(ev.target));
    },
});

export default VariantMixin;
