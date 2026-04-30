# -*- coding: utf-8 -*-

from datetime import date, timedelta

from odoo import models
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class PatientTestCommon(TransactionCase):
    # -----------------------------------------------------
    # SETUP
    # -----------------------------------------------------
    @classmethod
    def setUpClass(cls):
        super(PatientTestCommon, cls).setUpClass()
        # Modelos principales
        cls.Partner = cls.env["res.partner"]
        cls.Patient = cls.env["hms.patient"]

        # Configuración de entorno
        cls._setup_company()
        cls._setup_sequences()

        # Datos Maestros
        cls._setup_master_data()

        # Datos de prueba base
        cls.demo_partner = cls._create_demo_partner()
        cls.demo_patient = cls._create_demo_patient()

    @classmethod
    def _setup_company(cls):
        cls.company = cls.env.company
        cls.country = cls.env.ref("base.pe").sudo()
        cls.company.country_id = cls.country

    @classmethod
    def _setup_sequences(cls):
        cls.sequence_patient = cls.env["ir.sequence"].create(
            {
                "name": "Patient Sequence",
                "code": "PATIENT",
                "prefix": "PAC-",
                "padding": 5,
                "number_next": 1,
            }
        )

    @classmethod
    def _setup_master_data(cls):
        cls.religion = cls.env["tgr.religion"].create(
            {"name": "Cristianismo", "code": "CR", "notes": "Cristianismo"}
        )
        cls.tag_vip = cls.env["hms.patient.tag"].create({"name": "VIP", "color": 1})

    @classmethod
    def _create_demo_partner(cls, **kwargs):
        partner_vals = {
            "name": "Demo Partner",
            "birthday": date.today() - timedelta(days=365 * 30),
            "gender": "male",
            "email": "demo@example.com",
            "mobile": "999989898",
        }
        partner_vals.update(kwargs)
        return cls.Partner.create(partner_vals)

    @classmethod
    def _create_demo_patient(cls, **kwargs):
        if "partner_id" not in kwargs:
            partner = cls._create_demo_partner()
            kwargs["partner_id"] = partner.id
        patient_vals = {
            "name": "Demo Patient",
            "marital_status": "single",
            "tgr_religion_id": cls.religion.id,
            "tgr_tag_ids": [(6, 0, [cls.tag_vip.id])],
        }

        print("patient_vals", patient_vals)
        return cls.Patient.create([patient_vals])

    # -------------------------------------------------------------------------
    # UTILITY METHODS (REUSABLES)
    # -------------------------------------------------------------------------
    def assertPatientVals(self, patient, expected_vals):
        """
        Método utilitario para verificar valores de un paciente
        Args:
            patient (hms.patient): Registro de paciente a verificar
            expected_vals (dict): Diccionario con valores esperados
        """
        for field, expected_value in expected_vals.items():
            with self.subTest(field=field):
                actual_value = patient[field]
                if isinstance(actual_value, models.BaseModel):
                    actual_value = actual_value.id
                self.assertEqual(
                    actual_value,
                    expected_value,
                    f"El campo {field} no coincide. Esperado: {expected_value}, Obtenido: {actual_value}",
                )

    def assertPartnerVals(self, partner, expected_vals):
        """
        Método utilitario para verificar valores de un partner
        Similar a assertPatientVals pero para res.partner
        """
        self.assertPatientVals(partner, expected_vals)  # Reutilizamos la misma lógica
