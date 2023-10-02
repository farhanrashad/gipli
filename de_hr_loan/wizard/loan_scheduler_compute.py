# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

#
# Order Point Method:
#    - Order if the virtual stock of today is below the min of the defined order point
#

from odoo import models, tools

import logging
import threading

_logger = logging.getLogger(__name__)


class LoanSchedulerCompute(models.TransientModel):
    _name = 'hr.loan.scheduler.compute'
    _description = 'Run Loan Scheduler Manually'

    def _loan_reconcile_payment(self):
        # As this function is in a new thread, I need to open a new cursor, because the old one may be closed
        with self.pool.cursor() as new_cr:
            self = self.with_env(self.env(cr=new_cr))
            scheduler_cron = self.sudo().env.ref('de_hr_loan.ir_cron_loan_scheduler_action')
            # Avoid to run the scheduler multiple times in the same time
            try:
                with tools.mute_logger('odoo.sql_db'):
                    self._cr.execute("SELECT id FROM ir_cron WHERE id = %s FOR UPDATE NOWAIT", (scheduler_cron.id,))
            except Exception:
                _logger.info('Attempt to run procurement scheduler aborted, as already running')
                self._cr.rollback()
                return {}

            for company in self.env.user.company_ids:
                cids = (self.env.user.company_id | self.env.user.company_ids).ids
                self.env['hr.loan'].with_context(allowed_company_ids=cids).run_scheduler(
                    use_new_cursor=self._cr.dbname,
                    company_id=company.id)
            self._cr.rollback()
        return {}

    def reconcile_loans(self):
        threaded_calculation = threading.Thread(target=self._loan_reconcile_payment, args=())
        threaded_calculation.start()
        return {'type': 'ir.actions.client', 'tag': 'reload'}
