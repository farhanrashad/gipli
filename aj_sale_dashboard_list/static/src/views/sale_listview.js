/** @odoo-module **/

import { registry } from "@web/core/registry";
import { listView } from "@web/views/list/list_view";
import { ListRenderer } from "@web/views/list/list_renderer";
import { SaleDashBoard } from '@aj_sale_dashboard_list/views/sale_dashboard';

export class SaleDashBoardRenderer extends ListRenderer {};

SaleDashBoardRenderer.template = 'aj_sale_dashboard_list.SaleListView';
SaleDashBoardRenderer.components= Object.assign({}, ListRenderer.components, {SaleDashBoard})

export const SaleDashBoardListView = {
    ...listView,
    Renderer: SaleDashBoardRenderer,
};

registry.category("views").add("sale_dashboard_list", SaleDashBoardListView);
