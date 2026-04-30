# coding: utf-8

from odoo import models, api, fields
from datetime import date, datetime, timedelta


class AcsRescheduleAppointments(models.TransientModel):
    _name = 'tgr.reschedule.appointments'
    _description = "Reschedule Appointments"

    tgr_reschedule_time = fields.Float(string="Reschedule Selected Appointments by (Hours)", required=True)

    def tgr_reschedule_appointments(self):
        appointments = self.env['hms.appointment'].search([('id','in',self.env.context.get('active_ids'))])
        #TGR: do it in method only to use that method for notifications.
        appointments.tgr_reschedule_appointments(self.tgr_reschedule_time)
