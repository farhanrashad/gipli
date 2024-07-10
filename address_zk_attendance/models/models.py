# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
import json
from datetime import datetime
import datetime as delta
import datetime as time
import pytz
import requests
import logging
import dateutil
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)
import sys


class ResCompany(models.Model):
    _inherit ='res.company'

    seq_prefix = fields.Char('Prefix')



class HrEmployee(models.Model):
    _inherit = "hr.employee"


    zk_emp_id = fields.Char(string="Employee Attendance ID", )
    company_changed = fields.Boolean('Company Changed')

    # @api.onchange('company_id')
    def get_zk_emp_id(self):
        for rec in self:
            if rec.company_id and rec.company_id.id == 1:
                print("1111111111")
                rec.zk_emp_id = self.env['ir.sequence'].next_by_code('the.address.investments')

            if rec.company_id and rec.company_id.id == 2:
                print("2222222222222")
                rec.zk_emp_id = self.env['ir.sequence'].next_by_code('the.address.developments')

            if rec.company_id and rec.company_id.id == 3:
                rec.zk_emp_id = self.env['ir.sequence'].next_by_code('the.address.holding')
                print("3333333333333")

            if rec.company_id and rec.company_id.id == 4:
                print("44444444444444")
                rec.zk_emp_id = self.env['ir.sequence'].next_by_code('THE.MARQ.PROJECTS.MANAGEMENT.sequence')
            if rec.company_id and rec.company_id.id == 9:
                print("99999999999999999999")
                rec.zk_emp_id = self.env['ir.sequence'].next_by_code('MARQ2.sequence')

    # _sql_constraints = [('unique_zk_emp_id', 'unique(zk_emp_id)',
    #                      'Duplicate Attendance ID')]

    def update_seq(self):
        for rec in self:
            print("rec",rec)

            if rec.zk_emp_id and '-' in rec.zk_emp_id:
                x = rec.zk_emp_id.split('-', 1)[1]
                print("Xxxxxxxx",x)
                prefix = rec.company_id.seq_prefix
                print("prefix",prefix)
                rec.zk_emp_id = prefix + '-'+ x
            else:
                prefix = rec.company_id.seq_prefix
                print("prefix", prefix)
                old = rec.zk_emp_id 
                rec.zk_emp_id = prefix + '-' + str(old)


    def write(self, values):
        res = super(HrEmployee, self).write(values)
        if 'company_id' in values:
            values['company_changed'] = True
            print("55555",values)
            self.update_seq()



        return res

    @api.model
    def create(self, vals):
        # set attendance id as after the maximum one set for employees
        ##
        if vals.get('company_id', False):
            employees = self.env['hr.employee'].search(
                [('zk_emp_id', '!=', False), ('company_id', '=', vals.get('company_id')),
                 ('company_changed', '!=', True), '|', ('active', '=', True), ('active', '=', False)])
        else:
            raise ValidationError(_('Company is not set'))

        if vals['company_id'] and vals['identification_id']:
            prefix = self.env['res.company'].browse(vals['company_id']).seq_prefix

            vals['zk_emp_id'] = prefix + '-' + self.env['ir.sequence'].next_by_code('multi.company.employee.sequene')

        # if vals['company_id'] and vals['company_id'] == 1:
        #
        #     vals['zk_emp_id'] = self.env['ir.sequence'].next_by_code('the.address.investments')
        #     print("1111111111", self.env['ir.sequence'].next_by_code('the.address.investments'))
        #
        # if vals['company_id'] and vals['company_id'] == 2:
        #     print("2222222222222",self.env['ir.sequence'].next_by_code('the.address.developments'))
        #     vals['zk_emp_id'] = self.env['ir.sequence'].next_by_code('the.address.developments')
        #
        # if vals['company_id'] and vals['company_id'] == 3:
        #     vals['zk_emp_id'] = self.env['ir.sequence'].next_by_code('the.address.holding')
        #     print("3333333333333")
        #
        # if vals['company_id'] and vals['company_id'] == 4:
        #     print("44444444444444")
        #     vals['zk_emp_id'] = self.env['ir.sequence'].next_by_code('THE.MARQ.PROJECTS.MANAGEMENT.sequence')
        # if vals['company_id'] and vals['company_id'] == 9:
        #     print("99999999999999999999")
        #     vals['zk_emp_id'] = self.env['ir.sequence'].next_by_code('MARQ2.sequence')

        # attendance_ids = employees.mapped('zk_emp_id')
        # attendance_ids = list(map(int, attendance_ids))
        # new_attendace_id = max(attendance_ids) + 1 if attendance_ids else 1
        # set for new employee
        # vals['zk_emp_id'] = str(new_attendace_id)
        res = super(HrEmployee, self).create(vals)
        return res

    def increment_zk_emp_id(self,zk_emp_id):
        zk_emp_id = str(int(zk_emp_id) + 1)
        employees = self.env['hr.employee'].sudo().search(
            [('zk_emp_id', '=', zk_emp_id), ('id', '!=', self.id), '|', ('active', '=', True),
             ('active', '=', False)])
        if employees:
            self.increment_zk_emp_id(zk_emp_id)
        else:
            print('zk_emp_id',zk_emp_id)
            self.zk_emp_id = zk_emp_id

    @api.constrains('zk_emp_id')
    def check_zk_emp_id(self):
        for rec in self:
            if rec.zk_emp_id:
                employees = self.env['hr.employee'].sudo().search(
                    [('zk_emp_id', '=', rec.zk_emp_id), ('id', '!=', rec.id), '|', ('active', '=', True), ('active', '=', False)])
                if employees:
                    rec.increment_zk_emp_id(rec.zk_emp_id)
                    # raise ValidationError(_("The Attendance Id is already existed"))

    @api.constrains('identification_id')
    def check_identification_id(self):
        for rec in self:
            employees = self.env['hr.employee'].search(
                [('identification_id', '=', rec.identification_id), ('id', '!=', rec.id)])
            print(">>>>>>>>>>>", employees)
            termination_employee = self.env['hr.termination'].search(
                [('employee_id.identification_id', '=', rec.identification_id), ('employee_id', '!=', rec.id)])
            if employees or termination_employee:
                raise ValidationError(_("The Identification Id is already existed"))

    @api.constrains('private_email')
    def check_private_email(self):
        for rec in self:
            employees = self.env['hr.employee'].search(
                [('private_email', '=', rec.private_email), ('id', '!=', rec.id)])
            print(">>>>>>>>>>>", employees)
            termination_employee = self.env['hr.termination'].search(
                [('employee_id.private_email', '=', rec.private_email), ('employee_id', '!=', rec.id)])
            if employees or termination_employee:
                raise ValidationError(_("Private Email is already existed"))

    # @api.constrains('phone_num')
    # def check_phone_num(self):
    #     for rec in self:
    #         if rec.phone_num:
    #             employees = self.env['hr.employee'].sudo().search(
    #                 [('phone_num', '=', rec.phone_num), ('id', '!=', rec.id)])
    #             print(">>>>>>>>>>>", employees)
    #             if employees:
    #                 raise ValidationError(_("The Phone Number is already existed"))

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):

        args = args or []
        recs = self.browse()
        if not recs:
            recs = self.search([('zk_emp_id', operator, name)] + args, limit=limit)
        if not recs:
            recs = self.search([('name', operator, name)] + args, limit=limit)

        return recs.name_get()


