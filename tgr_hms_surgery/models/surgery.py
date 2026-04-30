# coding=utf-8
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class TGRSurgeryTemplate(models.Model):
    _name = "hms.surgery.template"
    _description = "Plantilla de Cirugía"

    name = fields.Char(string="Código de Cirugía", help="Código del procedimiento, por ejemplo código ICD-10-PCS de 7 caracteres")
    surgery_name = fields.Char(string="Nombre de la Cirugía")
    diseases_ids = fields.Many2many(
        "hms.diseases", "diseases_surgery_template_rel", "diseas_id", "surgery_id", string="Enfermedades"
    )
    # odoo18 remove diseases_id
    diseases_id = fields.Many2one("hms.diseases", ondelete="restrict", string="Enfermedad", help="Razón de la cirugía.")
    dietplan_id = fields.Many2one("hms.dietplan", ondelete="set null", string="Plan de Dieta")
    surgery_product_id = fields.Many2one("product.product", ondelete="cascade", string="Producto", required=True)
    diagnosis = fields.Text(string="Diagnóstico")
    clinincal_history = fields.Text(string="Historia Clínica")
    examination = fields.Text(string="Examen")
    investigation = fields.Text(string="Investigación")
    adv_on_dis = fields.Text(string="Consejos al dar de alta")
    notes = fields.Text(string="Notas Operatorias")
    classification = fields.Selection(
        [("o", "Opcional"), ("r", "Requerido"), ("u", "Urgente")], string="Clasificación de Cirugía", index=True
    )
    extra_info = fields.Text(string="Información Extra")
    special_precautions = fields.Text(string="Precauciones Especiales")
    consumable_line_ids = fields.One2many(
        "hms.consumable.line",
        "surgery_template_id",
        string="Línea de Consumibles",
        help="Lista de artículos consumidos durante la cirugía.",
    )
    medicament_line_ids = fields.One2many(
        "medicament.line",
        "surgery_template_id",
        string="Línea de Medicamentos",
        help="Definir los medicamentos a tomar después de la cirugía",
    )
    company_id = fields.Many2one(
        "res.company", ondelete="restrict", string="Hospital", default=lambda self: self.env.company
    )


