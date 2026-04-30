# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError

RESULT_TYPE = [
    ("quantitative", "Cuantitativo"),
    ("semiquantitative", "Semicuantitativo"),
    ("qualitative", "Cualitativo"),
]


class TGRLabTestUom(models.Model):
    _name = "tgr.lab.test.uom"
    _description = "Lab Test UOM"
    _order = "sequence asc"
    _rec_name = "code"

    name = fields.Char(string="UOM Name", required=True)
    code = fields.Char(
        string="Code",
        required=True,
        index=True,
        help="Short name - code for the test UOM",
    )
    sequence = fields.Integer("Sequence", default="100")

    _sql_constraints = [
        ("code_uniq", "unique (name)", "The Lab Test code must be unique")
    ]


class AcsLaboratory(models.Model):
    _name = "tgr.laboratory"
    _description = "Laboratory"
    _inherit = ["mail.thread", "mail.activity.mixin", "tgr.hms.mixin"]
    _inherits = {
        "res.partner": "partner_id",
    }

    description = fields.Text()
    is_collection_center = fields.Boolean("Is Collection Center")
    partner_id = fields.Many2one(
        "res.partner", "Partner", ondelete="restrict", required=True
    )
    active = fields.Boolean(string="Active", default=True)


class LabTest(models.Model):
    _name = "tgr.lab.test"
    _description = "Lab Test Type"
    _rec_names_search = ["name", "code"]

    name = fields.Char(
        string="Name", help="Test type, eg X-Ray, hemogram,biopsy...", index=True
    )
    code = fields.Char(string="Code", help="Short name - code for the test")
    description = fields.Text(string="Description")
    active = fields.Boolean(string="Active", default=True)
    product_id = fields.Many2one(
        "product.product",
        string="Servicio",
        required=True,
        help="Este es el servicio de laboratorio que se facturará al paciente o a su aseguradora.",
    )
    list_price = fields.Float(
        related="product_id.list_price",
        string="Precio",
        readonly=True,
        help="Precio de lista del servicio seleccionado",
    )
    critearea_ids = fields.One2many(
        "lab.test.critearea", "test_id", string="Test Cases"
    )
    remark = fields.Char(string="Remark")
    report = fields.Text(string="Test Report")
    company_id = fields.Many2one(
        "res.company",
        ondelete="restrict",
        string="Company",
        default=lambda self: self.env.company,
    )
    consumable_line_ids = fields.One2many(
        "hms.consumable.line", "lab_test_id", string="Consumable Line"
    )
    tgr_tat = fields.Char(string="Turnaround Time")
    result_value_type = fields.Selection(
        RESULT_TYPE,
        string="Result Type",
        default="quantitative",
    )
    sample_type_id = fields.Many2one("tgr.laboratory.sample.type", string="Sample Type")
    tgr_use_other_test_sample = fields.Boolean(
        string="Share Sample with Other Tests", default=True
    )
    subsequent_test_ids = fields.Many2many(
        "tgr.lab.test", "tgr_lab_test_rel", "test_id", "sub_test_id", "Subsequent Tests"
    )
    # ------------------------------------
    # custom tagre
    # ------------------------------------
    area_id = fields.Many2one(
        "laboratory.area",
        string="Área de Laboratorio",
        required=True,
        help="Área de laboratorio a la que pertenece este estudio",
    )
    # ------------------------------------
    # End custom tagre
    # ------------------------------------

    _sql_constraints = [
        (
            "code_company_uniq",
            "unique (code,company_id)",
            "The code of the account must be unique per company !",
        )
    ]

    def _compute_display_name(self):
        for rec in self:
            name = rec.name or ""
            if rec.code:
                name = "%s [%s]" % (rec.name, rec.code)
            rec.display_name = name

    def copy(self, default=None):
        self.ensure_one()
        new_name = _("%s (copy)") % self.name
        new_code = _("%s (copy)") % self.code
        default = dict(default or {}, name=new_name, code=new_code)
        return super(LabTest, self).copy(default)


