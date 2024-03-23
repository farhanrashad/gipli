# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.tools.misc import get_lang
from odoo.exceptions import UserError, ValidationError
from zoomus import ZoomClient
from datetime import timedelta
import datetime
import json
import pytz
from odoo import tools
from ast import literal_eval
import base64
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import time
import babel.dates
from datetime import datetime, time


CUSTOM_VIRTUAL_FORMATE = "%Y%m%d%H%M%S"


def convert_cal_id_to_actual_id(id_of_calander=None, date_time_with=False):
    """
        Recurring Events Ids which is type of string will convert to actual or real event id
        which would be type of int.
        example: if the id is 5-345398239000 it will be converted as 5.

        we have to pass the calender id, date_time_with value. Real event id will be return
    """

    # print('function')

    if id_of_calander and isinstance(id_of_calander, str):

        res = [bit for bit in id_of_calander.split('-') if bit]
        if len(res) == 2:
            real_id = res[0]
            if date_time_with:
                actual_date = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT, time.strptime(res[1], CUSTOM_VIRTUAL_FORMATE))
                start = datetime.datetime.strptime(actual_date, DEFAULT_SERVER_DATETIME_FORMAT)
                end = start + timedelta(hours=date_time_with)
                return (int(real_id), actual_date, end.strftime(DEFAULT_SERVER_DATETIME_FORMAT))
            return int(real_id)
    return id_of_calander and int(id_of_calander) or id_of_calander


def check_calender_id(id_of_the_record):
    return len(str(id_of_the_record).split('-')) != 1


def convert_actual_id_to_cal_id(id_of_the_record, date_t):
    # print('funtion')

    return '%s-%s' % (id_of_the_record, date_t.strftime(CUSTOM_VIRTUAL_FORMATE))


