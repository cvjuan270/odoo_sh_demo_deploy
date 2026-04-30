# -*- encoding: utf-8 -*-
from odoo import api, fields, models, _


class ResCompany(models.Model):
    _inherit = "res.company"

    tgr_surgery_usage_location_id = fields.Many2one(
        "stock.location", string="Ubicación de uso de cirugía para productos consumidos"
    )
    tgr_surgery_stock_location_id = fields.Many2one(
        "stock.location", string="Ubicación de stock de cirugía para productos consumidos"
    )


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    tgr_surgery_usage_location_id = fields.Many2one(
        "stock.location",
        related="company_id.tgr_surgery_usage_location_id",
        domain=[("usage", "=", "customer")],
        string="Ubicación de uso de cirugía para productos consumidos",
        ondelete="cascade",
        help="Ubicación de uso para productos consumidos en cirugía",
        readonly=False,
    )
    tgr_surgery_stock_location_id = fields.Many2one(
        "stock.location",
        related="company_id.tgr_surgery_stock_location_id",
        domain=[("usage", "=", "internal")],
        string="Ubicación de stock de cirugía para productos consumidos",
        ondelete="cascade",
        help="Ubicación de stock para productos consumidos en cirugía",
        readonly=False,
    )

