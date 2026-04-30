# -*- coding: utf-8 -*-
# Part of AlmightyCS See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.service import common
import requests
import json


class ResCompany(models.Model):
    _inherit = "res.company"

    birthday_mail_template_id = fields.Many2one('mail.template', 'Birthday Wishes Template',
        help="This will set the default mail template for birthday wishes.")
    unique_gov_code = fields.Boolean('Unique Government Identity for Patient', help='Set this True if the Givernment Identity in patients should be unique.')

    #Call this method directly in case of dependcy issue like tgr_certification (call in tgr_hms_certification)
    def tgr_create_sequence(self, name, code, prefix, padding=3):
        self.env['ir.sequence'].sudo().create({
            'name': self.name + " : " + name,
            'code': code,
            'padding': padding,
            'number_next': 1,
            'number_increment': 1,
            'prefix': prefix,
            'company_id': self.id,
            'tgr_auto_create': False,
        })

    def tgr_auto_create_sequences(self):
        sequences = self.env['ir.sequence'].search([('tgr_auto_create','=',True)])
        for sequence in sequences:
            self.tgr_create_sequence(name=sequence.name, code=sequence.code, prefix=sequence.prefix, padding=sequence.padding)

    #Auto create marked sequences in other HMS modules.
    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        for record in res:
            record.tgr_auto_create_sequences()
        return res

    @api.model
    def tgr_get_blocking_data(self):
        ir_config_model = self.env["ir.config_parameter"]
        access_is_blocked = ir_config_model.sudo().get_param("tgr.access.expired","False")
        message = ''
        if access_is_blocked!='False':
            message = ir_config_model.sudo().get_param("tgr.access.message")
            if not message:
                message = "Your Access Are blocked please contact at info@almightycs.com"
        return {"name": message}

    @api.model
    def tgr_send_access_data(self, data):
        ir_config_model = self.env["ir.config_parameter"].sudo()
        try:
            domain = "https://www.almightyhms.com" + '/acs/module/checksubscription'
            reply = requests.post(domain, json.dumps(data), headers={'accept': 'application/json', 'Content-Type': 'application/json'})
            if reply.status_code==200:
                reply = json.loads(reply.text)
                subscription_status = reply['result'].get('subscription_status')
                if subscription_status!='active':
                    ir_config_model.set_param("tgr.access.expired", "True")
                if subscription_status=='active':
                    ir_config_model.set_param("tgr.access.expired", "False")
        except:
            pass

    @api.model
    def tgr_update_access_data(self):
        user = self.env.user
        company = user.sudo().company_id
        ir_config_model = self.env["ir.config_parameter"].sudo()
        secret = ir_config_model.get_param("database.secret")
        url = ir_config_model.get_param("web.base.url")
        Module = self.env['ir.module.module'].sudo()
        data = {
            "installed_modules": Module.search([('state','=','installed')]).mapped('name'), 
            "db_secret": secret, 
            "company_name": company.name,
            "email": company.email,
            "mobile": company.mobile,
            "url": url,
            'users': self.env['res.users'].sudo().search_count([('share','=',False)]),
            'physicians': self.env['hms.physician'].sudo().search_count([]),
            'patients': self.env['hms.patient'].sudo().search_count([]),
        }

        try:
            version_info = common.exp_version()
            data['version'] = version_info.get('server_serie')    
        except:
            pass

        try:
            if Module.search([('name','=','tgr_hms'),('state','=','installed')]):
                data.update({
                    'appointments': self.env['hms.appointment'].sudo().search_count([]),
                    'evaluations': self.env['tgr.patient.evaluation'].sudo().search_count([]),
                    'prescriptions': self.env['prescription.order'].sudo().search_count([]),
                    'procedures': self.env['tgr.patient.procedure'].sudo().search_count([]),
                    'treatments': self.env['hms.treatment'].sudo().search_count([]),
                })
        except:
            pass

        try:
            if Module.search([('name','=','tgr_hms_insurance'),('state','=','installed')]):
                data['insurance_policies'] = self.env['hms.patient.insurance'].sudo().search_count([])
                data['claims'] = self.env['hms.insurance.claim'].sudo().search_count([])
            if Module.search([('name','=','tgr_hms_certification'),('state','=','installed')]):
                data['certificates'] = self.env['certificate.management'].sudo().search_count([])
            if Module.search([('name','=','tgr_hms_hospitalization'),('state','=','installed')]):
                data['hospitalizations'] = self.env['tgr.hospitalization'].sudo().search_count([])
            if Module.search([('name','=','tgr_consent_form'),('state','=','installed')]):
                data['consentforms'] = self.env['tgr.consent.form'].sudo().search_count([])
            if Module.search([('name','=','tgr_hms_laboratory'),('state','=','installed')]):
                data['laboratory_requests'] = self.env['tgr.laboratory.request'].sudo().search_count([])
                data['laboratory_results'] = self.env['patient.laboratory.test'].sudo().search_count([])
            if Module.search([('name','=','tgr_hms_radiology'),('state','=','installed')]):
                data['radiology_requests'] = self.env['tgr.radiology.request'].sudo().search_count([])
                data['radiology_results'] = self.env['patient.radiology.test'].sudo().search_count([])
            if Module.search([('name','=','tgr_hms_commission'),('state','=','installed')]):
                data['commissions'] = self.env['tgr.commission'].sudo().search_count([])
            if Module.search([('name','=','tgr_hms_vaccination'),('state','=','installed')]):
                data['vaccinations'] = self.env['tgr.vaccination'].sudo().search_count([])
            if Module.search([('name','=','tgr_hms_emergency'),('state','=','installed')]):
                data['emergencies'] = self.env['tgr.hms.emergency'].sudo().search_count([])
            if Module.search([('name','=','tgr_hms_surgery'),('state','=','installed')]):
                data['surgeries'] = self.env['hms.surgery'].sudo().search_count([])
            if Module.search([('name','=','tgr_sms'),('state','=','installed')]):
                data['sms'] = self.env['tgr.sms'].sudo().search_count([])
            if Module.search([('name','=','tgr_whatsapp'),('state','=','installed')]):
                data['whatsapp'] = self.env['tgr.whatsapp.message'].sudo().search_count([])
        except:
            pass
        self.tgr_send_access_data(data)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    birthday_mail_template_id = fields.Many2one('mail.template', 
        related='company_id.birthday_mail_template_id',
        string='Birthday Wishes Template',
        help="This will set the default mail template for birthday wishes.", readonly=False)
    unique_gov_code = fields.Boolean('Unique Government Identity for Patient',
         related='company_id.unique_gov_code', readonly=False,
         help='Set this True if the Givernment Identity in patients should be unique.')