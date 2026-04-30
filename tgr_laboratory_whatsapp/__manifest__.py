# -*- coding: utf-8 -*-
{
    "name": "Notificaciones WhatsApp de Laboratorio",
    "summary": "Envio de notificaciones de resultados de laboratorio por WhatsApp",
    "version": "19.0.1.0.1",
    "category": "Medical",
    "author": "tagre.pe",
    "maintainer": "cvjuan270@gmail.com",
    "website": "https://tagre.pe",
    "license": "Other proprietary",
    "depends": ["tgr_whatsapp", "tgr_laboratory"],
    "description": "",
    "data": [
        "data/data.xml",
        "views/company_view.xml",
        "views/tgr_hms_view.xml",
    ],
    "images": [
        "static/description/tgr_hms_whatsapp_almightycs_cover.jpg",
    ],
    "installable": True,
    "application": False,
    "sequence": 2,
}
