from odoo import api, fields, models, tools

class ReportStudentAttendance(models.Model):
    _name = "report.student.attendance"
    _description = "Student Attendance Analysis"
    _auto = False
    _rec_name = 'date'
    _order = 'date desc'

    date = fields.Date('Attendance Date', readonly=True)
    student_id = fields.Many2one('res.partner', 'Student', readonly=True)
    status = fields.Selection([
        ('Present', 'Present'),
        ('Absent', 'Absent'),
    ], string='Attendance Status', readonly=True)

    @property
    def _table_query(self):
        return '%s %s %s %s' % (self._select(), self._from(), self._where(), self._group_by())

    def _select(self):
        select_str = """
            SELECT
                d.attendance_date as date,
                s.id as student_id,
                CASE WHEN d.status = 'Present' THEN 'Present' ELSE 'Absent' END AS status
        """
        return select_str

    def _from(self):
        from_str = """
            FROM (
                WITH date_range AS (
                    SELECT 
                        to_char(date_trunc('month', current_date), 'YYYY-MM-DD')::date AS month_start,
                        to_char(date_trunc('month', current_date) + INTERVAL '1 month - 1 day', 'YYYY-MM-DD')::date AS month_end
                    )
                SELECT 
                    d.month_start + i AS attendance_date
                FROM (
                    SELECT generate_series(0, EXTRACT(day FROM (month_end - month_start))) AS i
                    FROM date_range
                ) AS days
                CROSS JOIN date_range
            ) AS dates
            LEFT JOIN oe_student_attendance d ON dates.attendance_date = d.date_attendance
            JOIN res_partner s ON TRUE
        """
        return from_str

    def _where(self):
        return """
            WHERE
                s.is_student = TRUE
        """

    def _group_by(self):
        group_by_str = """
            GROUP BY
                d.attendance_date, s.id, d.status
        """
        return group_by_str
