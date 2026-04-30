# coding=utf-8

from odoo import api, fields, models, _


class AdmissionCheckListTemplate(models.Model):
    _name="inpatient.checklist.template"
    _description = "Inpatient Checklist Template"

    name = fields.Char(string="Nombre", required=True)
    remark = fields.Char(string="Notas")


class AdmissionCheckList(models.Model):
    _name="inpatient.checklist"
    _description = "Inpatient Checklist"

    name = fields.Char(string="Nombre", required=True)
    is_done = fields.Boolean(string="Y/N")
    remark = fields.Char(string="Notas")
    hospitalization_id = fields.Many2one("tgr.hospitalization", ondelete="cascade", string="Hospitalización")


class PreWardCheckListTemplate(models.Model):
    _name="pre.ward.check.list.template"
    _description = "Pre Ward Checklist Template"

    name = fields.Char(string="Nombre", required=True)
    remark = fields.Char(string="Notas")


class PreWardCheckList(models.Model):
    _name="pre.ward.check.list"
    _description = "Pre Ward Checklist"

    name = fields.Char(string="Nombre", required=True)
    is_done = fields.Boolean(string="Hecho")
    remark = fields.Char(string="Notas")
    hospitalization_id = fields.Many2one("tgr.hospitalization", ondelete="cascade", string="Hospitalización")


class PatientAccommodationHistory(models.Model):
    _name = "patient.accommodation.history"
    _rec_name = "patient_id"
    _description = "Patient Accommodation History"

    def _rest_time(self):
        for registration in self:
            rest_time = 0
            end_date = registration.end_date or fields.Datetime.now()
            if end_date and registration.start_date:
                diff = end_date - registration.start_date
                if registration.bed_id.invoice_policy=='full':
                    rest_time = diff.days if diff.days > 0 else 1
                else:
                    total_seconds = int(diff.total_seconds())
                    rest_time = (total_seconds/3600) if total_seconds else 0
            registration.rest_time = rest_time

    @api.depends('account_move_line_ids')
    def tgr_get_move_lines_data(self):
        for rec in self:
            rec.invoiced_rest_time = sum(rec.account_move_line_ids.mapped('quantity'))

    hospitalization_id = fields.Many2one('tgr.hospitalization', ondelete="cascade", string='Hospitalización')
    patient_id = fields.Many2one('hms.patient', ondelete="restrict", string='Paciente', required=True)
    ward_id = fields.Many2one('hospital.ward', ondelete="restrict", string='Sala/Habitación')
    bed_id = fields.Many2one('hospital.bed', ondelete="restrict", string='Cama No.')
    start_date = fields.Datetime(string='Fecha de Inicio')
    end_date = fields.Datetime(string='Fecha Final')
    rest_time = fields.Float(compute=_rest_time, string='Tiempo de Descanso')
    company_id = fields.Many2one('res.company', ondelete='restrict', 
        string='Hospital', related='hospitalization_id.company_id') 
    invoice_policy = fields.Selection(related="bed_id.invoice_policy", string='Política de Facturación', readonly=True)
    account_move_line_ids = fields.Many2many('account.move.line', 'tgr_accomodation_account_move_line_rel', 'move_id', 'accommodation_id', string='Líneas de Factura')
    invoiced_rest_time = fields.Float(compute="tgr_get_move_lines_data", string="Tiempo de Descanso Facturado")


class WardRounds(models.Model):
    _name = "ward.rounds"
    _description = "Ward Rounds"

    instruction = fields.Char(string='Instrucción')
    remarks = fields.Char(string='Notas')
    hospitalization_id = fields.Many2one('tgr.hospitalization', ondelete="restrict",string='Hospitalización')
    date = fields.Datetime(string='Fecha', default=fields.Datetime.now)
    physician_id = fields.Many2one('hms.physician', string='Médico', ondelete="restrict")
    invoice_id = fields.Many2one('account.move', string='Factura', copy=False)
    prescription_ids = fields.One2many('prescription.order', 'ward_round_id', 'Recetas')

    def tgr_create_ip_medicine_request(self):
        action = self.env["ir.actions.actions"]._for_xml_id("tgr_hms.act_open_hms_prescription_order_view")
        action['domain'] = [('hospitalization_id', '=', self.hospitalization_id.id)]
        action['views'] = [(self.env.ref('tgr_hms.view_hms_prescription_order_form').id, 'form')]
        action['context'] = {
            'default_patient_id': self.hospitalization_id.patient_id.id,
            'default_physician_id':self.physician_id.id,
            'default_hospitalization_id': self.hospitalization_id.id,
            'default_ward_id': self.hospitalization_id.ward_id.id,
            'default_ward_round_id': self.id,
            'default_diseases_ids': [(6,0,self.hospitalization_id.diseases_ids.ids)],
            'default_bed_id': self.hospitalization_id.bed_id.id}
        return action

    def action_prescriptions(self):
        action = self.env["ir.actions.actions"]._for_xml_id("tgr_hms.act_open_hms_prescription_order_view")
        action['domain'] = [('hospitalization_id', '=', self.id)]
        action['context'] = {
            'default_patient_id': self.hospitalization_id.patient_id.id,
            'default_physician_id':self.physician_id.id,
            'default_hospitalization_id': self.hospitalization_id.id,
            'default_ward_id': self.hospitalization_id.ward_id.id,
            'default_ward_round_id': self.id,
            'default_bed_id': self.hospitalization_id.bed_id.id,
            'default_diseases_ids': [(6,0,self.hospitalization_id.diseases_ids.ids)],}
        return action


class ACSCarePlanTemplate(models.Model):
    _name = "hms.care.plan.template"
    _description = "Care Plan Template"

    name= fields.Char(string='Nombre del Plan de Cuidados')
    diseases_id = fields.Many2one ('hms.diseases', ondelete='restrict', string='Enfermedad')
    nursing_plan = fields.Text (string='Plan de Enfermería')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
