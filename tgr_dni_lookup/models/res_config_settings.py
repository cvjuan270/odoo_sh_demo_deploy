from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    tgr_dni_lookup_token = fields.Char(
        related="company_id.tgr_dni_lookup_token", string="Token - API Factiliza", readonly=False
    )
