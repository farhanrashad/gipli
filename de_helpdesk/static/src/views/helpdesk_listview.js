/** @odoo-module **/

import { HelpdeskDashBoard } from '@de_helpdesk/views/helpdesk_dashboard';
import { registry } from '@web/core/registry';
import { listView } from '@web/views/list/list_view';
import { ListRenderer } from '@web/views/list/list_renderer';

export class HelpdeskDashBoardRenderer extends ListRenderer {};

HelpdeskDashBoardRenderer.template = 'de_helpdesk.HelpdeskListView';
HelpdeskDashBoardRenderer.components = Object.assign({}, ListRenderer.components, { HelpdeskDashBoard });

export const HelpdeskDashBoardListView = {
    ...listView,
    Renderer: HelpdeskDashBoardRenderer,
};

registry.category("views").add("helpdesk_dashboard_list", HelpdeskDashBoardListView);
