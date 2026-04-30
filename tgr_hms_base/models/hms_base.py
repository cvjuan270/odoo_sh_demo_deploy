# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from random import randint


class TGRPatientTag(models.Model):
    _name = "hms.patient.tag"
    _description = "Tgr Patient Tag"

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char(string="Name")
    color = fields.Integer('Color', default=_get_default_color)


class TGRTherapeuticEffect(models.Model):
    _name = "hms.therapeutic.effect"
    _description = "Tgr Therapeutic Effect"


    code = fields.Char(string="Code")
    name = fields.Char(string="Name", required=True)


class TGRReligion(models.Model):
    _name = 'tgr.religion'
    _description = "TGR Religion"

    name = fields.Char(string="Name", required=True,translate=True)
    code = fields.Char(string='code')
    notes = fields.Char(string='Notes')

    _sql_constraints = [('name_uniq', 'UNIQUE(name)', 'Name must be unique!')]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: