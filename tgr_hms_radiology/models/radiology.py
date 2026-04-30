# -*- coding: utf-8 -*-

from odoo import _, fields, models


class TgrRadiologyRequest(models.Model):
    _inherit = 'tgr.radiology.request'

    appointment_id = fields.Many2one('hms.appointment', string='Cita', ondelete='restrict')
    treatment_id = fields.Many2one('hms.treatment', string='Tratamiento', ondelete='restrict')

    def prepare_test_result_data(self, line, patient):
        res = super(TgrRadiologyRequest, self).prepare_test_result_data(line, patient)
        res['appointment_id'] = self.appointment_id and self.appointment_id.id or False
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