class TGRSurgery(models.Model):
    _name = "hms.surgery"
    _description = "Cirugía"
    _inherit = ["mail.thread", "mail.activity.mixin", "tgr.hms.mixin"]
    _order = "id desc"

    @api.model
    def _default_prechecklist(self):
        vals = []
        prechecklists = self.env["pre.operative.check.list.template"].search([])
        for prechecklist in prechecklists:
            vals.append(
                (
                    0,
                    0,
                    {
                        "name": prechecklist.name,
                        "remark": prechecklist.remark,
                    },
                )
            )
        return vals

    @api.depends("pre_operative_checklist_ids", "pre_operative_checklist_ids.is_done")
    def _compute_checklist_done(self):
        for rec in self:
            if rec.pre_operative_checklist_ids:
                done_checklist = rec.pre_operative_checklist_ids.filtered(lambda s: s.is_done)
                rec.pre_operative_checklist_done = (len(done_checklist) * 100) / len(rec.pre_operative_checklist_ids)
            else:
                rec.pre_operative_checklist_done = 0

    @api.depends("patient_id")
    def _get_patient_age(self):
        for rec in self:
            if rec.patient_id:
                rec.age = rec.patient_id.age

    def _tgr_rec_count(self):
        for rec in self:
            rec.invoice_count = len(self.invoice_ids)

    name = fields.Char(string="Número de Cirugía", copy=False, readonly=True)
    state = fields.Selection(
        [
            ("draft", "Borrador"),
            ("confirm", "Confirmado"),
            ("cancel", "Cancelado"),
            ("done", "Realizado"),
        ],
        string="Estado",
        default="draft",
    )
    surgery_name = fields.Char(string="Nombre de la Cirugía")
    diseases_ids = fields.Many2many(
        "hms.diseases", "diseases_surgery_rel", "diseas_id", "surgery_id", string="Enfermedades"
    )
    # odoo18 remove diseases_id
    diseases_id = fields.Many2one("hms.diseases", ondelete="restrict", string="Enfermedad", help="Razón de la cirugía.")
    dietplan_id = fields.Many2one("hms.dietplan", ondelete="set null", string="Plan de Dieta")
    surgery_product_id = fields.Many2one("product.product", ondelete="cascade", string="Producto de Cirugía", required=True)
    surgery_template_id = fields.Many2one("hms.surgery.template", ondelete="restrict", string="Plantilla de Cirugía")
    patient_id = fields.Many2one("hms.patient", ondelete="restrict", string="Paciente")
    diagnosis = fields.Text(string="Diagnóstico")
    clinincal_history = fields.Text(string="Historia Clínica")
    examination = fields.Text(string="Examen")
    investigation = fields.Text(string="Investigación")
    adv_on_dis = fields.Text(string="Consejos al dar de alta")
    notes = fields.Text(string="Notas Operatorias")
    classification = fields.Selection(
        [("o", "Opcional"), ("r", "Requerido"), ("u", "Urgente")], string="Clasificación de Cirugía", index=True
    )
    age = fields.Char(
        string="Edad del paciente",
        help="Edad del paciente al momento de la cirugía. Puede ser estimativa",
        compute="_get_patient_age",
        store=True,
    )
    extra_info = fields.Text(string="Información Extra")
    special_precautions = fields.Text(string="Precauciones Especiales")
    consumable_line_ids = fields.One2many(
        "hms.consumable.line",
        "surgery_id",
        string="Línea de Consumibles",
        help="Lista de artículos consumidos durante la cirugía.",
    )
    medicament_line_ids = fields.One2many(
        "medicament.line",
        "surgery_id",
        string="Línea de Medicamentos",
        help="Definir los medicamentos a tomar después de la cirugía",
    )
    invoice_exempt = fields.Boolean(string="Exento de Factura")

    # Hospitalization Surgery
    start_date = fields.Datetime(string="Fecha de Cirugía")
    end_date = fields.Datetime(string="Fecha Final")
    anesthetist_id = fields.Many2one(
        "hms.physician", string="Anestesista", ondelete="set null", help="Datos del anestesista del paciente"
    )
    anesthesia_id = fields.Many2one("hms.anesthesia", ondelete="set null", string="Anestesia")
    primary_physician_id = fields.Many2one("hms.physician", ondelete="restrict", string="Cirujano Principal")
    primary_physician_ids = fields.Many2many(
        "hms.physician", "hosp_pri_doc_rel", "hosp_id", "doc_id", string="Cirujanos Principales"
    )
    assisting_surgeon_ids = fields.Many2many(
        "hms.physician", "hosp_doc_rel", "hosp_id", "doc_id", string="Cirujanos Asistentes"
    )
    scrub_nurse_id = fields.Many2one("res.users", ondelete="set null", string="Enfermera Instrumentista")
    pre_operative_checklist_ids = fields.One2many(
        "pre.operative.check.list",
        "surgery_id",
        string="Lista de Verificación Preoperatoria",
        default=lambda self: self._default_prechecklist(),
    )
    pre_operative_checklist_done = fields.Float(
        "Lista de Verificación Preoperatoria Realizada", compute="_compute_checklist_done", store=True
    )
    notes = fields.Text(string="Notas Operatorias")
    post_instruction = fields.Text(string="Instrucciones")

    special_precautions = fields.Text(string="Precauciones Especiales")
    company_id = fields.Many2one(
        "res.company", ondelete="restrict", string="Hospital", default=lambda self: self.env.company
    )
    invoice_id = fields.Many2one("account.move", string="Factura", copy=False)
    treatment_id = fields.Many2one("hms.treatment", string="Tratamiento", copy=False)
    department_id = fields.Many2one(
        "hr.department",
        ondelete="restrict",
        domain=[("patient_department", "=", True)],
        string="Departamento",
        tracking=True,
    )
    appointment_id = fields.Many2one("hms.appointment", string="Cita", copy=False)
    invoice_ids = fields.One2many("account.move", "surgery_id", string="Facturas")
    invoice_count = fields.Integer(compute="_tgr_rec_count", string="# Facturas")

    @api.onchange("surgery_template_id")
    def onchange_surgery_id(self):
        medicament_lines = []
        consumable_lines = []
        Consumable = self.env["hms.consumable.line"]
        MedicamentLine = self.env["medicament.line"]
        if self.surgery_template_id:
            self.surgery_name = self.surgery_template_id.surgery_name
            self.diseases_ids = self.surgery_template_id.diseases_ids
            self.surgery_product_id = (
                self.surgery_template_id.surgery_product_id and self.surgery_template_id.surgery_product_id.id
            )
            self.diagnosis = self.surgery_template_id.diagnosis
            self.clinincal_history = self.surgery_template_id.clinincal_history
            self.examination = self.surgery_template_id.examination
            self.investigation = self.surgery_template_id.investigation
            self.adv_on_dis = self.surgery_template_id.adv_on_dis
            self.notes = self.surgery_template_id.notes
            self.classification = self.surgery_template_id.classification

            for line in self.surgery_template_id.consumable_line_ids:
                self.consumable_line_ids += Consumable.new(
                    {
                        "product_id": line.product_id.id,
                        "product_uom_id": line.product_uom_id and line.product_uom_id.id or False,
                        "qty": line.qty,
                        "lot_id": line.lot_id and line.lot_id.id or False,
                    }
                )

            for line in self.surgery_template_id.medicament_line_ids:
                self.medicament_line_ids += MedicamentLine.new(
                    {
                        "product_id": line.product_id.id,
                        "common_dosage_id": line.common_dosage_id and line.common_dosage_id.id or False,
                        "dose": line.dose,
                        "active_component_ids": [(6, 0, [x.id for x in line.active_component_ids])],
                        "form_id": line.form_id.id,
                        "qty": line.qty,
                        "days": line.days,
                        "instruction": line.instruction,
                    }
                )

    @api.model_create_multi
    def create(self, vals_list):
        for values in vals_list:
            values["name"] = self.env["ir.sequence"].next_by_code("hms.surgery") or "Cirugía#"
        return super().create(vals_list)

    def action_confirm(self):
        self.state = "confirm"

    def action_done(self):
        self.state = "done"
        self.consume_surgery_material()

    def action_cancel(self):
        self.state = "cancel"

    def action_draft(self):
        self.state = "draft"

    def tgr_get_consume_locations(self):
        if not self.company_id.tgr_surgery_usage_location_id:
            raise UserError(_("Por favor defina una ubicación donde los consumibles serán usados en la configuración."))
        if not self.company_id.tgr_surgery_stock_location_id:
            raise UserError(_("Por favor defina una ubicación de cirugía de donde se tomarán los consumibles."))
        source_location_id = self.company_id.tgr_surgery_stock_location_id.id
        dest_location_id = self.company_id.tgr_surgery_usage_location_id.id
        return source_location_id, dest_location_id

    def consume_surgery_material(self):
        for rec in self:
            source_location_id, dest_location_id = rec.tgr_get_consume_locations()
            for line in rec.consumable_line_ids.filtered(lambda s: not s.move_id):
                if line.product_id.is_kit_product:
                    move_ids = []
                    for kit_line in line.product_id.tgr_kit_line_ids:
                        if kit_line.product_id.tracking != "none":
                            raise UserError(
                                _(
                                    "En las líneas de consumibles no se permite un producto tipo Kit con componentes que tengan seguimiento por lote/serie. Por favor elimine dicho producto kit de las líneas de consumibles."
                                )
                            )
                        move = self.consume_material(
                            source_location_id,
                            dest_location_id,
                            {"product": kit_line.product_id, "qty": kit_line.product_qty * line.qty},
                        )
                        move.surgery_id = rec.id
                        move_ids.append(move.id)
                    # Set move_id on line also to avoid issue
                    line.move_id = move.id
                    line.move_ids = [(6, 0, move_ids)]
                else:
                    move = self.consume_material(
                        source_location_id,
                        dest_location_id,
                        {
                            "product": line.product_id,
                            "qty": line.qty,
                            "lot_id": line.lot_id and line.lot_id.id or False,
                        },
                    )
                    move.surgery_id = rec.id
                    line.move_id = move.id

    def get_surgery_invoice_data(self):
        if self.invoice_exempt:
            return []
        product_data = [
            {
                "name": _("Cargos de Cirugía"),
            }
        ]
        for surgery in self:
            if surgery.surgery_product_id:
                # Line for Surgery Charge
                product_data.append(
                    {
                        "product_id": surgery.surgery_product_id,
                        "quantity": 1,
                    }
                )

            # Line for Surgery Consumables
            for surgery_consumable in surgery.consumable_line_ids:
                product_data.append(
                    {
                        "product_id": surgery_consumable.product_id,
                        "quantity": surgery_consumable.qty,
                        "lot_id": surgery_consumable.lot_id and surgery_consumable.lot_id.id or False,
                        "product_uom_id": surgery_consumable.product_uom_id.id,
                    }
                )
        return product_data

    def action_create_invoice(self):
        product_data = self.get_surgery_invoice_data()
        inv_data = {
            "physician_id": self.primary_physician_id and self.primary_physician_id.id or False,
            "hospital_invoice_type": "surgery",
        }
        tgr_context = {"commission_partner_ids": self.primary_physician_id.partner_id.id}
        invoice_id = self.with_context(tgr_context).tgr_create_invoice(
            partner=self.patient_id.partner_id, patient=self.patient_id, product_data=product_data, inv_data=inv_data
        )
        invoice_id.write(
            {
                "surgery_id": self.id,
            }
        )
        self.invoice_id = invoice_id.id
        return invoice_id

    def action_prescription(self):
        action = self.env["ir.actions.actions"]._for_xml_id("tgr_hms.act_open_hms_prescription_order_view")
        action["domain"] = [("surgery_id", "=", self.id)]
        action["context"] = {
            "default_patient_id": self.patient_id.id,
            "default_diseases_ids": [(6, 0, self.diseases_ids.ids)],
            "default_surgery_id": self.id,
        }
        return action

    def view_invoice(self):
        invoices = self.env["account.move"].search([("surgery_id", "=", self.id)])
        action = self.tgr_action_view_invoice(invoices)
        return action

    def button_pres_request(self):
        action = self.env["ir.actions.actions"]._for_xml_id("tgr_hms.act_open_hms_prescription_order_view")
        action["domain"] = [("surgery_id", "=", self.id)]
        action["views"] = [(self.env.ref("tgr_hms.view_hms_prescription_order_form").id, "form")]
        PrescriptionLine = self.env["prescription.line"]
        medicament_lines = []

        for line in self.medicament_line_ids:
            medicament_lines.append(
                (
                    0,
                    0,
                    {
                        "product_id": line.product_id.id,
                        "common_dosage_id": line.common_dosage_id and line.common_dosage_id.id or False,
                        "dose": line.dose,
                        "active_component_ids": [(6, 0, [x.id for x in line.active_component_ids])],
                        "form_id": line.form_id.id,
                        "qty_per_day": line.qty,
                        "days": line.days,
                        "short_comment": line.instruction,
                    },
                )
            )

        action["context"] = {
            "default_patient_id": self.patient_id.id,
            "default_diseases_ids": [(6, 0, self.diseases_ids.ids)],
            "default_treatment_id": self.treatment_id and self.treatment_id.id or False,
            "default_surgery_id": self.id,
            "default_prescription_line_ids": medicament_lines,
        }
        return action

    # method to create get invocie data and set passed invocie id.
    def tgr_common_invoice_surgery_data(self, invoice_id=False):
        data = []
        if self.ids:
            data = self.get_surgery_invoice_data()
            if invoice_id:
                self.invoice_id = invoice_id.id
        return data
