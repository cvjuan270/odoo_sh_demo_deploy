# -*- encoding: utf-8 -*-
from odoo import api, fields, models,_


class Bed(models.Model):
    _name = 'hospital.bed'
    _description = 'Bed'

    def _get_patient(self):
        for rec in self:
            patient_id = False
            ac_hists = rec.accommodation_history_ids.filtered(lambda r: r.start_date and not r.end_date )
            if ac_hists:
                patient_id = ac_hists[0].patient_id.id
            rec.patient_id = patient_id
    
    name = fields.Char(string='Nombre', required=True)
    product_id = fields.Many2one('product.product', ondelete='cascade',
        string='Producto Cama', required=True, domain=[('hospital_product_type', '=', 'bed')],
        context={'default_hospital_product_type': 'bed'})
    list_price = fields.Float(related='product_id.list_price', string="Precio", readonly=True)
    bed_type = fields.Selection([
        ('gatch', 'Cama Gatch'),
        ('electric', 'Eléctrica'),
        ('stretcher', 'Camilla'),
        ('low', 'Cama Baja'),
        ('low_air_loss', 'Pérdida de Aire Baja'),
        ('circo_electric', 'Circo Eléctrica'),
        ('clinitron', 'Clinitron')], string='Tipo', default='gatch', required=True)
    telephone = fields.Char(size=14, string='Teléfono')
    state = fields.Selection([
        ('free', 'Libre'),
        ('reserved', 'Reservado'),
        ('occupied', 'Ocupado'),
        ('blocked', 'Fuera de Uso'),], string='Estado', default="free")
    ward_id = fields.Many2one('hospital.ward', ondelete='restrict', string='Sala/Habitación')
    accommodation_history_ids = fields.One2many("patient.accommodation.history","bed_id",
        string="Historial de Alojamiento")
    notes = fields.Text(string='Notas')
    patient_id = fields.Many2one('hms.patient', compute="_get_patient", ondelete="restrict", string="Paciente")
    company_id = fields.Many2one('res.company', ondelete='restrict', 
        string='Hospital', default=lambda self: self.env.company)
    invoice_policy = fields.Selection([
        ('full', 'Días (Completo)'),
        ('hourly', 'Horas')], string='Política de Facturación', default='full', required=True)
    department_id = fields.Many2one('hr.department', related="ward_id.department_id", string='Departamento', store=True, readonly=True)

    @api.onchange('product_id')
    def onchnage_product_id(self):
        if not self.name:
            self.name = self.product_id.name

    def action_accommodation_history(self):
        action = self.env["ir.actions.actions"]._for_xml_id("tgr_hms_hospitalization.action_accommodation_history")
        action['domain'] = [('bed_id', '=', self.id)]
        action['context'] = {'default_bed_id': self.id}
        return action

    def copy(self, default=None):
        self.ensure_one()
        chosen_name = default.get('name') if default else ''
        new_name = chosen_name or _('%s (copia)') % self.name
        default = dict(default or {}, name=new_name)
        return super(Bed, self).copy(default)


class ACSHospitalWard(models.Model):
    _name = 'hospital.ward'
    _description = 'Ward/Room'

    def _rec_count(self):
        for rec in self:
            rec.bed_count = len(rec.bed_ids)
            rec.bed_available_count = len(rec.bed_ids.filtered(lambda r: r.state=='free' ))

    name = fields.Char(string='Nombre', required=True, 
        help='Número de Sala / Habitación')
    building_id = fields.Many2one('hospital.building', ondelete='restrict', 
        string='Edificio')
    floor = fields.Char(string='Número de Piso')
    gender = fields.Selection([
        ('men', 'Sala de Hombres'),
        ('women', 'Sala de Mujeres'),
        ('unisex', 'Unisex')], string='Género', required=True, default="unisex")
    state = fields.Selection([
        ('available', 'Disponible'),
        ('full', 'Lleno')], string='Estado', default="available")
    ward_room_type = fields.Selection([
        ('general', 'General'),
        ('semi_spaecial', 'Semi-Especial'),
        ('deluxe', 'De Lujo'),
        ('super_deluxe', 'Súper De Lujo'),
        ('suite', 'Suite'),
        ('sharing', 'Compartida'),
        ('icu', 'UCI'),
        ('dialysis', 'Diálisis'),
        ('recovery_room', 'Sala de Recuperación'), ], 
        string='Tipo de Sala/Habitación',required=True, default='general')
    company_id = fields.Many2one('res.company', ondelete='restrict', 
        string='Hospital', default=lambda self: self.env.company)
    department_id = fields.Many2one('hr.department', ondelete='restrict', 
        domain=[('patient_department', '=', True)], string='Departamento')

    #Facility
    private = fields.Boolean(string='Privada',
        help='Marque esta opción para habitación privada')
    television = fields.Boolean(string='Televisión')
    refrigerator = fields.Boolean(string='Refrigerador')
    internet = fields.Boolean(string='Acceso a Internet')
    bio_hazard = fields.Boolean(string='Riesgo Biológico', 
        help='Marque esta opción si hay riesgo biológico')
    private_bathroom = fields.Boolean(string='Baño Privado')
    telephone = fields.Boolean(string='Teléfono')
    microwave = fields.Boolean(string='Microondas')
    guest_sofa = fields.Boolean(string='Sofá-cama para invitados')
    air_conditioning = fields.Boolean(string='Aire Acondicionado')

    bed_ids = fields.One2many('hospital.bed', 'ward_id', 'Línea de Cama', copy=False)
    notes = fields.Text('Notas')
    bed_count = fields.Integer(compute='_rec_count', string='# Camas')
    bed_available_count = fields.Integer(compute='_rec_count', string='# Camas Disponibles')

    def action_bed(self):
        action = self.env["ir.actions.actions"]._for_xml_id("tgr_hms_hospitalization.action_bed")
        action['domain'] = [('ward_id', '=', self.id)]
        action['context'] = {'default_ward_id': self.id}
        return action

    def copy(self, default=None):
        self.ensure_one()
        chosen_name = default.get('name') if default else ''
        new_name = chosen_name or _('%s (copia)') % self.name
        default = dict(default or {}, name=new_name)
        return super(ACSHospitalWard, self).copy(default)


class ACSHospitalBuilding(models.Model):
    _name = 'hospital.building'
    _description = "Hospital Building"

    name = fields.Char(string='Nombre', required=True,
        help='Nombre del edificio dentro de la institución')
    code = fields.Char(string='Código')
    extra_info = fields.Text(string='Información Extra')
    company_id = fields.Many2one('res.company', ondelete='restrict', 
        string='Hospital', default=lambda self: self.env.company)


class ACSHospitalOT(models.Model):
    _name = 'tgr.hospital.ot'
    _description = "Operation Theater"

    name = fields.Char(string='Nombre', index=True, required=True, 
        help='Nombre de la Sala de Operaciones')
    physician_id = fields.Many2one('hms.physician', string='Médico', ondelete="restrict")
    building_id = fields.Many2one('hospital.building', string='Edificio', index=True, ondelete="restrict")
    telephone_number = fields.Integer(string='Número de Teléfono',
        help='Número de teléfono / Extensión')
    state = fields.Selection([
        ('free', 'Libre'),
        ('reserved', 'Reservado'),
        ('occupied', 'Ocupado'),
        ('na', 'No disponible')], string='Estado Actual', default="free")
    note = fields.Text(string='Información Extra')
    company_id = fields.Many2one('res.company', ondelete='restrict', 
        string='Hospital', default=lambda self: self.env.company) 

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
