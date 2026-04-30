# -*- coding: utf-8 -*-
{
    "name": "Laboratorio Hospitalario",
    "summary": "Gestion de laboratorio integrada con el sistema hospitalario HMS",
    "description": "",
    "version": "19.0.1.0.1",
    "category": "Medical",
    "author": "tagre.pe",
    "maintainer": "cvjuan270@gmail.com",
    "website": "https://tagre.pe",
    "license": "Other proprietary",
    "depends": ["tgr_hms", "tgr_laboratory"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "report/report_tgr_lab_prescription.xml",
        "report/lab_report.xml",
        "report/report_medical_advice.xml",
        "views/hms_base_view.xml",
        "views/laboratory_view.xml",
    ],
    "installable": True,
    "application": True,
}
