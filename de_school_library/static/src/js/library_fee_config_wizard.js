odoo.define('de_school_library.library_fee_config_wizard', function (require) {
    'use strict';

    var core = require('web.core');
    var Dialog = require('web.Dialog');
    var FieldMany2One = require('web.relational_fields').FieldMany2One;

    var _t = core._t;

    FieldMany2One.include({
        _onInput: function () {
            this._super.apply(this, arguments);
            var self = this;

            if (this.name === 'product_id') {
                // Add your custom logic here to open the dialogue or wizard.
                // You can use the 'this.value' to get the selected product_id.
                // Example:
                var product_id = this.value;
                if (product_id) {
                    new Dialog(this, {
                        title: _t("Custom Dialog Title"),
                        size: 'medium',
                        $content: "<p>Custom dialog content for product_id: " + product_id + "</p>",
                        buttons: [
                            {
                                text: _t("Close"),
                                classes: 'btn-secondary',
                                close: true,
                            },
                        ],
                    }).open();
                }
            }
        },
    });
});
