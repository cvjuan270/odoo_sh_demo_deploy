import logging
from datetime import datetime, timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class PatientLabSample(models.Model):
    _name = "tgr.patient.laboratory.sample"
    _description = "Patient Laboratory Sample"
    _order = "date desc, id desc"

    name = fields.Char(string="Name", help="Sample Name", readonly=True, copy=False, index=True)
    patient_id = fields.Many2one("hms.patient", string="Patient", required=True)
    user_id = fields.Many2one("res.users", string="User", default=lambda self: self.env.user)
    date = fields.Datetime(string="Date", default=fields.Datetime.now)
    request_id = fields.Many2one(
        "tgr.laboratory.request",
        string="Lab Request",
        ondelete="restrict",
        required=True,
    )
    company_id = fields.Many2one(
        "res.company",
        ondelete="restrict",
        string="Company",
        default=lambda self: self.env.company,
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("collect", "Collected"),
            ("examine", "Examined"),
            ("cancel", "Cancel"),
        ],
        string="Status",
        readonly=True,
        default="draft",
    )
    sample_type_id = fields.Many2one("tgr.laboratory.sample.type", string="Sample Type", required=True)
    container_name = fields.Char(
        string="Sample Container Code",
        help="If using preprinted sample tube/slide/box no can be updated here.",
        copy=False,
        index=True,
    )
    patient_test_ids = fields.Many2many(
        "patient.laboratory.test",
        "test_lab_sample_rel",
        "sample_id",
        "test_id",
        string="Patient Lab Tests",
    )
    test_ids = fields.Many2many(
        "tgr.lab.test",
        "tgr_test_lab_sample_rel",
        "sample_id",
        "test_id",
        string="Lab Tests",
    )

    notes = fields.Text(string="Notes")

    area_id = fields.Many2one("laboratory.area", string="Area de Laboratorio")

    # Just to make object selectable in selction field this is required: Waiting Screen
    tgr_show_in_wc = fields.Boolean(default=True)

    _sql_constraints = [
        (
            "name_company_uniq",
            "unique (name,company_id)",
            "Sample Name must be unique per company !",
        )
    ]

    @api.model_create_multi
    def create(self, vals_list):
        for values in vals_list:
            area_code = False
            area_id = values.get("area_id")
            if area_id:
                area = self.env["laboratory.area"].browse(area_id)
                area_code = area.code
            values["name"] = self.env["ir.sequence"].next_by_code("tgr.patient.laboratory.sample", values.get("date")) + "{}".format(
                area_code and "-%s" % area_code or ""
            )
            print(vals_list)
        return super().create(vals_list)

    def unlink(self):
        for rec in self:
            if rec.state not in ["draft"]:
                raise UserError(_("Record can be delete only in Draft state."))
        return super(PatientLabSample, self).unlink()

    @api.onchange("request_id")
    def onchange_request_id(self):
        if self.request_id:
            self.patient_id = self.request_id.patient_id.id

    def action_collect(self):
        self.state = "collect"

    def action_examine(self):
        self.state = "examine"

    def action_cancel(self):
        self.state = "cancel"

    def action_bulk_examine(self):
        for record in self:
            if record.state == "collect":
                record.action_examine()
        return True

    def action_bulk_collect_and_examine(self):
        for record in self:
            if record.state == "draft":
                record.action_collect()
                record.action_examine()
        return True
