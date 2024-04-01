/** @odoo-module */
import { useService } from "@web/core/utils/hooks";

const { Component, onWillStart } = owl;

export class HelpdeskDashBoard extends Component {
    setup() {
        this.orm = useService("orm");
        this.action = useService("action");

        onWillStart(async () => {
            this.helpdeskData = await this.orm.call(
                "project.project",
                "retrieve_dashboard",
            );
        });
    }

    async onActionClicked(e) {
        if (this.showDemo) {
            return;
        }
        const action = e.currentTarget;
        const actionRef = action.getAttribute('name');
        const title = action.dataset.actionTitle || action.getAttribute('title');
        const searchViewRef = action.getAttribute('search_view_ref');
        const buttonContext = action.getAttribute('context') || '';

        if (action.getAttribute('name').includes('de_helpdesk.')) {
            return await this.action.doActionButton({
                resModel: 'project.task',
                name: 'create_action',
                args: JSON.stringify([actionRef, title, searchViewRef]),
                context: '',
                buttonContext,
                type: 'object',
            });
        } else {
            if (['action_view_rating_today', 'action_view_rating_7days'].includes(actionRef)) {
                return this.action.doActionButton({
                    resModel: 'project.task',
                    name: actionRef,
                    context: '',
                    buttonContext,
                    type: 'object',
                });
            }
            return this.action.doAction(actionRef);
        }
    }

    /**
     * This method clears the current search query and activates
     * the filters found in `filter_name` attibute from button pressed
     */
    setSearchContext(ev) {
        let filter_name = ev.currentTarget.getAttribute("filter_name");
        let filters = filter_name.split(',');
        let searchItems = this.env.searchModel.getSearchItems((item) => filters.includes(item.name));
        this.env.searchModel.query = [];
        for (const item of searchItems){
            this.env.searchModel.toggleSearchItem(item.id);
        }
    }
}

HelpdeskDashBoard.template = 'de_helpdesk.HelpdeskDashboard'
