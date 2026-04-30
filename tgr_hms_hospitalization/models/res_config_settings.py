# -*- encoding: utf-8 -*-
from odoo import api, fields, models,_


class ResCompany(models.Model):
    _inherit = "res.company"

    tgr_hospitalization_usage_location_id = fields.Many2one('stock.location', 
        string='Ubicación de uso de hospitalización para productos consumidos')
    tgr_hospitalization_stock_location_id = fields.Many2one('stock.location', 
        string='Ubicación de stock de hospitalización para productos consumidos')
    allow_bed_reservation = fields.Boolean('Permitir Reserva de Cama')


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    tgr_hospitalization_usage_location_id = fields.Many2one('stock.location', 
        related='company_id.tgr_hospitalization_usage_location_id',
        domain=[('usage','=','customer')],
        string='Ubicación de uso de hospitalización para productos consumidos', 
        ondelete='cascade', help='Ubicación de Uso para Productos Consumidos', readonly=False)
    tgr_hospitalization_stock_location_id = fields.Many2one('stock.location', 
        related='company_id.tgr_hospitalization_stock_location_id',
        domain=[('usage','=','internal')],
        string='Ubicación de stock de hospitalización para productos consumidos', 
        ondelete='cascade', help='Ubicación de Stock para Productos Consumidos', readonly=False)
    allow_bed_reservation = fields.Boolean('Permitir Reserva de Cama',
        related='company_id.allow_bed_reservation',
        help='Permitir Reserva de Cama', readonly=False)
