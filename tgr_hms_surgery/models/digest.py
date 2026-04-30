# -*- coding: utf-8 -*-

from odoo import fields, models, _
from odoo.exceptions import AccessError


class Digest(models.Model):
    _inherit = "digest.digest"

    kpi_tgr_surgery_total = fields.Boolean("Nuevas Cirugías")
    kpi_tgr_surgery_total_value = fields.Integer(compute="_compute_kpi_tgr_surgery_total_value")

    def _compute_kpi_tgr_surgery_total_value(self):
        if not self.env.user.has_group("tgr_hms_base.group_hms_user"):
            raise AccessError(_("No tiene acceso, omita estos datos para el correo electrónico del resumen del usuario"))
        for record in self:
            start, end, company = record._get_kpi_compute_parameters()
            surgery = self.env["hms.surgery"].search_count(
                [
                    ("company_id", "=", company.id),
                    ("start_date", ">=", start),
                    ("start_date", "<", end),
                    ("state", "not in", ["cancel"]),
                ]
            )
            record.kpi_tgr_surgery_total_value = surgery

    def _compute_kpis_actions(self, company, user):
        res = super(Digest, self)._compute_kpis_actions(company, user)
        res["kpi_tgr_surgery_total"] = (
            "tgr_hms_surgery.action_hms_surgery&menu_id=%s" % self.env.ref("tgr_hms_surgery.main_menu_surgery").id
        )
        return res