class zk_attendance_tmp(models.Model):
    _name = 'hr.attendance.zk.temp'

    machine_id = fields.Many2one(comodel_name="hr.attendance.zk.machine", string="Attendance Machine", required=True)
    user_number = fields.Char(string="Machine User Id", index=True)
    user = fields.Many2one(comodel_name="hr.employee", compute="_compute_user", store=True)
    date = fields.Datetime(string="Date", index=True)
    local_date = fields.Datetime(string='Date', compute="_compute_local_date", store=True,
                                 help='for display only as the datetime of the system is showing as 2 hours after')
    date_temp = fields.Date(string="Date Temp", index=True, compute="_compute_date", store=True)
    inoutmode = fields.Char(string="In/Out Mode")
    logged = fields.Boolean(string="Logged", default=False)
    reversed = fields.Boolean(string='Reversed', defult=True)
    zk_emp_id = fields.Char(related='user.zk_emp_id', string="Employee Attendance ID")

    @api.depends('user_number')
    def _compute_user(self):
        if self.user_number:
            user = self.env['hr.employee'].search([('zk_emp_id', '=', self.user_number)])
            if user.id:
                self.user = user

    @api.depends('date')
    def _compute_date(self):
        for rec in self:
            if rec.date:
                egypt_timezone = datetime.strptime(str(rec.date), "%Y-%m-%d %H:%M:%S")  # + time.timedelta(hours=2)
                rec.date_temp = egypt_timezone.date()

    @api.depends('date')
    def _compute_local_date(self):
        for record in self:
            if record.date:
                record.local_date = datetime.strptime(str(record.date), "%Y-%m-%d %H:%M:%S") - time.timedelta(hours=2)

    def timezone_correction(self):
        for rec in self.search([]):
            date_Temp = datetime.strptime(rec.date, "%Y-%m-%d %H:%M:%S")
            print("First: ", date_Temp.strftime("%Y/%m/%d %H:%M:%S"))
            local = pytz.timezone("Africa/Cairo")
            local_dt = pytz.utc.localize(date_Temp, is_dst=None)
            date_Temp = local_dt.astimezone(local)
            print("Second: ", date_Temp.strftime("%Y/%m/%d %H:%M:%S"))
            # local_iraq = pytz.timezone("Asia/Baghdad")
            # local_dt = date_Temp.replace(tzinfo=local_iraq)
            # date_Temp = local_dt.astimezone(pytz.utc)
            print("Final: ", date_Temp.strftime("%Y/%m/%d %H:%M:%S"))
            rec.date = date_Temp

    @api.model
    def process_data(self):
        # Process_data
        # responsible for processing attendance data by
        # getting all the data for each employee for each day
        # checking the earliest check in and latest checkout
        # and producing an hr.attendance record with it if
        # the data is complete in case of a missing checkout
        # the record is handled based on the default time option
        # in config if set to default time we use the tie value set in config
        # or if the selected option is shift we use the checkout time set for the day in his shift
        # with open("/home/ali/ERP/cention11/sv/custom/zkLogs.txt", 'a') as out:
        conf = self.env['zk.attendance.setting'].get_values()
        records = self.search([('logged', '=', False)])
        date_in = None
        date_out = None
        employees = list(set(self.search([('logged', '=', False), ('user', "!=", False)]).mapped('user_number')))
        for emp in employees:
            emp_obj = self.env['hr.employee'].search([('zk_emp_id', '=', emp)])
            datetime_list = records.filtered(lambda x: x.user_number == emp).mapped('date')
            dates = [x.date().strftime("%Y-%m-%d") for x in datetime_list]
            dates_unique = list(set(dates))
            for date in dates_unique:
                attendance_per_emp = records.filtered(
                    lambda x: x.user_number == emp and str(x.date_temp) == date).sorted()

                date_ins = attendance_per_emp

                if len(attendance_per_emp) <= 1:
                    pass

                elif date_ins:
                    date_out = max(date_ins.mapped('date'))
                    date_in = min(date_ins.mapped('date'))
                    if date_in < date_out:
                        local_check_in = date_in - time.timedelta(hours=2)
                        local_check_out = date_out - time.timedelta(hours=2)
                        self.env['hr.attendance'].create(
                            {'employee_id': emp_obj.id, 'check_in': local_check_in,
                             'local_check_in': date_in,
                             'local_check_out': date_out,
                             'check_out': local_check_out})
                        attendance_per_emp.write({'logged': True})


