odoo.define('de_apollo_connector.tree_button', function (require) {
    "use strict";
    
    var ListController = require('web.ListController');
    var ListView = require('web.ListView');
    var viewRegistry = require('web.view_registry');
    
    var TreeButton = ListController.extend({
        buttons_template: 'de_apollo_connector.buttons',
        events: _.extend({}, ListController.prototype.events, {
            'click .open_wizard_action_apl_people_search_results': '_OpenWizard',
        }),
        _OpenWizard: function () {
            var self = this;
            this.do_action({
                type: 'ir.actions.act_window',
                res_model: 'apl.people.search.wizard', // Update with your actual model name
                name: 'Search People',
                view_mode: 'form',
                view_type: 'form',
                views: [[false, 'form']],
                target: 'new',
                res_id: false,
            });
        },
    });

    var AplPeopleSearchResultsListView = ListView.extend({
        config: _.extend({}, ListView.prototype.config, {
            Controller: TreeButton,
        }),
    });

    viewRegistry.add('apl_people_search_button_in_tree', AplPeopleSearchResultsListView);
});
