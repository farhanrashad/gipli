odoo.define('de_school_timetable.gantt_model', function (require) {
"use strict";

var AbstractModel = require('web.AbstractModel');

	return AbstractModel.extend({
	    init: function () {
	        this._super.apply(this, arguments);
	        this.gantt = null;
	    },
	});
});