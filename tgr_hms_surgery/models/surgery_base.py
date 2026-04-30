# -*- encoding: utf-8 -*-
from odoo import api, fields, models, _


class Anesthesia(models.Model):
    _name = "hms.anesthesia"
    _rec_name = "name"
    _description = "Anestesia"

    name = fields.Char("Nombre de Anestesia", required=True)


class PreOpetativeCheckListTemplate(models.Model):
    _name = "pre.operative.check.list.template"
    _description = "Plantilla de Lista de Verificación Preoperatoria"

    name = fields.Char(string="Nombre", required=True)
    remark = fields.Char(string="Observaciones")


class PreOpetativeCheckList(models.Model):
    _name = "pre.operative.check.list"
    _description = "Lista de Verificación Preoperatoria"

    name = fields.Char(string="Nombre", required=True)
    is_done = fields.Boolean(string="Hecho")
    remark = fields.Char(string="Observaciones")
    surgery_id = fields.Many2one("hms.surgery", ondelete="cascade", string="Cirugía")


class TGRDietplan(models.Model):
    _name = "hms.dietplan"
    _description = "Plan de Dieta"

    name = fields.Char(string="Nombre", required=True)


class PastSurgerys(models.Model):
    _name = "past.surgeries"
    _description = "Cirugías Pasadas"

    result = fields.Char(string="Resultado")
    date = fields.Date(string="Fecha")
    hosp_or_doctor = fields.Char(string="Hospital/Doctor")
    description = fields.Char(string="Descripción", size=128)
    complication = fields.Text("Complicación")
    patient_id = fields.Many2one(
        "hms.patient", ondelete="restrict", string="ID Paciente", help="Mencione las cirugías pasadas de este paciente."
    )


class TGRMedicamentLine(models.Model):
    _name = "medicament.line"
    _description = "Líneas de Medicamentos"

    product_id = fields.Many2one("product.product", ondelete="cascade", string="Nombre del Medicamento")
    name = fields.Char(string="Nombre")
    product_uom_category_id = fields.Many2one("uom.category", related="product_id.uom_id.category_id")
    medicine_uom_id = fields.Many2one(
        "uom.uom",
        string="Unidad",
        help="Cantidad de medicamento (ej. 250 mg) por dosis",
        domain="[('category_id', '=', product_uom_category_id)]",
    )
    qty = fields.Float(string="Cant", default=1.0)
    active_component_ids = fields.Many2many(
        "active.comp", "medica_line_comp_rel", "medica_id", "line_id", string="Componente Activo"
    )
    form_id = fields.Many2one("drug.form", ondelete="cascade", string="Forma", help="Forma del fármaco, como tableta o gel")
    dose = fields.Float(string="Dosificación", digits=(16, 2), help="Cantidad de medicamento (ej. 250 mg) por dosis")
    days = fields.Integer("Días")
    common_dosage_id = fields.Many2one(
        "medicament.dosage", ondelete="cascade", string="Frecuencia", help="Forma del fármaco, como tableta o gel"
    )
    surgery_template_id = fields.Many2one("hms.surgery.template", ondelete="cascade", string="Plantilla de Cirugía")
    surgery_id = fields.Many2one("hms.surgery", ondelete="cascade", string="Cirugía")
    instruction = fields.Char("Instrucciones")

    @api.onchange("product_id")
    def onchange_product_id(self):
        if self.product_id:
            self.form_id = self.product_id.form_id.id
            self.dose = self.product_id.dosage
            self.medicine_uom_id = self.product_id.uom_id.id
            self.common_dosage_id = self.product_id.common_dosage_id.id
            self.active_component_ids = [(6, 0, [x.id for x in self.product_id.active_component_ids])]
