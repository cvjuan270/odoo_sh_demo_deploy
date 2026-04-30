# coding=utf-8

from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import ValidationError, UserError


class Hospitalization(models.Model):
    _name = "tgr.hospitalization"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'tgr.hms.mixin']
    _description = "Hospitalización del Paciente"
    _order = "id desc"

    @api.model
    def _default_checklist(self):
        vals = []
        checklists = self.env['inpatient.checklist.template'].search([])
        for checklist in checklists:
            vals.append((0, 0, {
                'name': checklist.name,
                'remark': checklist.remark,
            }))
        return vals

    @api.model
    def _default_prewardklist(self):
        vals = []
        prechecklists = self.env['pre.ward.check.list.template'].search([])
        for prechecklist in prechecklists:
            vals.append((0,0,{
                'name': prechecklist.name,
                'remark': prechecklist.remark,
            }))
        return vals

    @api.depends('checklist_ids','checklist_ids.is_done')
    def _compute_checklist_done(self):
        for rec in self:
            if rec.checklist_ids:
                done_checklist = rec.checklist_ids.filtered(lambda s: s.is_done)
                rec.checklist_done = (len(done_checklist)* 100)/len(rec.checklist_ids)
            else:
                rec.checklist_done = 0

    @api.depends('pre_ward_checklist_ids','pre_ward_checklist_ids.is_done')
    def _compute_pre_ward_checklist_done(self):
        for rec in self:
            if rec.pre_ward_checklist_ids:
                done_checklist = rec.pre_ward_checklist_ids.filtered(lambda s: s.is_done)
                rec.pre_ward_checklist_done = (len(done_checklist)* 100)/len(rec.pre_ward_checklist_ids)
            else:
                rec.pre_ward_checklist_done = 0

    def _rec_count(self):
        for rec in self:
            rec.invoice_count = len(rec.sudo().invoice_ids)
            rec.prescription_count = len(rec.prescription_ids.ids)
            rec.surgery_count = len(rec.surgery_ids)
            rec.accommodation_count = len(rec.accommodation_history_ids)
            rec.evaluation_count = len(rec.evaluation_ids)
            rec.procedure_count = len(rec.procedure_ids)

    name = fields.Char(string='Hospitalización#', copy=False, default="Hospitalización#", tracking=True)
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('confirm', 'Confirmado'),
        ('reserved', 'Reservado'),
        ('hosp','Hospitalizado'), 
        ('discharged', 'Alta'),
        ('cancel', 'Cancelado'),
        ('done', 'Realizado'),], string='Estado', default='draft', tracking=True)
    patient_id = fields.Many2one('hms.patient', ondelete="restrict", string='Paciente', tracking=True)
    image_128 = fields.Binary(related='patient_id.image_128',string='Imagen', readonly=True)
    age = fields.Char(string="Edad" ,related="patient_id.age")
    appointment_id = fields.Many2one('hms.appointment', ondelete="restrict", 
        string='Cita')
    hospitalization_date = fields.Datetime(string='Fecha de Hospitalización', 
        default=fields.Datetime.now, tracking=True)
    company_id = fields.Many2one('res.company', ondelete="restrict", 
        string='Hospital', default=lambda self: self.env.company)
    department_id = fields.Many2one('hr.department', ondelete="restrict", 
        string='Departamento', domain=[('patient_department', '=', True)])
    attending_physician_ids = fields.Many2many('hms.physician','hosp_pri_att_doc_rel','hosp_id','doc_id',
        string='Médicos Principales')
    relative_id = fields.Many2one('res.partner', ondelete="cascade", 
        domain=[('type', '=', 'contact')], string='Nombre del Pariente del Paciente')
    relative_number = fields.Char(string='Número del Pariente del Paciente')
    ward_id = fields.Many2one('hospital.ward', ondelete="restrict", string='Sala/Habitación')
    bed_id = fields.Many2one ('hospital.bed', ondelete="restrict", string='Cama No.')
    admission_type = fields.Selection([
        ('routine','Rutina'),
        ('elective','Electiva'),
        ('urgent','Urgente'),
        ('emergency','Emergencia')], string='Tipo de Admisión', default='routine')
    diseases_ids = fields.Many2many('hms.diseases', 'diseases_hospitalization_rel', 'diseas_id', 'hospitalization_id', 
        string='Enfermedades')
    discharge_date = fields.Datetime (string='Fecha de Alta', tracking=True)
    invoice_exempt = fields.Boolean(string='Exento de Factura')
    accommodation_history_ids = fields.One2many("patient.accommodation.history", "hospitalization_id", 
        string="Historial de Alojamiento")
    accommodation_count = fields.Integer(compute='_rec_count', string='# Historial de Alojamiento')
    physician_id = fields.Many2one('hms.physician', string='Médico Principal', tracking=True)

    #CheckLists
    checklist_ids = fields.One2many('inpatient.checklist', 'hospitalization_id', 
        string='Lista de Verificación de Admisión', default=lambda self: self._default_checklist())
    checklist_done = fields.Float('Lista de Verificación de Admisión Realizada', compute='_compute_checklist_done', store=True)
    pre_ward_checklist_ids = fields.One2many('pre.ward.check.list', 'hospitalization_id', 
        string='Lista de Verificación Pre-Sala', default=lambda self: self._default_prewardklist())
    pre_ward_checklist_done = fields.Float('Lista de Verificación Pre-Sala Realizada', compute='_compute_pre_ward_checklist_done', store=True)

    #Hospitalization Surgery
    picking_type_id = fields.Many2one('stock.picking.type', ondelete="restrict", 
        string='Tipo de Albarán')

    consumable_line_ids = fields.One2many('hms.consumable.line', 'hospitalization_id',
        string='Línea de Consumibles')

    # Discharge fields
    diagnosis = fields.Text(string="Diagnóstico")
    clinincal_history = fields.Text(string="Resumen Clínico")
    examination = fields.Text(string="Examinación")
    investigation = fields.Text(string="Investigación")
    adv_on_dis = fields.Text(string="Consejo sobre el Alta")

    discharge_diagnosis = fields.Text(string="Diagnóstico de Alta")
    op_note = fields.Text(string="Nota Operativa")
    post_operative = fields.Text(string="Curso Postoperatorio")
    instructions = fields.Text(string='Instrucciones')

    #Legal Details
    legal_case = fields.Boolean('Caso Legal')
    medico_legal = fields.Selection([
        ('yes','Sí'),
        ('no','No')], string="Si es Médico Legal")
    reported_to_police = fields.Selection([
        ('yes','Sí'),
        ('no','No')], string="Reportado a la policía")
    fir_no = fields.Char(string="No. FIR", help="Registration number of the police complaint.")
    fir_reason = fields.Char(string="Si no se reportó a la policía, dé la razón")

    #For Basic Care Plan
    nurse_id = fields.Many2one('res.users', ondelete="cascade", string='Enfermera Principal', 
        help='Anesthetist data of the patient')
    nursing_plan = fields.Text (string='Plan de Enfermería')
    physician_ward_round_ids = fields.One2many('ward.rounds', 'hospitalization_id', string='Rondas de Sala del Médico')

    discharge_plan = fields.Text (string='Plan de Alta')
    move_ids = fields.One2many('stock.move','hospitalization_id', string='Movimientos')
    invoice_ids = fields.One2many('account.move', 'hospitalization_id', 'Facturas')

    invoice_count = fields.Integer(compute='_rec_count', string='# Facturas')
    prescription_ids = fields.One2many('prescription.order', 'hospitalization_id', 'Recetas')
    prescription_count = fields.Integer(compute='_rec_count', string='# Recetas')
    surgery_ids = fields.One2many('hms.surgery', 'hospitalization_id', "Cirugías")
    surgery_count = fields.Integer(compute='_rec_count', string='# Cirugía')
    ref_physician_id = fields.Many2one('res.partner', ondelete='restrict', string='Médico de Referencia', 
        index=True, help='Referring Physician')
    death_register_id = fields.Many2one('patient.death.register', string='Registro de Defunción')
    care_plan_template_id = fields.Many2one('hms.care.plan.template', ondelete='restrict',
        string= "Plantilla de Plan de Cuidados")

    evaluation_ids = fields.One2many('tgr.patient.evaluation', 'hospitalization_id', '# Evaluaciones')
    evaluation_count = fields.Integer(compute="_rec_count", string='Evaluaciones')
    procedure_ids = fields.One2many('tgr.patient.procedure', 'hospitalization_id', 'Procedimientos')
    procedure_count = fields.Integer(compute="_rec_count", string='# Procedimientos')
    allow_bed_reservation = fields.Boolean('Permitir Reserva de Cama', related='company_id.allow_bed_reservation')

    last_evaluation_id = fields.Many2one("tgr.patient.evaluation", related='patient_id.last_evaluation_id', string="Última Evaluación")
    weight = fields.Float(related="last_evaluation_id.weight", string='Peso', help="Weight in KG", readonly=True)
    height = fields.Float(related="last_evaluation_id.height", string='Altura', help="Height in cm", readonly=True)
    temp = fields.Float(related="last_evaluation_id.temp", string='Temp', readonly=True)
    hr = fields.Integer(related="last_evaluation_id.hr", string='HR', help="Heart Rate", readonly=True)
    rr = fields.Integer(related="last_evaluation_id.rr", string='RR', readonly=True, help='Respiratory Rate')
    systolic_bp = fields.Integer(related="last_evaluation_id.systolic_bp", string="PA Sistólica")
    diastolic_bp = fields.Integer(related="last_evaluation_id.diastolic_bp", string="PA Diastólica")
    spo2 = fields.Integer(related="last_evaluation_id.spo2", string='SpO2', readonly=True, 
        help='Oxygen Saturation, percentage of oxygen bound to hemoglobin')
    rbs = fields.Integer(related="last_evaluation_id.rbs", string='RBS', readonly=True, 
        help='Random blood sugar measures blood glucose regardless of when you last ate.')
    bmi = fields.Float(related="last_evaluation_id.bmi", string='Índice de Masa Corporal', readonly=True)
    bmi_state = fields.Selection(related="last_evaluation_id.bmi_state", string='Estado IMC', readonly=True)
    
    pain_level = fields.Selection(related="last_evaluation_id.pain_level", string="Nivel de Dolor", readonly=True)
    pain = fields.Selection(related="last_evaluation_id.pain", string="Dolor", readonly=True)

    tgr_weight_name = fields.Char(related="last_evaluation_id.tgr_weight_name", string='Etiqueta de unidad de medida de peso del paciente')
    tgr_height_name = fields.Char(related="last_evaluation_id.tgr_height_name", string='Etiqueta de unidad de medida de altura del paciente')
    tgr_temp_name = fields.Char(related="last_evaluation_id.tgr_temp_name", string='Etiqueta de unidad de medida de temperatura del paciente')
    tgr_spo2_name = fields.Char(related="last_evaluation_id.tgr_spo2_name", string='Etiqueta de unidad de medida de SpO2 del paciente')
    tgr_rbs_name = fields.Char(related="last_evaluation_id.tgr_rbs_name", string='Etiqueta de unidad de medida de RBS del paciente')
    pricelist_id = fields.Many2one('product.pricelist', string='Tarifa', check_company=True, 
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help="If you change the pricelist, related invoice will be affected.")
    
    _sql_constraints = [
        ('name_company_uniq', 'unique (name,company_id)', '¡La hospitalización debe ser única por compañía!')
    ]

    @api.onchange('care_plan_template_id')
    def on_change_care_plan_template_id(self):
        if self.care_plan_template_id:
            self.nursing_plan = self.care_plan_template_id.nursing_plan

    def action_view_evaluation(self):
        action = self.env["ir.actions.actions"]._for_xml_id("tgr_hms.action_tgr_patient_evaluation")
        action['domain'] = [('hospitalization_id','=',self.id)]
        action['context'] = {'default_patient_id': self.patient_id.id, 'default_hospitalization_id': self.id, 'default_physician_id': self.physician_id.id}
        return action

    def action_view_procedures(self):
        action = self.env["ir.actions.actions"]._for_xml_id("tgr_hms.action_tgr_patient_procedure")
        action['domain'] = [('hospitalization_id','=',self.id)]
        action['context'] = {
            'default_patient_id': self.patient_id.id,
            'default_physician_id': self.physician_id.id,
            'default_department_id': self.department_id.id,
            'default_hospitalization_id': self.id
        }
        return action

    @api.model_create_multi
    def create(self, vals_list):
        for values in vals_list:
            patient_id = values.get('patient_id')
            active_hospitalizations = self.search([('patient_id','=',patient_id),('state','not in',['cancel','done','discharged'])])
            if active_hospitalizations:
                raise ValidationError(_("La hospitalización del paciente ya está activa en este momento. Por favor complétela antes de crear una nueva."))
            if values.get('name', 'Hospitalization#') == 'Hospitalization#':
                values['name'] = self.env['ir.sequence'].next_by_code('tgr.hospitalization') or 'Hospitalization#'
        return super().create(vals_list)

    def action_confirm(self):
        self.state = 'confirm'

    def action_reserve(self):
        History = self.env['patient.accommodation.history']
        for rec in self:
            rec.bed_id.sudo().write({'state': 'reserved'})
            rec.state = 'reserved'
            History.sudo().create({
                'hospitalization_id': rec.id,
                'patient_id': rec.patient_id.id,
                'ward_id': self.ward_id.id,
                'bed_id': self.bed_id.id,
                'start_date': datetime.now(),
            })

    def action_hospitalize(self):
        History = self.env['patient.accommodation.history']
        for rec in self:
            if not self.allow_bed_reservation:
                History.sudo().create({
                    'hospitalization_id': rec.id,
                    'patient_id': rec.patient_id.id,
                    'ward_id': self.ward_id.id,
                    'bed_id': self.bed_id.id,
                    'start_date': datetime.now(),
                })
            rec.bed_id.sudo().write({'state': 'occupied'})
            rec.state = 'hosp'
            rec.patient_id.write({'hospitalized': True})

    def action_discharge(self):
        for rec in self:
            rec.bed_id.sudo().write({'state': 'free'})
            rec.state = 'discharged'
            rec.discharge_date = datetime.now()
            for history in rec.accommodation_history_ids:
                if rec.bed_id == history.bed_id:
                    history.sudo().end_date = datetime.now()
            rec.patient_id.write({'discharged': True})

    def action_done(self):
        self.state = 'done'
        self.consume_hopitalization_material()
        if not self.discharge_date:
            self.discharge_date = datetime.now()

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'
            rec.bed_id.sudo().write({'state': 'free'}) 

    def action_create_evaluation(self):
        action = self.env["ir.actions.actions"]._for_xml_id("tgr_hms.action_tgr_patient_evaluation_popup")
        action['domain'] = [('patient_id','=',self.id)]
        action['context'] = {'default_patient_id': self.patient_id.id, 'default_physician_id': self.physician_id.id, 'default_hospitalization_id': self.id}
        return action

    def action_draft(self):
        self.state = 'draft'

    def action_prescription(self):
        action = self.env["ir.actions.actions"]._for_xml_id("tgr_hms.act_open_hms_prescription_order_view")
        action['domain'] = [('hospitalization_id', '=', self.id)]
        action['context'] = {
            'default_patient_id': self.patient_id.id,
            'default_physician_id':self.physician_id.id,
            'default_hospitalization_id': self.id,
            'default_ward_id': self.ward_id.id,
            'default_diseases_ids': [(6,0,self.diseases_ids.ids)],
            'default_bed_id': self.bed_id.id}
        return action

    def action_accommodation_history(self):
        action = self.env["ir.actions.actions"]._for_xml_id("tgr_hms_hospitalization.action_accommodation_history")
        action['domain'] = [('hospitalization_id', '=', self.id)]
        action['context'] = {
            'default_patient_id': self.patient_id.id,
            'default_hospitalization_id': self.id}
        return action

    def action_view_surgery(self):
        action = self.env["ir.actions.actions"]._for_xml_id("tgr_hms_surgery.action_hms_surgery")
        action['domain'] = [('hospitalization_id', '=', self.id)]
        action['context'] = {
            'default_patient_id': self.patient_id.id,
            'default_hospitalization_id': self.id}
        return action

    def view_invoice(self):
        invoices = self.env['account.move'].search([('hospitalization_id', '=', self.id)])
        action = self.tgr_action_view_invoice(invoices)
        return action

    def tgr_get_consume_locations(self):
        if not self.company_id.tgr_hospitalization_usage_location_id:
            raise UserError(_('Por favor defina una ubicación donde se usarán los consumibles durante la cirugía en la compañía.'))
        if not self.company_id.tgr_hospitalization_stock_location_id:
            raise UserError(_('Por favor defina una ubicación de hospitalización de donde se tomarán los consumibles.'))

        dest_location_id  = self.company_id.tgr_hospitalization_usage_location_id.id
        source_location_id  = self.company_id.tgr_hospitalization_stock_location_id.id
        return source_location_id, dest_location_id

    def consume_hopitalization_material(self):
        for rec in self:
            source_location_id, dest_location_id = rec.tgr_get_consume_locations()
            for line in rec.consumable_line_ids.filtered(lambda s: not s.move_id):
                if line.product_id.is_kit_product:
                    move_ids = []
                    for kit_line in line.product_id.tgr_kit_line_ids:
                        if kit_line.product_id.tracking!='none':
                            raise UserError("En líneas de consumibles, no se permite producto Kit con componente que tenga seguimiento por lote/serie. Por favor elimine tal producto kit de las líneas de consumibles.")
                        move = self.consume_material(source_location_id, dest_location_id,
                            {'product': kit_line.product_id, 'qty': kit_line.product_qty * line.qty})
                        move.hospitalization_id = rec.id
                        move_ids.append(move.id)
                    #Set move_id on line also to avoid issue
                    line.move_id = move.id
                    line.move_ids = [(6,0,move_ids)]
                else:
                    move = self.consume_material(source_location_id, dest_location_id,
                        {'product': line.product_id, 'qty': line.qty, 'lot_id': line.lot_id and line.lot_id.id or False,})
                    move.hospitalization_id = rec.id
                    line.move_id = move.id

    def get_accommodation_invoice_data(self, invoice_id=False):
        product_data = []
        accommodation_history_ids = []
        for line in self.accommodation_history_ids:
            if line.invoiced_rest_time < line.rest_time:
                accommodation_history_ids += [line]

        if accommodation_history_ids:
            product_data.append({
                'name': _("Cargos de Alojamiento"),
            })
            for bed_history in accommodation_history_ids:
                product_data.append({
                    'product_id': bed_history.bed_id.product_id,
                    'quantity': bed_history.rest_time - bed_history.invoiced_rest_time,
                    'accommodation_history_id': bed_history,
                    
                })
        return product_data

    def get_consumable_invoice_data(self, invoice_id=False):
        product_data = []
        consumable_line_ids = self.consumable_line_ids.filtered(lambda s: not s.invoice_id)
        if consumable_line_ids:
            product_data.append({
                'name': _("Cargos de Productos Consumidos"),
            })
            for consumable in consumable_line_ids:
                product_data.append({
                    'product_id': consumable.product_id,
                    'quantity': consumable.qty,
                    'lot_id': consumable.lot_id and consumable.lot_id.id or False,
                    'product_uom_id': consumable.product_uom_id.id,
                })
                if invoice_id:
                    consumable.invoice_id = invoice_id.id

        return product_data

    def get_surgery_invoice_data(self, invoice_id=False):
        product_data = []

        surgery_ids = self.surgery_ids.filtered(lambda s: not s.invoice_id)
        if surgery_ids:
            surgery_data = surgery_ids.get_surgery_invoice_data()
            product_data += surgery_data

            if invoice_id:
                surgery_ids.invoice_id = invoice_id.id

        return product_data

    def tgr_hospitalization_physician_round_data(self, invoice_id=False):
        product_data = []
        ward_rounds_to_invoice = self.physician_ward_round_ids.filtered(lambda s: not s.invoice_id)
        if ward_rounds_to_invoice:
            ward_data = {}
            for ward_round in ward_rounds_to_invoice:
                if ward_round.physician_id.ward_round_service_id:
                    if ward_round.physician_id.ward_round_service_id in ward_data:
                        ward_data[ward_round.physician_id.ward_round_service_id] += 1
                    else:
                        ward_data[ward_round.physician_id.ward_round_service_id] = 1
            if ward_data:
                product_data.append({
                    'name': _("Cargos de Rondas de Sala del Médico"),
                })
            for product in ward_data:
                product_data.append({
                    'product_id': product,
                    'quantity': ward_data[product],
                })

            if invoice_id:
                ward_rounds_to_invoice.invoice_id = invoice_id.id
        return product_data

    def tgr_hospitalization_prescription_data(self, invoice_id=False):
        pres_data = []
        installed_tgr_hms_pharmacy = self.env['ir.module.module'].sudo().search([('name','=','tgr_hms_pharmacy'),('state','=','installed')])
        if installed_tgr_hms_pharmacy:
            prescription_ids = self.mapped('prescription_ids').filtered(lambda req: req.state=='prescription' and req.deliverd and not req.invoice_id)
            if prescription_ids:
                pres_data.append({'name': _("Cargos de Medicamentos")})
                for record in prescription_ids:
                    for line in record.prescription_line_ids:
                        pres_data.append({
                            'product_id': line.product_id,
                            'quantity': line.quantity,
                        })
                    if invoice_id:
                        record.invoice_id = invoice_id.id
        return pres_data

    #In lab module it get implemented.
    def tgr_hospitalization_lab_data(self, invoice_id=False):
        return []

    #In radio module it get implemented.
    def tgr_hospitalization_radiology_data(self, invoice_id=False):
        return []

    #In nursing module it get implemented.
    def tgr_hospitalization_nurse_round_data(self, invoice_id=False):
        return []

    #Keep Sub methods for projection flow. Because it just return list of data. Do not create real invoice.
    def tgr_hospitalization_invoicing(self, invoice_id=False):
        #consumable Invoicing
        consumable_data = self.get_consumable_invoice_data(invoice_id)

        #accomodation Invoicing
        accommodation_data = self.get_accommodation_invoice_data(invoice_id)

        #Physician Rounds Invoicing
        physician_round_data = self.tgr_hospitalization_physician_round_data(invoice_id)

        #Nurse Round Invoicing
        nurse_round_data = self.tgr_hospitalization_nurse_round_data(invoice_id)

        #Procedure Invoicing
        procedure_ids = self.procedure_ids.filtered(lambda proc: not proc.invoice_id)
        procedure_data = procedure_ids.tgr_common_invoice_procedure_data(invoice_id)

        #surgey Invoicing
        surgery_data = self.get_surgery_invoice_data(invoice_id)
        
        #Pharmacy Invoicing
        pres_data = self.tgr_hospitalization_prescription_data(invoice_id)

        #Lab Invoicing
        lab_data = self.tgr_hospitalization_lab_data(invoice_id)

        #Radiology Invoicing
        radiology_data = self.tgr_hospitalization_radiology_data(invoice_id)

        data = consumable_data + accommodation_data + physician_round_data + nurse_round_data + procedure_data + surgery_data + pres_data + lab_data + radiology_data
        #create Invoice lines only if invocie is passed
        if invoice_id:
            for line in data:
                pricelist_id = line.get('pricelist_id',False)
                inv_line = self.with_context(tgr_pricelist_id=pricelist_id).tgr_create_invoice_line(line, invoice_id)
                #ACS: As on accomodation history we need to set inv line as special case it is managed here.
                if line.get('accommodation_history_id'):
                    bed_history = line.get('accommodation_history_id')
                    bed_history.account_move_line_ids = [(4, inv_line.id)]

        return data

    def action_create_invoice(self):
        product_data = []
        inv_data = {
            'ref_physician_id': self.ref_physician_id and self.ref_physician_id.id or False,
            'physician_id': self.physician_id and self.physician_id.id or False,
            'hospital_invoice_type': 'hospitalization',
        }
        tgr_context = {'commission_partner_ids':self.physician_id.partner_id.id, 'tgr_pricelist_id': self.pricelist_id.id}
        invoice_id = self.with_context(tgr_context).tgr_create_invoice(partner=self.patient_id.partner_id, patient=self.patient_id, product_data=product_data, inv_data=inv_data)
        invoice_id.hospitalization_id = self.id

        self.tgr_hospitalization_invoicing(invoice_id)

        message = _('Factura Creada.')
        user = self.env.user.sudo()
        return {
            'effect': {
                'fadeout': 'slow',
                'message': message,
                'img_url': '/web/image/%s/%s/image_1024' % (user._name, user.id) if user.image_1024 else '/web/static/img/smile.svg',
                'type': 'rainbow_man',
            }
        }

    def button_indoor_medication(self):
        action = self.env["ir.actions.actions"]._for_xml_id("tgr_hms.act_open_hms_prescription_order_view")
        action['domain'] = [('hospitalization_id', '=', self.id)]
        action['views'] = [(self.env.ref('tgr_hms.view_hms_prescription_order_form').id, 'form')]
        action['context'] = {
            'default_patient_id': self.patient_id.id,
            'default_physician_id':self.physician_id.id,
            'default_hospitalization_id': self.id,
            'default_ward_id': self.ward_id.id,
            'default_bed_id': self.bed_id.id}
        return action

    def tgr_invoice_forecast(self):
        action = self.env["ir.actions.actions"]._for_xml_id("tgr_hms_hospitalization.action_tgr_hospitalization_forecast")
        action['domain'] = [('hospitalization_id', '=', self.id)]
        rec_id = self.env['tgr.hospitalization.forecast'].create({
            'hospitalization_id': self.id,
        })
        rec_id.onchange_hospitalization()
        action['res_id'] = rec_id.id
        return action

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
