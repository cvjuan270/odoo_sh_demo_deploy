from odoo import api, fields, models


class LabTestProfile(models.Model):
    _name = "tgr.laboratory.test.profile"
    _description = "Perfil de examenes de laboratorio"

    name = fields.Char("Nombre", required=True)
    code = fields.Char("Código", required=True)
    line_ids = fields.One2many(
        "tgr.laboratory.test.profile.line", "profile_id", string="Exámenes"
    )


class LabTestProfileLine(models.Model):
    _name = "tgr.laboratory.test.profile.line"
    _description = "Exámenes de laboratorio en el perfil"

    profile_id = fields.Many2one(
        "tgr.laboratory.test.profile", string="Perfil", ondelete="restrict"
    )
    test_id = fields.Many2one(
        "tgr.lab.test", string="Examen", ondelete="cascade", required=True
    )
    instruction = fields.Char(string="Instrucciones especiales")
    sale_price = fields.Float(string="Precio de venta")

    @api.onchange("test_id")
    def onchange_test(self):
        if self.test_id:
            self.sale_price = self.test_id.product_id.lst_price
