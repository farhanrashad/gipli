/** @odoo-module **/

import { TimetableGantt } from '@de_school_timetable/views/timetable_template';
import { registry } from '@web/core/registry';
import { ganttView } from '@web/views/gantt/kanban_view';
import { KanbanRenderer } from '@web/views/kanban/kanban_renderer';

export class HelpdeskDashBoardRenderer extends KanbanRenderer {};

HelpdeskDashBoardRenderer.template = 'de_helpdesk.HelpdeskKanbanView';
HelpdeskDashBoardRenderer.components = Object.assign({}, KanbanRenderer.components, { HelpdeskDashBoard });

export const HelpdeskDashBoardKanbanView = {
    ...kanbanView,
    Renderer: HelpdeskDashBoardRenderer,
};

registry.category("views").add("helpdesk_dashboard_kanban", HelpdeskDashBoardKanbanView);
