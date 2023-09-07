odoo.define('de_portal_hr_service.auto_fill_script', function (require) {
    "use strict";

    var core = require('web.core');

    $(document).ready(function () {
        var productField = document.getElementById('product_id');
        var nameField = document.getElementById('name');

        $(productField).on('change', function () {
            var productId = $(this).val();

            if (productId) {
                // Fetch product name using Odoo API
                odoo.rpc('/get_product_name', { product_id: productId }).then(function (result) {
                    nameField.value = 'Modified ' + result;
                });
            } else {
                nameField.value = '';
            }
        });
    });
});
