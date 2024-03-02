odoo.define('de_gym.calendar_nutr_schedule_button', function (require) {
    "use strict";
    
    var CalendarController = require('web.CalendarController');
    var CalendarView = require('web.CalendarView');
    var viewRegistry = require('web.view_registry');
    


    var NutrScheduleCalendarView = CalendarView.extend({
        config: _.extend({}, CalendarView.prototype.config, {
            Controller: CalendarButton,
        }),
    });

    viewRegistry.add('nutr_schedule_button_in_calendar', NutrScheduleCalendarView);
});
