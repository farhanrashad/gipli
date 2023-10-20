odoo.define('de_school_timetable.gantt', function (require) {
"use strict";
var core = require('web.core');
// var Model = require('web.Model');
// var formats = require('web.formats');
var time = require('web.time');
var parse_value = require('web.web_client');
var QWeb = core.qweb;
// var form_common = require('web.form_common');
var view_registry = require('web.view_registry');
var AbstractView = require('web.AbstractView');
var GanttModel = require('de_school_timetable.gantt_model');
var GanttRenderer = require('de_school_timetable.gantt_renderer');
var GanttController = require('de_school_timetable.gantt_controller');
var _t = core._t;
var _lt = core._lt;


var GanttView = AbstractView.extend({
	display_name: _lt('Gantt'),
	template: "GanttView",
	jsLibs: [
			"/de_school_timetable/static/lib/anychart-core.min.js",
			"/de_school_timetable/static/lib/anychart-gantt.min.js"
		],
	icon: 'fa-tasks',
	config: {
        Model: GanttModel,
        Controller: GanttController,
        Renderer: GanttRenderer,
    },
    view_type: "gantt",
	init: function (viewInfo, params) {
		var self = this;
		self.parent_actions = parent.actions
		this._super.apply(this, arguments);
		this.$view = $(QWeb.render('GanttView'));
		this.$loading = this.$view.find('#container');
	},

});
view_registry.add('gantt', GanttView);

return GanttView;

});
