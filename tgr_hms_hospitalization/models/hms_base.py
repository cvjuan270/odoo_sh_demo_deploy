# -*- encoding: utf-8 -*-
from odoo import api, fields, models,_


class AccountMove(models.Model):
    _inherit = "account.move"

    hospitalization_id = fields.Many2one('tgr.hospitalization', ondelete="restrict", string='Hospitalización',
        help="Ingrese el código de hospitalización del paciente")
    hospital_invoice_type = fields.Selection(selection_add=[('hospitalization', 'Hospitalización')])


class Prescription(models.Model):
    _inherit = 'prescription.order'

    hospitalization_id = fields.Many2one('tgr.hospitalization', ondelete="restrict", string='Hospitalización',
        help="Ingrese el código de hospitalización del paciente")
    ward_id = fields.Many2one('hospital.ward', string='Sala/Habitación No.', ondelete="restrict")
    bed_id = fields.Many2one("hospital.bed", string="Cama No.", ondelete="restrict")
    ward_round_id = fields.Many2one("ward.rounds", string="Ronda de Sala", ondelete="restrict")
    print_in_discharge = fields.Boolean('Imprimir en Alta')
 

class ACSAppointment(models.Model):
    _inherit = 'hms.appointment'

    hospitalization_ids = fields.One2many('tgr.hospitalization', 'appointment_id',string='Hospitalizaciones')

    def action_hospitalization(self):
        action = self.env["ir.actions.actions"]._for_xml_id("tgr_hms_hospitalization.tgr_action_form_inpatient")
        action['domain'] = [('appointment_id', '=', self.id)]
        action['context'] = {'default_patient_id': self.patient_id.id, 'default_appointment_id': self.id, 'default_physician_id': self.physician_id.id}
        return action


class ACSPatient(models.Model):
    _inherit = "hms.patient"
    
    def _get_hospitalization_count(self):
        for rec in self:
            rec.hospitalization_count = len(rec.hospitalization_ids)

    hospitalization_ids = fields.One2many('tgr.hospitalization', 'patient_id',string='Hospitalizaciones')
    hospitalization_count = fields.Integer(compute='_get_hospitalization_count', string='# Hospitalizaciones')
    death_register_id = fields.Many2one('patient.death.register', string='Registro de Defunción')

    hospitalized = fields.Boolean()
    discharged = fields.Boolean()

    @api.onchange('death_register_id')   
    def onchange_death_register(self):
        if self.death_register_id:
            self.date_of_death = self.death_register_id.date_of_death

    def action_hospitalization(self):
        action = self.env["ir.actions.actions"]._for_xml_id("tgr_hms_hospitalization.tgr_action_form_inpatient")
        action['domain'] = [('patient_id', '=', self.id)]
        action['context'] = {'default_patient_id': self.id}
        return action


class StockMove(models.Model):
    _inherit = "stock.move"
    
    hospitalization_id = fields.Many2one('tgr.hospitalization', 'Hospitalización')


class ACSConsumableLine(models.Model):
    _inherit = "hms.consumable.line"

    hospitalization_id = fields.Many2one('tgr.hospitalization', ondelete="restrict", string='Hospitalización')


class ACSSurgery(models.Model):
    _inherit = "hms.surgery"

    hospital_ot_id = fields.Many2one('tgr.hospital.ot', ondelete="restrict", 
        string='Quirófano')
    hospitalization_id = fields.Many2one('tgr.hospitalization', ondelete="restrict", string='Hospitalización')


class ACSMedicamentLine(models.Model):
    _inherit = "medicament.line"
    
    hospitalization_id = fields.Many2one('tgr.hospitalization', ondelete="restrict", string='Hospitalización')


class product_template(models.Model):
    _inherit = "product.template"

    hospital_product_type = fields.Selection(selection_add=[('bed', 'Cama')])


class AcsPatientEvaluation(models.Model):
    _inherit = 'tgr.patient.evaluation'

    hospitalization_id = fields.Many2one('tgr.hospitalization', string='Hospitalización')


class PatientProcedure(models.Model):
    _inherit="tgr.patient.procedure"

    hospitalization_id = fields.Many2one('tgr.hospitalization', ondelete="restrict", string='Hospitalización')


class Physician(models.Model):
    _inherit = "hms.physician"

    def _hos_rec_count(self):
        Hospitalization = self.env['tgr.hospitalization']
        for record in self.with_context(active_test=False):
            record.hospitalization_count = Hospitalization.search_count([('physician_id', '=', record.id)])

    hospitalization_count = fields.Integer(compute='_hos_rec_count', string='# Hospitalización')
    ward_round_service_id = fields.Many2one('product.product', domain=[('type','=','service')],
        string='Servicio de Ronda de Sala',  ondelete='cascade', help='Producto de Ronda de Sala')

    def action_hospitalization(self):
        action = self.env["ir.actions.actions"]._for_xml_id("tgr_hms_hospitalization.tgr_action_form_inpatient")
        action['domain'] = [('physician_id','=',self.id)]
        action['context'] = {'default_physician_id': self.id}
        return action
