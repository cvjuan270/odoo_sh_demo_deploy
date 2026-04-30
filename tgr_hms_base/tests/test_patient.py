from .patient_common import PatientTestCommon


class TestHmsPatient(PatientTestCommon):

    def test_patient_creation(self):
        """Prueba creación básica de paciente"""
        expected_vals = {
            "name": "Demo Patient",
            "marital_status": "single",
        }
        self.assertPatientVals(self.demo_patient, expected_vals)

    def test_custom_creation(self):
        """Prueba creación con valores personalizados"""
        custom_patient = self._create_demo_patient(
            name="Demo Patient",
            tgr_tag_ids=None,  # Sobreescribe el valor por defecto
        )
        self.assertEqual(custom_patient.name, "Demo Patient")
        self.assertEqual(len(custom_patient.tgr_tag_ids), 1)