class LabTestCritearea(models.Model):
    _name = "lab.test.critearea"
    _description = "Lab Test Criteria"
    _order = "sequence, id asc"

    name = fields.Char("Parameter")
    sequence = fields.Integer("Sequence", default=100)
    result = fields.Char("Result")
    lab_uom_id = fields.Many2one("tgr.lab.test.uom", string="UOM")
    remark = fields.Char("Remark")
    # normal_range = fields.Char("Normal Range")
    minimum_range = fields.Char("Rango Mínimo")
    maximum_range = fields.Char("Rango Máximo")
    test_id = fields.Many2one("tgr.lab.test", "Test type", ondelete="cascade")
    patient_lab_id = fields.Many2one(
        "patient.laboratory.test", "Lab Test", ondelete="cascade"
    )
    request_id = fields.Many2one(
        "tgr.laboratory.request", "Lab Request", ondelete="cascade"
    )
    company_id = fields.Many2one(
        "res.company",
        ondelete="restrict",
        string="Company",
        default=lambda self: self.env.company,
    )
    display_type = fields.Selection(
        [("line_section", "Section")], help="Technical field for UX purpose."
    )
    result_type = fields.Selection(
        [
            ("low", "Low"),
            ("normal", "Normal"),
            ("high", "High"),
            ("positive", "Positive"),
            ("negative", "Negative"),
        ],
        default="normal",
        string="Result Type",
        help="Technical field for UI purpose.",
    )
    result_value_type = fields.Selection(
        RESULT_TYPE,
        string="Result Value Type",
        default="quantitative",
    )

    lab_request_line_id = fields.Many2one("laboratory.request.line")

    @api.onchange("minimum_range")
    def onchange_minimum_range(self):
        if self.minimum_range and not self.maximum_range:
            self.maximum_range = self.minimum_range

    # @api.onchange("result")
    # def onchange_result(self):
    # if (
    # self.result and self.result_value_type == "quantitative"
    # and self.normal_range
    # ):
    # try:
    # split_value = self.normal_range.split("-")
    # low_range = high_range = 0
    # result = float(self.result)
    # if len(split_value) == 2:
    #     low_range = float(split_value[0])
    #     high_range = float(split_value[1])
    # elif len(split_value) == 2:
    #     low_range = float(split_value[0])
    #     high_range = float(split_value[0])
    #
    # if low_range or high_range:
    #     if result < low_range:
    #         self.result_type = "low"
    #     elif result > high_range:
    #         self.result_type = "high"
    #     elif result > low_range and result < high_range:
    #         self.result_type = "normal"
    #     elif result == low_range or result == high_range:
    #         self.result_type = "warning"
    # except:
    # pass


class LaboratoryGroupLine(models.Model):
    _name = "laboratory.group.line"
    _description = "Laboratory Group Line"

    group_id = fields.Many2one(
        "laboratory.group", ondelete="restrict", string="Laboratory Group"
    )
    test_id = fields.Many2one(
        "tgr.lab.test", string="Test", ondelete="cascade", required=True
    )
    tgr_tat = fields.Char(
        related="test_id.tgr_tat", string="Turnaround Time", readonly=True
    )
    instruction = fields.Char(string="Special Instructions")
    sale_price = fields.Float(string="Sale Price")

    @api.onchange("test_id")
    def onchange_test(self):
        if self.test_id:
            self.sale_price = self.test_id.product_id.lst_price


class LaboratoryGroup(models.Model):
    _name = "laboratory.group"
    _description = "Perfil de Laboratorio"

    name = fields.Char(string="Nombre del Perfil", required=True)
    line_ids = fields.One2many(
        "laboratory.group.line", "group_id", string="Medicament line"
    )


class LabSampleType(models.Model):
    _name = "tgr.laboratory.sample.type"
    _description = "Laboratory Sample Type"
    _order = "sequence asc"

    name = fields.Char(string="Name", required=True)
    sequence = fields.Integer("Sequence", default="100")
    description = fields.Text("Description")


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
