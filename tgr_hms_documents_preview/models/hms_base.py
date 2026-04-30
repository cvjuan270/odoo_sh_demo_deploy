# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class TgrHmsPatient(models.Model):
    _name = "hms.patient"
    _inherit = ["hms.patient", "tgr.document.view.mixin"]


class TgrHmsTreatment(models.Model):
    _name = "hms.treatment"
    _inherit = ["hms.treatment", "tgr.document.view.mixin"]


class TgrPatientProcedure(models.Model):
    _name = "tgr.patient.procedure"
    _inherit = ["tgr.patient.procedure", "tgr.document.view.mixin"]


class TgrHmsAppointment(models.Model):
    _name = "hms.appointment"
    _inherit = ["hms.appointment", "tgr.document.view.mixin"]


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

