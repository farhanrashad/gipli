/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { AttendeeCalendarModel } from "@calendar/views/attendee_calendar/attendee_calendar_model";

patch(AttendeeCalendarModel.prototype, {
    async onCalendlyButtonClick() {
        const rpc = useService("rpc");
        const notification = useService("notification");

        try {
            await rpc({
                model: 'res.users',
                method: '_sync_all_calendly_events',
                args: [[]], // Pass any necessary arguments here
            });
            // Success message (optional)
            notification.add(
                _t("Method called successfully."),
                {
                    title: _t("Success"),
                    type: "success",
                },
            );
        } catch (error) {
            // Error handling (optional)
            console.error("Error calling method:", error);
            notification.add(
                _t("An error occurred while calling the method."),
                {
                    title: _t("Error"),
                    type: "danger",
                },
            );
        }
    },
});