class zk_attendance_machine(models.Model):
    _name = "hr.attendance.zk.machine"

    machine_number = fields.Integer(string="Machine Number", default=0, readonly=True)
    name = fields.Char(string="Name")
    ip = fields.Char(string="IP", required=True)
    port = fields.Integer(string="port", default=4370)
    sync = fields.Boolean(string="Synced", default=False)
    model = fields.Char(string="Model")
    date_sync = fields.Datetime(string="Sync Date")
    date_sync_success = fields.Datetime(string="Successful Sync Date")
    manual_upload_sync_date = fields.Datetime(string="Last Manual Upload Date")
    sync_error = fields.Text(string="Sync Error")

    @api.model
    def create(self, values):
        res = super(zk_attendance_machine, self).create(values)
        res['machine_number'] = res.id
        return res

    @api.model
    def pull_machines(self):
        machines = self.search([])
        for machine in machines:
            machine.pull_attendance()

    def pull_attendance(self):
        # Pull attendance
        # function sends a request to the attendance api according to the ip and port set in the config
        # receives the data from the api and sets them in the attendance temp model with duplicate detection
        # with open("/home/mohamed/Desktop/zkAttendanceIntegration/AttendanceLogs.json", encoding="utf-8-sig") as f:
        #     # raise Warning(f)
        #     file = f.read()
        #     data = json.loads(file)
        #     raise Warning(data)

        ############################################
        conf = self.env['zk.attendance.setting'].get_values()
        if conf['api_ip'] == None:
            raise exceptions.ValidationError("Please configure API IP and port before pulling from the machines")
        if conf['api_port'] == None or conf['api_port'] == False:
            url = "http://%s/api/AttendanceMachines/%s/%s" % (str(conf['api_ip']), str(self.ip), str(self.port))
        else:
            url = "http://%s:%s/api/AttendanceMachines/%s/%s" % (
                str(conf['api_ip']), str(conf['api_port']), str(self.ip), str(self.port))

        res = requests.get(url)
        res = res.json()

        if len(res) > 0:
            for record in res:
                date_Temp = datetime.strptime(record["DateTimeRecord"], "%Y/%m/%d %H:%M:%S")
                local = pytz.timezone("Africa/Cairo")
                local_dt = local.localize(date_Temp, is_dst=None)
                date_Temp = local_dt.astimezone(pytz.utc)
                vals = {"machine_id": self.machine_number, "user_number": record["IndRegID"], "date": date_Temp,
                        "inoutmode": record["InOutMode"]}
                duplicate = self.env['hr.attendance.zk.temp'].search(
                    [("machine_id", '=', self.machine_number), ("user_number", '=', record["IndRegID"]),
                     ("date", '=', date_Temp.strftime("%Y-%m-%d %H:%M:%S")),
                     ("inoutmode", '=', record["InOutMode"])]) or False
                if not duplicate:
                    new_vals, vals = self.check_overlapping_shift(vals)

                    if new_vals:
                        self.env['hr.attendance.zk.temp'].create(vals)
                        self.env['hr.attendance.zk.temp'].create(new_vals)
                    else:
                        self.env['hr.attendance.zk.temp'].create(vals)

            self.sync = True
            self.sync_error = ""
            self.date_sync = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.date_sync_success = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def check_overlapping_shift(self, vals):
        employee = self.env['hr.employee'].search([('zk_emp_id', '=', vals['user_number'])])
        if employee:
            shift = employee.resource_calendar_id.attendance_rel_ids
            shift_from = sum(shift.mapped('hour_from'))
            shift_to = sum(shift.mapped('hour_to'))
            datetime_obj = vals['date']
            new_vals = vals.copy()

            # 2nd Shift
            if shift_to == 0.0:
                if datetime_obj.hour <= 2:
                    privious_date = datetime_obj - delta.timedelta(1)
                    new_date = privious_date.replace(hour=21, minute=59, second=59)
                    new_vals['date'] = new_date
                    vals['logged'] = True
            # 3rd Shift
            elif shift_from == 0.0:
                if datetime_obj.hour == 21:
                    new_date = datetime_obj.replace(hour=22, minute=1, second=59)
                    new_vals['date'] = new_date
                    vals['logged'] = True
            # 12 hours
            elif shift[0].hour_from == 20.0:
                if datetime_obj.hour in [5, 6]:
                    new_date = datetime_obj - delta.timedelta(1)
                    new_vals['date'] = new_date
                    vals['logged'] = True
                    # vals['reversed'] = True
                    # new_vals['reversed'] = True

            else:
                new_vals = False
        else:
            new_vals = False

        return new_vals, vals

    def process(self):
        # responsile to call process_data function from schedualed action
        self.env['hr.attendance.zk.temp'].process_data()


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    no_checkout = fields.Boolean(string="Missing Check-out", default=False)

    no_check_in = fields.Boolean(string="Missing Check-in", default=False)

    local_check_in = fields.Datetime(string="Local Check In")
    local_check_out = fields.Datetime(string="Local Check Out")

    zk_emp_id = fields.Char(related='employee_id.zk_emp_id', string="Employee Attendance ID")