class Meeting(models.Model):
    """
    Creating meetings
    """

    _inherit = 'calendar.event'

    is_zoom_meeting = fields.Boolean("Zoom Meeting")
    zoom_occurrence_list = fields.Char('Zoom Occurrence list')
    meeting_pswd = fields.Char('Meeting Password')
    video_host = fields.Boolean(string='Video Host')
    video_participant = fields.Boolean(string='Video Participant')
    enable_join_bf_host = fields.Boolean("Enable join before host")
    mute_participants_upon_entry = fields.Boolean('Mute participants upon entry')
    enable_waiting_room = fields.Boolean("Enable waiting room")
    auto_recording = fields.Boolean('Record the meeting automatically on the local computer')
    join_url = fields.Char("Join URL", default='')
    start_url = fields.Char("Start URL")
    meeting_id = fields.Char('Meeting ID')
    host_id = fields.Char('Host ID')
    external_participants = fields.One2many('zoom_meeting.external_user', 'event_id', string='External Participant')
    visible_factor = fields.Boolean("Visibility Check", compute='is_visible_test')
    update_single_instance = fields.Boolean('Update single instance')
    user_visibility = fields.Boolean('User visibility', compute='is_user_visible_test')
    join_visible_factor = fields.Boolean("Join Meeting Visibility Check", compute='is_join_visibile_test')
    todays_meeting = fields.Html(compute='check_today_events', string='Meeting')
    end_type = fields.Selection([
        ('count', 'Number of occurrences'),
        ('end_date', 'End date')
    ], string='Recurrence Termination', default='count')

    @api.onchange('start_datetime')
    def meeting_datetime_start(self):
        # print('funtion')
        self.check_today_events()

    def check_today_events(self):
        # print('funtion')

        self.todays_meeting = ''
        if not self.create_uid or (self.create_uid and self.create_uid.id == self.env.user.id):
            if not self.recurrency and self.start_datetime and self.is_zoom_meeting:
                local_date_time = self.local_time_fun(self.start_datetime)
                if not local_date_time:
                    raise UserError('You Have Not Selected TimeZone In User Profile!')
                local_time = datetime.strptime(local_date_time, "%Y-%m-%d %H:%M:%S")
                start_date = local_time.strftime("%Y-%m-%d").strip() + " 00:00:00"
                tz = pytz.timezone(self.env.user.tz)
                start_date_strip = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
                start_tz_localize = tz.localize(start_date_strip, is_dst=None)
                utc_from_date = start_tz_localize.astimezone(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")
                meet_end_date = local_time.date() + timedelta(days=1)
                end_date = meet_end_date.strftime("%Y-%m-%d").strip() + " 00:00:00"
                en_date_strip = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
                end_tz_localize = tz.localize(en_date_strip, is_dst=None)
                utc_end_date = end_tz_localize.astimezone(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")
                todays_meeting = self.env['calendar.event'].search([('id', '!=', self.id), ('is_zoom_meeting', '=', True), ('create_uid', '=', self.env.user.id), ('recurrency', '!=', True), ('start_datetime', '>=', utc_from_date), ('start_datetime', '<', utc_end_date)])
                if todays_meeting:
                    todays_meeting_description = '<font size=4 color=blue><b>Normal Zoom Meetings created for the day</b></font>'+"<br/>"+"<br/>"
                    for today_meeting in todays_meeting:
                        meeting_date = self.local_time_userformat(today_meeting.start_datetime)
                        description = ''
                        description += "<b>Meeting Subject: </b>" + today_meeting.name + "<br/>" + "<b>Time: </b>" + str(meeting_date) +"<br/>" + "<b>Duration: </b>" + str(today_meeting.duration) +"<br/>"+"<br/>"
                        todays_meeting_description += description
                    self.todays_meeting = todays_meeting_description
                else:
                    self.todays_meeting = ''
            else:
                self.todays_meeting = ''

    def is_visible_test(self):
        # print('funtion')

        for record in self:
            record.visible_factor = False
            if record.is_zoom_meeting != True and self.id != False:
                if record.allday == False:
                    record.visible_factor = True

    def is_join_visibile_test(self):
        # print('funtion')

        for record in self:
            record.join_visible_factor = True
            emails = []
            if record.attendee_ids:
                emails = record.attendee_ids.mapped('email')
            if record.external_participants:
                ext_emails = record.external_participants.mapped('email')
                emails.extend(ext_emails)
            if self.env.user.email in emails or self.env.user.id == self.env.user.company_id.zoom_admin_user_id.id or self.env.user.id == record.create_uid.id:
                record.join_visible_factor = False

    def is_user_visible_test(self):
        # print('funtion')

        # Checking the login user is same as meeting created user.
        for record in self:
            record.user_visibility = False
            current_user = record.env.user.id
            if current_user == record.create_uid.id:
                record.user_visibility = True

    @api.constrains('event_tz')
    def timezone_check(self):
        """
         Check Whether the time selected is available in odoo or not.
        """
        # print('funtion')

        for meeting in self:
            if meeting.is_zoom_meeting == True and meeting.event_tz:
               if meeting.event_tz not in ['Pacific/Midway','Pacific/Pago_Pago','Pacific/Honolulu','America/Anchorage','America/Vancouver',
                                       'America/Los_Angeles','America/Tijuana','America/Edmonton','America/Denver','America/Phoenix','America/Mazatlan',
                                       'America/Winnipeg','America/Regina','America/Chicago','America/Mexico_City','America/Guatemala','America/El_Salvador',
                                       'America/Managua','America/Costa_Rica','America/Montreal','America/New_York','America/Indianapolis','America/Panama',
                                       'America/Bogota','America/Lima','America/Halifax','America/Puerto_Rico','America/Caracas','America/Santiago','America/St_Johns',
                                       'America/Montevideo','America/Araguaina','America/Argentina/Buenos_Aires','America/Godthab','America/Sao_Paulo','Atlantic/Azores',
                                       'Canada/Atlantic','Atlantic/Cape_Verde','UTC','Etc/Greenwich','Europe/Belgrade','CET','Atlantic/Reykjavik','Europe/Dublin','Europe/London',
                                       'Europe/Lisbon','Africa/Casablanca','Africa/Nouakchott','Europe/Oslo','Europe/Copenhagen','Europe/Brussels','Europe/Berlin','Europe/Helsinki',
                                       'Europe/Amsterdam','Europe/Rome','Europe/Stockholm','Europe/Vienna','Europe/Luxembourg','Europe/Paris','Europe/Zurich','Europe/Madrid','Africa/Bangui',
                                       'Africa/Algiers','Africa/Tunis','Africa/Harare','Africa/Nairobi','Europe/Warsaw','Europe/Prague','Europe/Budapest','Europe/Sofia','Europe/Istanbul','Europe/Athens',
                                       'Europe/Bucharest','Asia/Nicosia','Asia/Beirut','Asia/Damascus','Asia/Jerusalem','Asia/Amman','Africa/Tripoli','Africa/Cairo','Africa/Johannesburg','Europe/Moscow',
                                       'Asia/Baghdad','Asia/Kuwait','Asia/Riyadh','Asia/Bahrain','Asia/Qatar','Asia/Aden','Asia/Tehran','Africa/Khartoum','Africa/Djibouti','Africa/Mogadishu','Asia/Dubai',
                                       'Asia/Muscat','Asia/Baku','Asia/Kabul','Asia/Yekaterinburg','Asia/Tashkent','Asia/Calcutta','Asia/KathmanduAsia/Novosibirsk','Asia/Almaty','Asia/Dacca','Asia/Krasnoyarsk',
                                       'Asia/Dhaka','Asia/Bangkok','Asia/Saigon','Asia/Jakarta','Asia/Irkutsk','Asia/Shanghai','Asia/Hong_Kong','Asia/Taipei','Asia/Kuala_Lumpur','Asia/Singapore','Australia/Perth',
                                       'Asia/Yakutsk','Asia/Seoul','Asia/Tokyo','Australia/Darwin','Australia/Adelaide','Asia/Vladivostok','Pacific/Port_Moresby','Australia/Brisbane','Australia/Sydney','Australia/Hobart',
                                       'Asia/Magadan','SST','Pacific/Noumea','Asia/Kamchatka','Pacific/Fiji','Pacific/Auckland','Asia/Kolkata','Europe/Kiev','America/Tegucigalpa','Pacific/Apia']:
                   raise UserError("Zoom doesn't support timezone %s" % meeting.event_tz)

    @api.constrains('rrule_type')
    def weekday_check(self):
        # print('funtion')

        for meeting in self:
            if meeting.rrule_type == 'weekly':
                    weekday_list = []
                    weekday_list.append(self.mo)
                    weekday_list.append(self.tu)
                    weekday_list.append(self.th)
                    weekday_list.append(self.we)
                    weekday_list.append(self.fr)
                    weekday_list.append(self.sa)
                    weekday_list.append(self.su)
                    flag = False
                    for weekday in weekday_list:
                        if weekday == True:
                            flag = True
                    if flag == False:
                        raise UserError("Select atleast one day in week")

    @api.constrains('is_zoom_meeting')
    def rruleproperty_check(self):
        """
            Checking the years whether is available in zoom or not. Otherwise raise exception.
        """
        # print('funtion')

        for meeting in self:
            if meeting.is_zoom_meeting == True:
                if meeting.rrule_type == 'yearly':
                    raise UserError("Zoom doesn't support recurrence option Years")

    @api.onchange('recurrency')
    def recurrency_check(self):
        # print('funtion')

        self.rrule_type = ''
        if self.recurrency:
            self.interval = 1
        else:

            self.interval = ''
        self.end_type = ''
        if self.recurrency:
            self.count = 1
        else:
            self.count = ''

        self.final_date = ''
        self.month_by = ''
        self.byday = ''
        self.week_list = ''
        self.day = ''
        self.we = False
        self.th = False
        self.mo = False
        self.tu = False
        self.sa = False
        self.su = False
        self.fr = False

    @api.onchange('rrule_type')
    def rruletype_check(self):
        # print('funtion')

        if self.rrule_type == 'daily':
            self.month_by = ''
            self.byday = ''
            self.week_list = ''
            self.day = ''
            self.we = False
            self.th = False
            self.mo = False
            self.tu = False
            self.sa = False
            self.su = False
            self.fr = False
            # self.mo, self.tu, self.we, self.th, self.fr, self.sa, self.su = False

        elif self.rrule_type == 'weekly':
            self.month_by = ''
            self.byday = ''
            self.week_list = ''
            self.day = ''

        elif self.rrule_type == 'monthly':
            self.we = False
            self.th = False
            self.mo = False
            self.tu = False
            self.sa = False
            self.su = False
            self.fr = False
            # self.mo, self.tu, self.we, self.th, self.fr, self.sa, self.su = False

        else:
            self.end_type = ''
            self.count = ''
            self.final_date = ''
            self.month_by = ''
            self.byday = ''
            self.week_list = ''
            self.day = ''
            self.we = False
            self.th = False
            self.mo = False
            self.tu = False
            self.sa = False
            self.su = False
            self.fr = False
            # self.mo, self.tu, self.we, self.th, self.fr, self.sa, self.su = False

    @api.onchange('end_type')
    def endtype_check(self):
        # print('funtion')

        if self.end_type == "count":
            self.final_date = ''
        elif self.end_type == "end_date":
            self.count = ''

    @api.onchange('month_by')
    def monthby_check(self):
        # print('funtion')

        if self.end_type == "day":
            self.day = ''
        elif self.end_type == "date":
            self.byday = ''
            self.week_list = ''

    @api.onchange('is_zoom_meeting')
    def zoommetingchange(self):
        # print('funtion')

        if self.is_zoom_meeting == True:
            self.allday = False
        self.meeting_id = ''
        self.join_url = ''
        self.start_url = ''
        self.host_id = ''
        self.meeting_pswd = ''
        self.zoom_occurrence_list = ''

    def local_time_fun(self, date):

        """
        Take UTC Timezone and Convert it to local Timezone
        """
        # print('funtion')

        user_tz = self.env.user.tz
        if user_tz:
            local = pytz.timezone(user_tz)
            is_var_str = isinstance(date, str)
            if is_var_str != True:
                date = date.strftime("%Y-%m-%d %H:%M:%S")
            display_date_result = datetime.strftime(pytz.utc.localize(datetime.strptime(date, DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local), "%Y-%m-%d %H:%M:%S")
            return display_date_result
        else:
            UserError("Please set user timezone")

    def local_time_userformat(self, date):
        """
        Convert utc time to local timezone.
        """
        # print('funtion')

        user_tz = self.env.user.tz
        if user_tz:
            local = pytz.timezone(user_tz)
            user_lang = self.env['res.lang'].search([('code','=',self.env.user.lang)])
            if user_lang:
                date_format_user = user_lang[0].date_format + ' ' + user_lang[0].time_format
            else:
                date_format_user = "%Y-%m-%d %H:%M:%S"
            is_var_str = isinstance(date, str)
            if is_var_str != True:
                date = date.strftime("%Y-%m-%d %H:%M:%S")
            display_date_result = datetime.strftime(pytz.utc.localize(datetime.strptime(date, DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local), date_format_user)
            return display_date_result
        else:
            UserError("Please set user timezone")

    def meeting_join_fun(self):
        """
        Allow the internal odoo users called attendee and the external users to join the meet.
        """
        # print('funtion')

        if self.sudo().join_url:
            return {
                "url": self.join_url,
                "type": "ir.actions.act_url"
            }

    def meeting_start_fun(self):
        """
            Who have created a meeting can join the meeting, start the meeting.
        """
        # print('funtion')

        if self.sudo().start_url:
            return {
                "url": self.start_url,
                "type": "ir.actions.act_url"
            }

    @api.model
    def create(self, values):
        """
          It will create the meeting, delete or unlink the zoom meeting etc.
        """
        # print('funtion')

        self = self.with_context(zoom_meeting_create=True)
        res = super(Meeting, self).create(values)
        if self._context.get('zoom_meet_unlink') == True or self._context.get('zoom_create')==True:
            pass
        else:
            # Updating zoom meeting response to current record
            if res.is_zoom_meeting == True:
                try:
                    data_dict = self.create_zoom_meeting(res)
                except UserError as e:
                    # let UserErrors (messages) bubble up
                    raise e
                except Exception as e:
                    raise UserError(_('Zoom API Exception! \n %s') % e)
                res.start_url = data_dict['start_url']
                res.join_url = data_dict['join_url']
                res.meeting_id = data_dict['meeting_id']
                occurrence_list=data_dict['occurrence_list']
                records = self.env['calendar.event'].search([('meeting_id', '=', data_dict['meeting_id'])])
                if occurrence_list:
                    res.zoom_occurrence_list = self.check_zoom_list_of_occurence(records, occurrence_list,res,res.meeting_id)
                if data_dict['http_status'] == 201:
                    pass
                else:
                    if data_dict['http_status'] == 429:
                        raise UserError(
                            "You have exceed the daily rate limit(100) of Meeting Create/Update API requests permitted."
                            "for this particular user. Try again later or get paid license")
                    raise UserError("Something went wrong ! You can't create meeting")
                # Mail notification to attendees and external users
                if self.env.user.company_id.meeting_event_mail_notification == True:
                    if self._context.get('no_invite_mail') != True:
                        current_user = self.env.user
                        if res.attendee_ids:
                            to_notify = res.attendee_ids.filtered(lambda a: a.email != current_user.email)
                            to_notify.email_notification_to_participents_attendi(res,
                                                                    'calendar.calendar_template_meeting_invitation')
                        if res.external_participants:
                            for participant_id in res.external_participants:
                                if participant_id.mail_sent != True:
                                    participant_id.email_for_outer_zoom_people(res,
                                                                                       'de_zoom_connector.calendar_template_external_user_meeting_invitation')
                                    participant_id.mail_sent = True
        return res

    def check_zoom_list_of_occurence(self, records, occurrence_list, res_obj, meeting_id):

        # print('funtion')

        client = self.api_connection_fun()
        zoom_occurrence_list = []
        for rec in records:
            for occurrence in occurrence_list:
                zoom_start_datetime = datetime.strptime(occurrence['start_time'], "%Y-%m-%dT%H:%M:%SZ")
                zoom_start_datetime_str = zoom_start_datetime.strftime("%Y-%m-%d %H:%M")
                zoom_start_datetime = datetime.strptime(zoom_start_datetime_str, "%Y-%m-%d %H:%M")
                start_datetime = rec.start_datetime
                is_var_str = isinstance(start_datetime, str)
                if is_var_str != True:
                    start_datetime_str = start_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")
                    start_datetime = self.date_time_conversion_time_zone(start_datetime_str, res_obj.event_tz)
                else:
                    start_datetime = datetime.strptime(start_datetime, "%Y-%m-%d %H:%M:%S")
                    start_datetime = start_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")
                    start_datetime = self.date_time_conversion_time_zone(start_datetime, res_obj.event_tz)
                start_datetime = datetime.strptime(start_datetime, "%Y-%m-%dT%H:%M:%SZ")
                start_datetime_str = start_datetime.strftime("%Y-%m-%d %H:%M")
                start_datetime = datetime.strptime(start_datetime_str, "%Y-%m-%d %H:%M")

                if start_datetime == zoom_start_datetime:
                    zoom_occurrence_list.append({'occurrence_id': occurrence['occurrence_id'], 'id': rec.id})
        for rec in records:
            for occurrence in occurrence_list:
                flag = False
                for zoom_occurrence in zoom_occurrence_list:
                    if zoom_occurrence['occurrence_id'] == occurrence['occurrence_id']:
                        flag = True
                if flag == False:
                    client.meeting.delete(id = meeting_id, occurrence_id = occurrence['occurrence_id'])
        return zoom_occurrence_list

    def create_zoom_meeting(self, res):
        """
        It will create the zoom meeting using the python sdk and check the record and also stores
        the xoom responce.
        """
        # print('funtion')

        client = self.api_connection_fun()
        user_id = self.env.user.zoom_login_user_id
        if user_id:
            if res.recurrency == True:
                    meeting_type = 8
            else:
                meeting_type = 2
            duration = ''
            if res.duration:
                duration = res.duration * 60
            auto_recording = 'none'
            if res.auto_recording == True:
                auto_recording = 'local'
            weekdays_list = []
            if res.mo == True:
                weekdays_list.append(2)
            if res.tu == True:
                weekdays_list.append(3)
            if res.we == True:
                weekdays_list.append(4)
            if res.th == True:
                weekdays_list.append(5)
            if res.fr == True:
                weekdays_list.append(6)
            if res.sa == True:
                weekdays_list.append(7)
            if res.su == True:
                weekdays_list.append(1)

            weeklist = ""
            if res.week_list == "SU":
                weeklist = 1
            elif res.week_list == "MO":
                weeklist = 2
            elif res.week_list == "TU":
                weeklist = 3
            elif res.week_list == "WE":
                weeklist = 4
            elif res.week_list == "TH":
                weeklist = 5
            elif res.week_list == "FR":
                weeklist = 6
            elif res.week_list == "SA":
                weeklist = 7
            recur_type = ''
            if res.rrule_type == 'daily':
                recur_type = 1
            elif res.rrule_type == 'weekly':
                recur_type = 2
            elif res.rrule_type == 'monthly':
                recur_type = 3
            final_datetime = ''
            if res.final_date:
                final_datetime = res.final_date
            if final_datetime:
                is_str_final_date = isinstance(final_datetime, str)
                final_time = res.start_datetime.time()
                if str(is_str_final_date) != "True":
                    final_date = final_datetime
                    final_datetime = datetime.combine(final_datetime, final_time)
                else:
                    final_date = datetime.strptime(final_datetime, "%Y-%m-%d").date()
                    final_datetime = datetime.strptime(final_datetime, "%Y-%m-%d")
                    final_datetime = datetime.combine(final_datetime, final_time)
                final_datetime = final_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")
                final_datetime = self.date_time_conversion_time_zone(final_datetime,res.event_tz)
                local = pytz.timezone(res.event_tz)
                display_datetime = datetime.strftime(pytz.utc.localize(datetime.strptime(final_datetime, "%Y-%m-%dT%H:%M:%SZ")).astimezone(local), "%Y-%m-%dT%H:%M:%SZ")
                display_datetime = datetime.strptime(display_datetime, "%Y-%m-%dT%H:%M:%SZ")
                display_datetime = display_datetime + timedelta(minutes=duration)
                if display_datetime.date() > final_date:
                    final_datetime = datetime.strptime(final_datetime, "%Y-%m-%dT%H:%M:%SZ")
                    final_datetime = final_datetime - timedelta(days=1)
                    final_datetime = final_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")
            recurrence = {"type": recur_type}
            if res.rrule_type == 'daily' or res.rrule_type == 'weekly' or res.rrule_type == 'monthly':
                recurrence.update({
                    "repeat_interval": res.interval,
                })
                if res.end_type == "count":
                    recurrence.update({
                        "end_times": res.count,
                    })
                elif res.end_type == "end_date":
                    recurrence.update({
                        "end_date_time": final_datetime,
                    })
            if res.rrule_type == 'weekly':
                recurrence.update({
                    "weekly_days": str(weekdays_list)[1:-1],
                })
            if res.rrule_type == 'monthly':
                if res.month_by == 'date':
                    recurrence.update({
                        "monthly_day": res.day,
                    })
                else:
                    recurrence.update({
                        "monthly_week": res.byday,
                        "monthly_week_day": weeklist,
                    })
            start_datetime = res.start_datetime
            start_datetime_str = start_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")
            start_datetime = self.date_time_conversion_time_zone(start_datetime_str,res.event_tz)
            start_datetime = datetime.strptime(start_datetime, "%Y-%m-%dT%H:%M:%SZ")
            kwargs = {
                'topic': res.name,
                'type': meeting_type,
                "password": res.meeting_pswd,
                "start_time": start_datetime,
                "duration": duration,
                "timezone": res.event_tz,
                "agenda": res.description or '',
                "settings": {
                    "host_video": res.video_host or False,
                    "join_before_host": res.enable_join_bf_host or False,
                    "mute_upon_entry": res.mute_participants_upon_entry or False,
                    "participant_video": res.video_participant or False,
                    "waiting_room": res.enable_waiting_room or False,
                    "auto_recording": auto_recording,
                },

            }
            if res.rrule_type != 'no_fixed_time' and res.recurrency == True:
                kwargs.update({"recurrence": recurrence})

            meeting_res = client.meeting.create(user_id=user_id, **kwargs)
            http_status = meeting_res.status_code
            if http_status == 400:
                raise UserError(
                    _('Zoom API Exception:\n Invalid/Missing Data - Validation Failed on Meeting Values,Passwords...'))

            result = json.loads(meeting_res.content.decode('utf-8'))
            occurrence_list = []
            start_url = ''
            join_url = ''
            meeting_id = ''
            host_id = ''
            if http_status == 201:
                start_url = result['start_url']
                join_url = result['join_url']
                meeting_id = result['id']
                host_id = result['host_id']
                response = client.meeting.get(id=meeting_id, show_previous_occurrences=True)
                get_result = json.loads(response.content.decode('utf-8'))
                if get_result.get('occurrences'):
                    occurrence_list = get_result.get('occurrences')
            data_dict = {
                'join_url': join_url,
                'start_url': start_url,
                'http_status': http_status,
                'meeting_id': meeting_id,
                'host_id': host_id,
                'occurrence_list': occurrence_list
            }

            return data_dict

    def api_connection_fun(self):

        """
         Test Connection with JWt App
        """

        # print('function')

        company_rec = self.env.user.company_id
        if company_rec.api_key and company_rec.api_secret:
            try:
                client = ZoomClient(company_rec.api_key, company_rec.api_secret)

            except Exception as e:
                raise UserError(_('API credential invalid', e))
            if self.env.user.zoom_login_email:
                users = client.user.list()
                if users.status_code == 200:
                    user_response = json.loads(users.content.decode('utf-8'))
                    all_users = user_response['users']
                    zoom_user = False
                    for all_user in all_users:
                        if all_user['email'] == self.env.user.zoom_login_email:
                            if all_user['status'] == 'active':
                                zoom_user = True
                                self.env.user.zoom_login_user_id = all_user['id']
                                self.env.user.zoom_user_timezone = all_user['timezone']
                                if not all_user['timezone']:
                                    raise UserError(_('Please set zoom user timezone'))
                                break;
                            else:
                                raise UserError(_('Invalid zoom user'))

                    if not zoom_user:
                        raise UserError(_('Invalid zoom user'))
                else:
                    raise UserError(_('Zoom API Exception'))

            else:
                raise UserError(_('Invalid zoom user'))

            return client
        else:
            raise UserError(_(
                'API credential invalid'))

    def convert_to_datetime(self, date):
        # print('funtion')

        if date:
            is_var_str = isinstance(date, str)
            if str(is_var_str) == "True":
                date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        return date

    def write(self, values):

        """
                - zoom_meeting_create,zoom_meet_unlink,zoom_write are restrict to access zoom api

        """
        # print('funtion')

        super(Meeting, self).write(values)
        zoom_meeting = False
        for meeting in self:
            if values.get('is_zoom_meeting') and values['is_zoom_meeting'] or meeting.is_zoom_meeting == True:
                if self.env.user.id != meeting.create_uid.id and self.env.user.id != self.env.user.company_id.zoom_admin_user_id.id:
                    raise UserError("You didn't have permission to edit this meeting.")

                zoom_meeting = True
                rrule_type = values.get('rrule_type') and values['rrule_type'] or meeting.rrule_type
                if rrule_type == 'yearly':
                    raise UserError("Zoom doesn't support recurrence option Years")

            # Except zoom meeting : Meeting updated notification send to attendees
            if self._context.get('zoom_meeting_create') != True:
                if values.get('is_zoom_meeting') and values['is_zoom_meeting'] or meeting.is_zoom_meeting != True:
                    if self.env.user.company_id.meeting_event_mail_notification == True:
                        if (values.get('start_date') or values.get('start_datetime') or
                                (values.get('start') and self.env.context.get('from_ui'))) and values.get('active', True):
                            for meeting in self:
                                if meeting.attendee_ids:
                                    meeting.attendee_ids.email_notification_to_participents_attendi(meeting,
                                                                                       'calendar.calendar_template_meeting_changedate')
        if zoom_meeting:

            #zoom api call only if the api related field are updated
            field_changes = self.api_fields_change_test_check(values)
            if self._context.get('zoom_meet_unlink') == True or self._context.get(
                    'zoom_meeting_create') == True or self._context.get('zoom_write') == True or field_changes != True:
                pass
            else:
                # updating zoom meeting updation response to current record
                try:
                    http_status, occurrence_list = self.zoom_meet_updation(values)
                    if values.get('external_participants'):
                        values.pop('external_participants')
                    self.write_and_update_zoom_fun(http_status, occurrence_list, values)
                except Exception as e:
                    raise UserError(_('Zoom API Exception! \n %s') % e)

                recurrency_fields = self._get_recurrent_fields()
                recurrency_change=False
                for field in recurrency_fields:
                    if values.get(field) != None:
                        recurrency_change = True

                # Meeting updated notification send to attendees and external users
                for meeting in self:
                    if self.env.user.company_id.meeting_event_mail_notification == True:
                        if (values.get('is_zoom_meeting') and values['is_zoom_meeting']) or recurrency_change or values.get(
                                'meeting_pswd') or values.get('event_tz') or (
                                values.get('start_date') or values.get('start_datetime') or  values.get('update_single_instance')==True or (
                            values.get('start') and self.env.context.get('from_ui'))) and values.get('active', True) :
                            if meeting.attendee_ids:
                                meeting.attendee_ids.email_notification_to_participents_attendi(meeting,
                                                                                   'calendar.calendar_template_meeting_changedate')
                            if meeting.external_participants:
                                meeting.external_participants.email_for_outer_zoom_people(meeting,
                                                                                              'de_zoom_connector.calendar_template_zoom_external_user_meeting_changedate')
        return True

    def write_and_update_zoom_fun(self, http_status, occurrence_list, values):

        """
        parameter that are given : zoom responce of updation
                                   zoom meeting occureance to current record updatation
                                   zoom meeting id updataion
        """
        # print('funtion')

        self = self.with_context(zoom_write=True)
        meeting_id = self.meeting_id
        if not meeting_id:
            meeting_id = values.get('meeting_id')
            super(Meeting, self).write(values)
        records = self.env['calendar.event'].search([('meeting_id', '=', meeting_id)])
        res_obj=self
        zoom_occurrence_list=[]
        if occurrence_list:
            zoom_occurrence_list = self.check_zoom_list_of_occurence(records, occurrence_list,res_obj,meeting_id)
        if http_status == 204 or 201:
            values.update({'zoom_occurrence_list': zoom_occurrence_list})
            return super(Meeting, self).write(values)
        else:
            if http_status == 429:
                raise UserError("You have exceed the daily rate limit(100) of Meeting Create/Update API requests permitted."
                                "for this particular user. Try again later or get paid license")

            raise UserError("Something went wrong ! You can't update meeting")

    def api_fields_change_test_check(self, values):
        """
        check if the related fileds are updated then it calls zoom api and return true
        """
        # print('funtion')

        is_zoom_meeting = values.get('is_zoom_meeting') and values['is_zoom_meeting']
        recurrency = False
        if 'recurrency' in values:
            recurrency = True
        rrule_type = values.get('rrule_type') and values['rrule_type']
        duration = values.get('duration') and values['duration']
        auto_recording_val = False
        if 'auto_recording' in values:
            auto_recording_val = True
        event_tz = values.get('event_tz') and values['event_tz']
        start_datetime = values.get('start_datetime') and values['start_datetime']
        su = False
        if 'su' in values:
            su = True
        mo = False
        if 'mo' in values:
            mo = True
        tu = False
        if 'tu' in values:
            tu = True
        we = False
        if 'we' in values:
            we = True
        th = False
        if 'th' in values:
            th = True
        fr = False
        if 'fr' in values:
            fr = True
        sa = False
        if 'sa' in values:
            sa = True
        week_list = values.get('week_list')
        final_datetime = values.get('final_date') and values['final_date']
        interval = values.get('interval')
        end_type = values.get('end_type') and values['end_type']
        count = values.get('count') and values['count']
        month_by = values.get('month_by') and values['month_by']
        day = values.get('day')
        byday = values.get('byday')
        name = values.get('name')
        meeting_pswd = values.get('meeting_pswd')
        description = values.get('description')
        video_host = False
        if 'video_host' in values:
            video_host = True
        enable_join_bf_host = False
        if 'enable_join_bf_host' in values:
            enable_join_bf_host = True
        mute_participants_upon_entry=False
        if 'mute_participants_upon_entry' in values:
            mute_participants_upon_entry = True
        video_participant=False
        if 'video_participant' in values:
            video_participant = True
        enable_waiting_room=False
        if 'enable_waiting_room' in values:
            enable_waiting_room = True
        if is_zoom_meeting or recurrency or rrule_type or duration or auto_recording_val or event_tz or start_datetime or su or mo \
            or tu or we or th or fr or sa or week_list or final_datetime or interval or end_type or count or month_by \
            or day or byday or name or meeting_pswd or description or video_host or enable_join_bf_host or mute_participants_upon_entry \
            or video_participant or enable_waiting_room:
            return True
        else:
            return False

    # Zoom meeting updation api
    def zoom_meet_updation(self, values):

        """
        it will update the zoom meeting and return the responce of api
        """
        # print('funtion')

        client = self.api_connection_fun()
        recurrency = values.get('recurrency') and values['recurrency'] or self.recurrency
        rrule_type = values.get('rrule_type') and values['rrule_type'] or self.rrule_type
        if recurrency == True:
                meeting_type = 8
        else:
            meeting_type = 2
        duration_in_min = ''
        duration = values.get('duration') and values['duration'] or self.duration
        if duration:
            duration_in_min = duration * 60
        auto_recording = 'none'
        auto_recording_val = 'auto_recording' in values and values['auto_recording'] or self.auto_recording
        if auto_recording_val == True:
            auto_recording = 'local'
        event_tz = values.get('event_tz') and values['event_tz'] or self.event_tz
        real_id = convert_cal_id_to_actual_id(self.id)
        meeting_origin = self.browse(real_id)
        start_datetime = meeting_origin.start_datetime
        final_time = ''
        if start_datetime:
            is_var_str = isinstance(start_datetime, str)
            if str(is_var_str) == "True":

                start_datetime = datetime.strptime(start_datetime, "%Y-%m-%d %H:%M:%S")
                final_time = start_datetime.time()
            else:
                final_time = start_datetime.time()
        start_datetime_str = start_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")
        start_datetime = self.date_time_conversion_time_zone(start_datetime_str, event_tz)
        start_datetime = datetime.strptime(start_datetime, "%Y-%m-%dT%H:%M:%SZ")
        weekdays_list = []
        if values.get('mo') and values['mo'] or self.mo == True:
            weekdays_list.append(2)
        if values.get('tu') and values['tu'] or self.tu == True:
            weekdays_list.append(3)
        if values.get('we') and values['we'] or self.we == True:
            weekdays_list.append(4)
        if values.get('th') and values['th'] or self.th == True:
            weekdays_list.append(5)
        if values.get('fr') and values['fr'] or self.fr == True:
            weekdays_list.append(6)
        if values.get('sa') and values['sa'] or self.sa == True:
            weekdays_list.append(7)
        if values.get('su') and values['su'] or self.su == True:
            weekdays_list.append(1)
        weeklist = ""
        week_list = values.get('week_list') or self.week_list
        if week_list == "SU":
            weeklist = 1
        elif week_list == "MO":
            weeklist = 2
        elif week_list == "TU":
            weeklist = 3
        elif week_list == "WE":
            weeklist = 4
        elif week_list == "TH":
            weeklist = 5
        elif week_list == "FR":
            weeklist = 6
        elif week_list == "SA":
            weeklist = 7
        recur_type = ''
        if rrule_type == 'daily':
            recur_type = 1
        elif rrule_type == 'weekly':
            recur_type = 2
        elif rrule_type == 'monthly':
            recur_type = 3
        final_datetime = values.get('final_date') and values['final_date'] or self.final_date
        if final_datetime:
            is_str_final_date = isinstance(final_datetime, str)
            if str(is_str_final_date) != "True":
                final_date = final_datetime
                final_datetime = datetime.combine(final_datetime, final_time)
            else:
                final_date = datetime.strptime(final_datetime, "%Y-%m-%d").date()
                final_datetime = datetime.strptime(final_datetime, "%Y-%m-%d")
                final_datetime = datetime.combine(final_datetime, final_time)
            final_datetime = final_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")
            final_datetime = self.date_time_conversion_time_zone(final_datetime, event_tz)
            local = pytz.timezone(event_tz)
            display_datetime = datetime.strftime(
                pytz.utc.localize(datetime.strptime(final_datetime, "%Y-%m-%dT%H:%M:%SZ")).astimezone(local),
                "%Y-%m-%dT%H:%M:%SZ")
            display_datetime = datetime.strptime(display_datetime, "%Y-%m-%dT%H:%M:%SZ")
            display_datetime = display_datetime + timedelta(minutes=duration_in_min)
            if display_datetime.date() > final_date:
                final_datetime = datetime.strptime(final_datetime, "%Y-%m-%dT%H:%M:%SZ")
                final_datetime = final_datetime - timedelta(days=1)
                final_datetime = final_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")

        recurrence = {"type": recur_type, }
        if rrule_type in ('daily', 'weekly', 'monthly'):
            recurrence.update({
                "repeat_interval": values.get('interval') or self.interval,
            })
            if (values.get('end_type') and values['end_type'] or self.end_type) == 'count':
                recurrence.update({
                    "end_times": values.get('count') and values['count'] or self.count,
                })
            else:
                recurrence.update({
                    "end_date_time": final_datetime,
                })
        if rrule_type == 'weekly':
            recurrence.update({
                "weekly_days": str(weekdays_list)[1:-1],
            })
        if rrule_type == 'monthly':
            if values.get('month_by') and values['month_by'] or self.month_by == 'date':
                recurrence.update({
                    "monthly_day": values.get('day') or self.day,
                })
            else:
                recurrence.update({
                    "monthly_week": values.get('byday') or self.byday,
                    "monthly_week_day": weeklist,
                })
        kwargs = {
            'topic': values.get('name') or self.name or '',
            'type': meeting_type,
            'password': values.get('meeting_pswd') or self.meeting_pswd or '',
            "start_time": start_datetime,
            "duration": duration_in_min,
            "timezone": event_tz,
            "agenda": values.get('description') or self.description or '',
            "settings": {
                "host_video": 'video_host' in values and values['video_host'] or self.video_host,
                "join_before_host": 'enable_join_bf_host' in values and values[
                    'enable_join_bf_host'] or self.enable_join_bf_host,
                "mute_upon_entry": 'mute_participants_upon_entry' in values and values[
                    'mute_participants_upon_entry'] or self.mute_participants_upon_entry,
                "participant_video": 'video_participant' in values and values[
                    'video_participant'] or self.video_participant,
                "waiting_room": 'enable_waiting_room' in values and values[
                    'enable_waiting_room'] or self.enable_waiting_room,
                "auto_recording": auto_recording,
            }

        }
        if rrule_type != 'no_fixed_time' and recurrency == True:
            kwargs.update({"recurrence": recurrence})
        http_status = ''
        occurrence_list = {}
        if self.meeting_id:
            response = client.meeting.get(id=self.meeting_id,show_previous_occurrences=True)
            if response.status_code == 200:
                result = client.meeting.update(id=self.meeting_id, **kwargs)
                http_status = result.status_code
            else:
                if http_status == 429:
                    raise UserError(
                        "You have exceed the daily rate limit(100) of Meeting Create/Update API requests permitted."
                        "for this particular user. Try again later or get paid license")
                raise UserError("Something went wrong ! You can't create meeting")
            response = client.meeting.get(id=self.meeting_id,show_previous_occurrences=True)
            get_result = json.loads(response.content.decode('utf-8'))
            values.update({'join_url': get_result.get('join_url'),
                           'start_url': get_result.get('start_url'),})
            occurrence_list = []
            if http_status == 204:
                if get_result.get('occurrences'):
                    occurrence_list = get_result.get('occurrences')
        else:
            user_id = self.env.user.zoom_login_user_id
            if user_id:
                meeting_res = client.meeting.create(user_id=user_id, **kwargs)
                http_status = meeting_res.status_code
                if http_status ==400:
                    raise UserError(_('Zoom API Exception:\n Invalid/Missing Data - Validation Failed on Meeting Values,Passwords...'))

                result = json.loads(meeting_res.content.decode('utf-8'))
                if http_status == 201:
                    response = client.meeting.get(id=result.get('id'), show_previous_occurrences=True)
                    get_result = json.loads(response.content.decode('utf-8'))
                    occurrence_list = []
                    values.update({'join_url': result.get('join_url'),
                                   'start_url': result.get('start_url'),
                                   'meeting_id': result.get('id'),
                                   'host_id': result.get('id'),
                                   'meeting_pswd': result.get('password')})
                    if get_result.get('occurrences'):
                        occurrence_list = get_result.get('occurrences')


                    return http_status, occurrence_list
                else:
                    if http_status == 429:
                        raise UserError(
                            "You have exceed the daily rate limit(100) of Meeting Create/Update API requests permitted."
                            "for this particular user. Try again later or get paid license")
                    raise UserError("Something went wrong ! You can't create meeting")
        return http_status, occurrence_list

    def unlink(self, can_be_deleted=True):
        # print('funtion')

        # Get concerned attendees to notify them if there is an alarm on the unlinked events,
        # as it might have changed their next event notification
        events = self.search([('id', 'in', self.ids), ('alarm_ids', '!=', False)])
        partner_ids = events.mapped('partner_ids').ids
        records_to_exclude = self.env['calendar.event']
        records_to_unlink = self.env['calendar.event'].with_context(recompute=False, zoom_meet_unlink=True)
        for meeting in self:

            if can_be_deleted and not check_calender_id(meeting.id):  # if  ID REAL
                if meeting.recurrent_id:
                    records_to_exclude |= meeting
                else:
                    # int() required because 'id' from calendar view is a string, since it can be calendar virtual id
                    records_to_unlink |= self.browse(int(meeting.id))

            else:
                records_to_exclude |= meeting
                # records_to_unlink |= self.browse(int(meeting.id))

            # Meeting delete notification send to attendees and external users.
            if meeting.is_zoom_meeting==True:
                if self.env.user.id != meeting.create_uid.id and self.env.user.id !=self.env.user.company_id.zoom_admin_user_id.id:
                    raise UserError("You didn't have permission to cancel this meeting.")
                date = self.local_time_fun(meeting.start_datetime or meeting.start_date)
                self.zoom_meet_deletion(meeting)
                if self.env.user.company_id.meeting_event_mail_notification == True and  self._context.get('no_invite_mail')!=True :
                    if meeting.attendee_ids:
                        for attendee_id in meeting.attendee_ids:
                            mail_template_1 = self.env.ref('de_zoom_connector.unlink_meeting_notification_to_attendees')
                            mail_template_1.with_context(date=date).send_mail(attendee_id.id, force_send=True,notif_layout='mail.mail_notification_light')
                    if meeting.external_participants:
                        for participant_id in meeting.external_participants:
                            mail_template_2 = self.env.ref('de_zoom_connector.unlink_meeting_notification_to_external_users')
                            mail_template_2.with_context(date=date).send_mail(participant_id.id, force_send=True,notif_layout='mail.mail_notification_light')

        result = False
        if records_to_unlink:
            result = super(Meeting, records_to_unlink).unlink()
        if records_to_exclude:
            result = records_to_exclude.with_context(dont_notify=True, zoom_meet_unlink=True).write({'active': False,'is_zoom_meeting':False,'meeting_id':'','join_url': '','start_url': '','host_id': '','meeting_pswd':'','zoom_occurrence_list':''})
        # Notify the concerned attendees (must be done after removing the events)
        self.env['calendar.alarm_manager']._notify_next_alarm(partner_ids)

        return result

    # zoom meeting deletion api
    def zoom_meet_deletion(self, meeting):
        """
            Zoom meeting deletion api : using python SDK.
        """
        # print('funtion')

        try:
            client = self.api_connection_fun()
            if meeting.meeting_id:
                zoom_occurrence_list=[]
                if meeting.zoom_occurrence_list :
                    zoom_occurrence_list=literal_eval(meeting.zoom_occurrence_list)
                if zoom_occurrence_list:
                        for occurrence in literal_eval(meeting.zoom_occurrence_list):
                            if occurrence['id'] == meeting.id:
                                response = client.meeting.get(id=meeting.meeting_id,occurrence_id=occurrence['occurrence_id'])
                                if response.status_code == 200:
                                    client.meeting.delete(id=meeting.meeting_id,occurrence_id=occurrence['occurrence_id'])
                else:
                    response = client.meeting.get(id=meeting.meeting_id,show_previous_occurrences=True)
                    if response.status_code == 200:
                        client.meeting.delete(id=meeting.meeting_id)

        except Exception as e:
            raise UserError(_('Zoom API Exception! \n %s') % e)

    def zoom_meeting_cancel_fun(self):
        # print('funtion')

        self.unlink()
        if self.env.context.get('default_is_zoom_meeting'):

            list_view_id = self.env.ref('de_zoom_connector.view_calendar_event_tree_inherit').id
            form_view_id = self.env.ref('de_zoom_connector.action_zoom_calendar_event').id
            return {
                'type': 'ir.actions.act_url',
                'url': '/web#action=%s&model=calendar.event&view_type=list&cids=&menu_id=%s' %(form_view_id,list_view_id),
                'target': 'self',

            }
        else:
            list_view_id = self.env.ref('calendar.view_calendar_event_tree').id
            form_view_id = self.env.ref('calendar.action_calendar_event').id
            return {
                'type': 'ir.actions.act_url',
                'url': '/web#action=%s&model=calendar.event&view_type=list&cids=&menu_id=%s' % (form_view_id, list_view_id),
                'target': 'self',

            }

    def date_time_conversion_time_zone(self, date, event_tz):

        """
        it will take the paramters of converted datetime and current meeting timezon and return
        the current meeting time to zoom user time.
        """
        # print('funtion')

        if event_tz and self.env.user.zoom_user_timezone:
            tz1 = pytz.timezone(event_tz)
            tz2 = pytz.timezone(self.env.user.zoom_user_timezone)

            if tz1 != tz2:
                date = datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")
                date = tz1.localize(date)
                date = date.astimezone(tz2)
                date = date.strftime("%Y-%m-%dT%H:%M:%SZ")
            else:
                date=datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")
                date = date.strftime("%Y-%m-%dT%H:%M:%SZ")
            return date
        else:
            if not self.event_tz:
                UserError("Please set meeting timezone")
            if not self.env.user.zoom_user_timezone:
                UserError("Please set zoom user timezone")

    def action_sendmail(self):
        # print('funtion')

        current_user = self.env.user
        email = self.env.user.email
        if email:
            for meeting in self:
                to_notify = meeting.attendee_ids.filtered(lambda a: a.email != current_user.email)
                to_notify.email_notification_to_participents_attendi(meeting,'calendar.calendar_template_meeting_invitation')
        if self.external_participants:
            for meeting in self:
                meeting.external_participants.email_for_outer_zoom_people(meeting,'de_zoom_connector.calendar_template_external_user_meeting_invitation')
        return True

    def create_attendees(self):
        # print('funtion')

        current_user = self.env.user
        result = {}
        for meeting in self:
            alreay_meeting_partners = meeting.attendee_ids.mapped('partner_id')
            meeting_attendees = self.env['calendar.attendee']
            meeting_partners = self.env['res.partner']
            for partner in meeting.partner_ids.filtered(lambda partner: partner not in alreay_meeting_partners):
                values = {
                    'partner_id': partner.id,
                    'email': partner.email,
                    'event_id': meeting.id,
                }

                # current user don't have to accept his own meeting
                if partner == self.env.user.partner_id:
                    values['state'] = 'accepted'

                attendee = self.env['calendar.attendee'].create(values)

                meeting_attendees |= attendee
                meeting_partners |= partner
            if self.env.user.company_id.meeting_event_mail_notification == True and self._context.get('zoom_meeting_create') != True and self._context.get('no_invite_mail')!=True:
                    if meeting_attendees and not self._context.get('detaching'):
                        to_notify = meeting_attendees.filtered(lambda a: a.email != current_user.email)
                        to_notify.email_notification_to_participents_attendi(meeting,'calendar.calendar_template_meeting_invitation')
                    if meeting.external_participants and not self._context.get('detaching'):
                        for participant_id in meeting.external_participants:
                            if participant_id.mail_sent != True:
                                participant_id.email_for_outer_zoom_people(meeting,
                                                                                   'de_zoom_connector.calendar_template_external_user_meeting_invitation')
                                participant_id.mail_sent = True
            if meeting_attendees:
                meeting.write({'attendee_ids': [(4, meeting_attendee.id) for meeting_attendee in meeting_attendees]})

            if meeting_partners:
                meeting.message_subscribe(partner_ids=meeting_partners.ids)

            # We remove old attendees who are not in partner_ids now.
            all_partners = meeting.partner_ids
            all_partner_attendees = meeting.attendee_ids.mapped('partner_id')
            old_attendees = meeting.attendee_ids
            partners_to_remove = all_partner_attendees + meeting_partners - all_partners

            attendees_to_remove = self.env["calendar.attendee"]
            if partners_to_remove:
                attendees_to_remove = self.env["calendar.attendee"].search(
                    [('partner_id', 'in', partners_to_remove.ids), ('event_id', '=', meeting.id)])
                attendees_to_remove.unlink()

            result[meeting.id] = {
                'new_attendees': meeting_attendees,
                'old_attendees': old_attendees,
                'removed_attendees': attendees_to_remove,
                'removed_partners': partners_to_remove
            }
        return result

    # Remove zoom meeting
    def delete_remove_zoom_meeting_fun(self):
        # print('funtion')

        for meeting in self:
            if self.env.user.id != meeting.create_uid.id and self.env.user.id != self.env.user.company_id.zoom_admin_user_id.id:
                raise UserError("You didn't have permission to remove zoom meeting.")
            try:

                client = self.api_connection_fun()
                response = client.meeting.get(id=meeting.meeting_id,show_previous_occurrences=True)
                if response.status_code == 200:
                    client.meeting.delete(id=meeting.meeting_id)

            except Exception as e:
                raise UserError(_('Zoom API Exception! \n %s') % e)
            meeting.with_context(zoom_write=True).write({'meeting_id': '', 'join_url': '',
                                                      'start_url': '', 'zoom_occurrence_list': '',
                                                      'host_id': '',
                                                      'meeting_pswd': '', 'is_zoom_meeting': False})
            if meeting.attendee_ids:
                meeting.attendee_ids.email_notification_to_participents_attendi(meeting,
                                                                   'calendar.calendar_template_meeting_changedate')
            if meeting.external_participants:
                meeting.external_participants.email_for_outer_zoom_people(meeting,
                                                                                  'de_zoom_connector.calendar_template_zoom_external_user_meeting_changedate')

    def join_link_zoom_meeting_fun(self):
        """
        :return: Link current meeting to zoom
        """
        # print('funtion')

        for meeting in self:
            if meeting.allday != True:
               if meeting.rrule_type != 'yearly':
                    if meeting.start and meeting.stop:
                        meeting.start_date = meeting.start
                        meeting.stop_date = meeting.stop
                        meeting.zoommetingchange()
                        meeting._compute_display_time()
                    meeting.is_zoom_meeting = True
               else:
                   raise UserError(_("Zoom doesn't support recurrence option Years"))
            else:
                raise UserError(_('You cannot link this event to zoom'))

    def get_display_time_tz(self, tz=False):

        """ get the display_time of the meeting, forcing the timezone.
            This method is called from email template, to not use sudo().

          """
        # print('funtion')

        self.ensure_one()
        if tz:
            self = self.with_context(tz=tz)
        return self._get_display_time(self.start, self.stop, self.duration, self.allday)

    def detach_recurring_event(self, values=None):
        """
            it will detach the events of virtual recurring by making the copy of orignal and then change
            the values to it.
        """
        # print('funtion')

        if not values:
            values = {}
        real_id = convert_cal_id_to_actual_id(self.id)
        meeting_origin = self.browse(real_id)
        data = self.read(['allday', 'start','stop','rrule', 'duration'])[0]
        if meeting_origin.is_zoom_meeting != True or self._context.get('zoom_meet_unlink')==True:
            if data.get('rrule'):
                data.update(
                    values,
                    recurrent_id=real_id,
                    recurrent_id_date=data.get('start'),
                    rrule_type=False,
                    rrule='',
                    recurrency=False,
                    final_date=False,
                    end_type=False,
                    update_single_instance=True

                )
                # do not copy the id
                if data.get('id'):
                    del data['id']
                return meeting_origin.with_context(detaching=True,zoom_create=True,zoom_write=True).copy(default=data)
        else:
            if self.env.user.id != meeting_origin.create_uid.id and self.env.user.id != self.env.user.company_id.zoom_admin_user_id.id:
                raise UserError("You didn't have permission to remove zoom meeting.")
            meeting_dict = meeting_origin.copy_data()[0]
            participant_list = []
            for participant_id in meeting_origin.external_participants:
                participant_dict={
                    'name' : participant_id.name,
                    'email': participant_id.email
                }
                participant_list.append((0,0,participant_dict))

            meeting_dict.update({
                'recurrent_id': real_id,
                'recurrent_id_date': data.get('start'),
                'start':data.get('start'),
                'stop':data.get('stop'),
                'rrule_type': False,
                'rrule': '',
                'recurrency': False,
                'final_date': False,
                'end_type': False,
                'zoom_occurrence_list':'',
                'meeting_id':'',
                'start_url':'',
                'join_url':'',
                'update_single_instance' : True,
                'external_participants' : participant_list


            })
            data = self.read(['start'])[0]

            meeting=meeting_origin.with_context(detaching=True,zoom_write=True,no_invite_mail=True).copy(default=meeting_dict)
            client = self.api_connection_fun()

            # Updating zoom occurrence in current record.
            if meeting_origin.zoom_occurrence_list:
                zoom_occurrence_list=literal_eval(meeting_origin.zoom_occurrence_list)
                for occurrence in range(len(zoom_occurrence_list) - 1, -1, -1):
                    if zoom_occurrence_list[occurrence]['id'] == data['id']:
                        occurrence_id=zoom_occurrence_list[occurrence]['occurrence_id']
                        zoom_occurrence_list.pop(occurrence)
                        try:
                            response = client.meeting.get(id=meeting_origin.meeting_id,occurrence_id=occurrence_id)
                            if response.status_code == 200:
                                client.meeting.delete(id=meeting_origin.meeting_id,occurrence_id=occurrence_id)

                        except Exception as e:
                            raise UserError(_('Zoom API Exception! \n %s') % e)
                meeting_origin.with_context(zoom_write=True).write({'zoom_occurrence_list':zoom_occurrence_list})
            if data.get('id'):
                del data['id']

            return meeting

    def get_date(self, date, interval, tz=None):
        """
            it will format the dates , local dates which are used in email templates

            it will accept the paramters of intervel indicating the desired format.
            return the formateed date
        """
        # print('funtion')

        self.ensure_one()
        date = fields.Datetime.from_string(date)
        result = False
        if tz:
            timezone = pytz.timezone(tz or 'UTC')
            if date:
                date = date.replace(tzinfo=pytz.timezone('UTC')).astimezone(timezone)

        if interval == 'day':
            # Day number (1-31)
            if date:
                result = str(date.day)

        elif interval == 'month':
            # Localized month name and year
            if date:
                result = babel.dates.format_date(date=date, format='MMMM y', locale=get_lang(self.env).code)

        elif interval == 'dayname':
            # Localized day name
            if date:
                result = babel.dates.format_date(date=date, format='EEEE', locale=get_lang(self.env).code)

        elif interval == 'time':
            # Localized time
            # FIXME: formats are specifically encoded to bytes, maybe use babel?
            dummy, format_time = self._get_date_formats()
            if date:
                result = tools.ustr(date.strftime(format_time + " %Z"))

        return result


class OuterUserForEmail(models.Model):
    _name = 'zoom_meeting.external_user'
    _description = 'Zoom Meeting External Participant'
    _order = 'name'

    name = fields.Char('Name', required=True)
    email = fields.Char('Email', required=True)
    event_id = fields.Many2one('calendar.event', 'Meeting linked', ondelete='cascade')
    partner_id = fields.Many2one(related='event_id.create_uid.partner_id')
    send_mail = fields.Boolean('Send Invitation', default=True)
    mail_sent = fields.Boolean('Invitation Sent', readonly=True, default=False)

    def email_for_outer_zoom_people(self, meeting, template_xmlid, force_send=True):

        """
        It will sent the mail to Participents to join the meeting

        paramenters template_Xmlid used for email template to sent the mail.
        and force_Send used to send the mail instantly.
        """

        # print('function')

        res = False

        if self.env['ir.config_parameter'].sudo().get_param('calendar.block_mail') or self._context.get(
                "no_mail_to_attendees"):
            return res

        calendar_view = self.env.ref('calendar.view_calendar_event_calendar')
        invitation_template = self.env.ref(template_xmlid)

        # get ics file for all meetings
        ics_files = self.mapped('event_id')._get_ics_file()

        # prepare rendering context for mail template
        colors = {
            'needsAction': 'grey',
            'accepted': 'green',
            'tentative': '#FFFF00',
            'declined': 'red'
        }
        rendering_context = dict(self._context)
        rendering_context.update({
            'color': colors,
            'action_id': self.env['ir.actions.act_window'].search([('view_id', '=', calendar_view.id)], limit=1).id,
            'dbname': self._cr.dbname,
            'base_url': self.env['ir.config_parameter'].sudo().get_param('web.base.url',
                                                                         default='http://localhost:8069')
        })
        invitation_template = invitation_template.with_context(rendering_context)

        # send email with attachments
        mail_ids = []
        for participant in self:
            if participant.name or participant.email:
                ics_file = ics_files.get(participant.event_id.id)

                email_values = {
                    'model': None,  # We don't want to have the mail in the tchatter while in queue!
                    'res_id': None,
                }
                if ics_file:
                    email_values['attachment_ids'] = [
                        (0, 0, {'name': 'invitation.ics',
                                'mimetype': 'text/calendar',
                                'datas': base64.b64encode(ics_file)})
                    ]
                mail_ids.append(invitation_template.with_context(
                    date=meeting.start_datetime or meeting.start_date).send_mail(participant.id,
                    email_values=email_values, notif_layout='mail.mail_notification_light'))

        if force_send and mail_ids:
            res = self.env['mail.mail'].browse(mail_ids).send()

        return res


class AlarmManager(models.AbstractModel):
    _inherit = 'calendar.alarm_manager'

    def do_mail_reminder(self, alert_check):
        # print('funtion')

        meeting = self.env['calendar.event'].browse(alert_check['event_id'])

        alarm = self.env['calendar.alarm'].browse(alert_check['alarm_id'])

        result = False

        if meeting.create_uid.company_id.meeting_event_mail_notification == True:

            if alarm.alarm_type == 'email':
                    result_1 = meeting.attendee_ids.filtered(lambda r: r.state != 'declined').email_notification_to_participents_attendi(meeting,
                        'calendar.calendar_template_meeting_reminder', force_send=True)
                    result_2 = meeting.external_participants.email_for_outer_zoom_people(meeting,
                        'de_zoom_connector.calendar_template_zoom_external_user_meeting_reminder', force_send=True)

                    if result_1 and result_2 == True:
                        result = True

        return result


class Attendee(models.Model):

    _inherit = 'calendar.attendee'
    
    def email_notification_to_participents_attendi(self, meeting, template_xmlid, force_send=True):

        """
        It will send the email to contacts that are the part of email attendi.
        xml_id use for email templete.
        force_send used for to send the email instantly.
        """

        # print('funtion')

        res = False

        if self.env['ir.config_parameter'].sudo().get_param('calendar.block_mail') or self._context.get(
                "no_mail_to_attendees"):
            return res

        calendar_view = self.env.ref('calendar.view_calendar_event_calendar')
        invitation_template = self.env.ref(template_xmlid)

        # get ics file for all meetings
        ics_files = self.mapped('event_id')._get_ics_file()

        # prepare rendering context for mail template
        colors = {
            'needsAction': 'grey',
            'accepted': 'green',
            'tentative': '#FFFF00',
            'declined': 'red'
        }
        rendering_context = dict(self._context)
        rendering_context.update({
            'color': colors,
            'action_id': self.env['ir.actions.act_window'].search([('view_id', '=', calendar_view.id)], limit=1).id,
            'dbname': self._cr.dbname,
            'base_url': self.env['ir.config_parameter'].sudo().get_param('web.base.url', default='http://localhost:8069')
        })
        invitation_template = invitation_template.with_context(rendering_context)

        # send email with attachments
        mail_ids = []
        for attendee in self:
            if attendee.email or attendee.partner_id.email:
                # FIXME: is ics_file text or bytes?
                ics_file = ics_files.get(attendee.event_id.id)

                email_values = {
                    'model': None,  # We don't want to have the mail in the tchatter while in queue!
                    'res_id': None,
                }
                if ics_file:
                    email_values['attachment_ids'] = [
                        (0, 0, {'name': 'invitation.ics',
                                'mimetype': 'text/calendar',
                                'datas': base64.b64encode(ics_file)})
                    ]
                mail_ids.append(invitation_template.with_context(date=meeting.start_datetime or meeting.start_date).send_mail(attendee.id, email_values=email_values,
                                                              notif_layout='mail.mail_notification_light'))

        if force_send and mail_ids:
            res = self.env['mail.mail'].browse(mail_ids).send()

        return res
