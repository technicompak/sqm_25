odoo.define('@pricelist_sqmeter/js/website_sale', ['@website_sale/js/sale_variant_mixin', '@web/legacy/js/public/public_widget', '@web/core/utils/render', '@website_sale/js/website_sale', '@odoo/owl'], function (require) {
    'use strict';
    let __exports = {};

    const VariantMixin = require("@website_sale/js/sale_variant_mixin")[Symbol.for("default")];
    const publicWidget = require("@web/legacy/js/public/public_widget")[Symbol.for("default")];
    const { renderToFragment } = require("@web/core/utils/render");
    require("@website_sale/js/website_sale");
    const { markup } = require("@odoo/owl");

    publicWidget.registry.WebsiteSale.include({
        _onChangeCombination: function (ev, $parent, combination) {
            this._super.apply(this, arguments);
            var self = this;
            
            console.log("Combination data:", combination);
            
            var $price = $parent.find(".oe_price:first .oe_currency_value");
            var $default_price = $parent.find(".oe_default_price:first .oe_currency_value");
            var $optional_price = $parent.find(".oe_optional:first .oe_currency_value");
            
            $price.text(self._priceToStr(combination.list_price));
            $default_price.text(self._priceToStr(combination.list_price));

            // Price per square meter update
            var $pricePerSqm = $parent.find("div[style*='font-size: 1rem'] > .oe_currency_value");
            if ($pricePerSqm.length && combination.price_per_sqm !== undefined) {
                $pricePerSqm.text(self._priceToStr(combination.price_per_sqm));
            }

            var isCombinationPossible = true;
            if (typeof combination.is_combination_possible !== "undefined") {
                isCombinationPossible = combination.is_combination_possible;
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

    __exports[Symbol.for("default")] = VariantMixin;
    return __exports;
});
