odoo.define('de_hunter_connector.tree_search_buttons', function (require) {
    "use strict";
    
    var ListController = require('web.ListController');
    var ListView = require('web.ListView');
    var viewRegistry = require('web.view_registry');
    
    var TreeButtons = ListController.extend({
        buttons_template: 'de_hunter_connector.search_buttons',
        events: _.extend({}, ListController.prototype.events, {
            'click .open_wizard_action_find_email_results': '_OpenFindEmailWizard',
        }),
        _OpenFindEmailWizard: function () {
            this._openWizard('hunter.find.email.wizard', 'Find Email');
        },
        _openWizard: function (resModel, name) {
            this.do_action({
                type: 'ir.actions.act_window',
                res_model: resModel,
                name: name,
                view_mode: 'form',
                view_type: 'form',
                views: [[false, 'form']],
                target: 'new',
                res_id: false,
            });
        },
    });

    var FindEmailResultsListView = ListView.extend({
        config: _.extend({}, ListView.prototype.config, {
            Controller: TreeButtons,
        }),
    });

    viewRegistry.add('hunter_find_email_button_in_tree', FindEmailResultsListView);
});
