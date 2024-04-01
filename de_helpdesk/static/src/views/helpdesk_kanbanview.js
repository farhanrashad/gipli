/** @odoo-module **/

import { HelpdeskDashBoard } from '@de_helpdesk/views/helpdesk_dashboard';
import { registry } from '@web/core/registry';
import { kanbanView } from '@web/views/kanban/kanban_view';
import { KanbanRenderer } from '@web/views/kanban/kanban_renderer';

export class HelpdeskDashBoardRenderer extends KanbanRenderer {};

HelpdeskDashBoardRenderer.template = 'de_helpdesk.HelpdeskKanbanView';
HelpdeskDashBoardRenderer.components = Object.assign({}, KanbanRenderer.components, { HelpdeskDashBoard });

export const HelpdeskDashBoardKanbanView = {
    ...kanbanView,
    Renderer: HelpdeskDashBoardRenderer,
};

registry.category("views").add("helpdesk_dashboard_kanban", HelpdeskDashBoardKanbanView);
