/** @odoo-module **/

import VariantMixin from "@website_sale/js/sale_variant_mixin";
import publicWidget from "@web/legacy/js/public/public_widget";
import { renderToFragment } from "@web/core/utils/render";

import "@website_sale/js/website_sale";

import { markup } from "@odoo/owl";

/**
 * Addition to the variant_mixin._onChangeCombination
 *
 * This will prevent the user from selecting a quantity that is not available in the
 * stock for that product.
 *
 * It will also display various info/warning messages regarding the select product's stock.
 *
 * This behavior is only applied for the web shop (and not on the SO form)
 * and only for the main product.
 *
 * @param {MouseEvent} ev
 * @param {$.Element} $parent
 * @param {Array} combination
 */

publicWidget.registry.WebsiteSale.include({

_onChangeCombination: function (ev, $parent, combination) {
    this._super.apply(this, arguments);
    var self = this;
    
    console.log("Combination data:", combination);  // Debug log
    
    // Main price update
    var $price = $parent.find(".oe_price .oe_currency_value").first();
    var $default_price = $parent.find(".oe_default_price .oe_currency_value").first();
    
    $price.text(self._priceToStr(combination.list_price));
    $default_price.text(self._priceToStr(combination.list_price));

    // Price per square meter update
    var $pricePerSqm = $parent.find(".price_per_sqm_value > .oe_currency_value");
    console.log("Price per sqm element found:", $pricePerSqm.length);  // Debug log
    console.log("Price per sqm value:", combination.price_per_sqm);    // Debug log
    
    if ($pricePerSqm.length && combination.price_per_sqm !== undefined) {
        $pricePerSqm.text(self._priceToStr(combination.price_per_sqm));
    }

        
        }
        this._toggleDisable($parent, isCombinationPossible);

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

        var rootComponentSelectors = [
            'tr.js_product',
            '.oe_website_sale',
            '.o_product_configurator'
        ];

        // update images only when changing product
        // or when either ids are 'false', meaning dynamic products.
        // Dynamic products don't have images BUT they may have invalid
        // combinations that need to disable the image.
        if (!combination.product_id ||
            !this.last_product_id ||
            combination.product_id !== this.last_product_id) {
            this.last_product_id = combination.product_id;
            self._updateProductImage(
                $parent.closest(rootComponentSelectors.join(', ')),
                combination.display_image,
                combination.product_id,
                combination.product_template_id,
                combination.carousel,
                isCombinationPossible
            );
        }

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

        $parent
            .find('.o_product_tags')
            .first()
            .html(combination.product_tags);

        this.handleCustomValues($(ev.target));
    },

});

export default VariantMixin;
