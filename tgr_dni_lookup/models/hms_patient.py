import logging
from datetime import datetime

import requests
from odoo import models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class TGRPatient(models.Model):
    _inherit = "hms.patient"

    def tgr_dni_lookup(self):
        self.ensure_one()
        l10n_pe_vat_code = (
            self.l10n_latam_identification_type_id.l10n_pe_vat_code
            if self.l10n_latam_identification_type_id
            else None
        )
        if l10n_pe_vat_code != "1":
            raise UserError("Solo se puede consultar DNI")
        doc_number = self.vat or ""
        if len(doc_number) != 8:
            raise UserError("Numero de caracteres del DNI es incorrecto")
        token = self.env.company.sudo().tgr_dni_lookup_token
        if not token:
            raise UserError("No se ha configurado el token de consulta de DNI")
        url = f"https://api.factiliza.com/v1/dni/info/{doc_number}"
        headers = {"Authorization": f"Bearer {token}"}
        try:
            response = requests.get(url, headers=headers, timeout=10)
        except requests.exceptions.RequestException as e:
            _logger.error("Error de conexión en el servicio de lookup: %s", e)
            raise UserError("Error de conexión en el servicio de lookup: %s" % e)
        if response.status_code != 200:
            raise UserError("Error en el servicio de lookup (código %s)" % response.status_code)
        payload = response.json()
        data = payload.get("data")
        if not data:
            raise UserError("No se encontraron datos para el DNI %s" % doc_number)
        nombres = data.get("nombres") or ""
        apellido_paterno = data.get("apellido_paterno") or ""
        apellido_materno = data.get("apellido_materno") or ""
        name = " ".join(part for part in [nombres, apellido_paterno, apellido_materno] if part)
        if name:
            self.name = name
        fecha_nacimiento = data.get("fecha_nacimiento")
        if fecha_nacimiento:
            try:
                self.birthday = datetime.strptime(fecha_nacimiento, "%d/%m/%Y").date()
            except (ValueError, TypeError):
                _logger.warning("Fecha de nacimiento con formato inesperado: %s", fecha_nacimiento)
        if data.get("sexo"):
            self.gender = "male" if data.get("sexo") == "M" else "female"
