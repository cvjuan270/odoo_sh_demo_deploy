# -*- coding: utf-8 -*-
{
    "name": "Consulta de DNI/RUC",
    "summary": "Consulta automatica de datos de DNI y RUC desde servicios externos",
    "description": """
Consulta de DNI/RUC
===================
Permite consultar datos de DNI y RUC desde servicios externos
para autocompletar informacion de pacientes.
    """,
    "author": "tagre.pe",
    "maintainer": "cvjuan270@gmail.com",
    "website": "https://tagre.pe",
    "license": "Other proprietary",
    "category": "Medical",
    "version": "19.0.1.0.0",
    "depends": ["base", "tgr_hms_base"],
    "data": [
        "views/res_config_settings_views.xml",
        "views/patient_view.xml",
    ],
}
