odoo.define('de_portal_hr_service.dynamic_filter', function (require) {
    "use strict";

    var core = require('web.core');
    var publicWidget = require('web.public.widget');

    publicWidget.registry.DynamicFilter = publicWidget.Widget.extend({
        selector: '.select2-dynamic',
        events: {
            'focus': '_onFocus',
        },

        _onFocus: function (event) {
            var $target = $(event.currentTarget);
            var model = $target.data('model');
            var field = $target.data('field');
            var searchFields = $target.data('search-fields');
            var domain = $target.data('domain');
            var labelFields = $target.data('label-fields');

            $target.select2({
                ajax: {
                    url: '/dynamic_filter',
                    dataType: 'json',
                    delay: 250,
                    data: function (params) {
                        return {
                            model: model,
                            field: field,
                            search_fields: searchFields,
                            domain: domain,
                            label_fields: labelFields,
                            q: params.term
                        };
                    },
                    processResults: function (data) {
                        return {
                            results: data
                        };
                    },
                    cache: true
                },
                minimumInputLength: 1
            });
        },
    });

    return publicWidget.registry.DynamicFilter;
});
