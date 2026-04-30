from odoo import fields, models


class LabaratoryArea(models.Model):
    _name = "laboratory.area"
    _description = "Área de Laboratorio"

    name = fields.Char(
        string="Nombre",
        required=True,
        translate=True,
        help="Nombre del área de laboratorio (ej. Hematología, Bioquímica)",
    )
    code = fields.Char(
        string="Código", help="Código único para identificar el área", required=True
    )
    sequence = fields.Integer(
        string="Sequence", default=10, help="Secuencia para ordenar las áreas"
    )
    description = fields.Text(
        string="Description",
        translate=True,
        help="Descripción detallada del área de laboratorio",
    )
    color = fields.Integer(
        string="Color", help="Color para identificar visualmente esta área"
    )
