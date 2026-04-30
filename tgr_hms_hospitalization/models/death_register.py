# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class DeathRegister(models.Model):
    _name = "patient.death.register"
    _description = "Patient Death Register"

    name = fields.Char('Nombre', readonly=True, copy=False)
    date_of_death = fields.Date(string='Fecha de fallecimiento', required=True)
    hospitalizaion_id = fields.Many2one('tgr.hospitalization', string='Hospitalización')
    patient_id = fields.Many2one('hms.patient', string="Paciente", required=True)
    patient_age = fields.Char(related="patient_id.age", store=True, string="Edad")
    patient_gender = fields.Selection(related="patient_id.gender", store=True, string='Género')
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('done', 'Realizado')], string='Estado', required=True, readonly=True, copy=False, default='draft')
    physician_id = fields.Many2one('hms.physician', ondelete='restrict', string='Médico', index=True)
    reason = fields.Text (string='Causa de muerte', required=True)
    extra_info = fields.Text (string='Notas')
    company_id = fields.Many2one('res.company', ondelete='restrict', 
        string='Hospital',default=lambda self: self.env.company) 

    @api.model_create_multi
    def create(self, vals_list):
        for values in vals_list:
            values['name'] = self.env['ir.sequence'].next_by_code('patient.death.register') or 'Death'
        return super().create(vals_list)

    def unlink(self):
        for data in self:
            if data.state in ['done']:
                raise UserError(('No puede eliminar un registro en estado realizado'))
        return super(DeathRegister, self).unlink()

    def action_done(self):
        self.state = 'done'
        self.patient_id.death_register_id = self.id
        self.patient_id.date_of_death = self.date_of_death
        if self.hospitalizaion_id:
            self.hospitalizaion_id.death_register_id = self.id
        self.patient_id.active = False

    def action_draft(self):
        self.state = 'draft'

    @api.onchange('hospitalizaion_id')   
    def onchange_hospitalizaion(self):
        if self.hospitalizaion_id:
            self.patient_id = self.hospitalizaion_id.patient_id.id

    @api.onchange('patient_id')   
    def onchange_patient_id(self):
        if self.patient_id:
            self.patient_age = self.patient_id.age

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:   
