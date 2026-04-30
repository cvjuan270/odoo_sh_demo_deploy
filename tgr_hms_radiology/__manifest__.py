# -*- coding: utf-8 -*-
{
    "name": "Gestion de Radiologia Hospitalaria",
    "summary": "Gestionar solicitudes de radiologia, pruebas de radiologia, facturacion e historial relacionado para el hospital",
    "version": "19.0.1.0.1",
    "category": "Medical",
    "author": "tagre.pe",
    "maintainer": "cvjuan270@gmail.com",
    "website": "https://tagre.pe",
    "license": "Other proprietary",
    "depends": ["tgr_hms", "tgr_radiology"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "report/report_tgr_radiology_prescription.xml",
        "report/radiology_report.xml",
        "report/report_medical_advice.xml",
        "views/hms_base_view.xml",
        "views/radiology_view.xml",
    ],
    "installable": True,
    "application": True,
}
