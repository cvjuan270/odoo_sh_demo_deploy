# -*- coding: utf-8 -*-
{
    "name": "Integracion WhatsApp",
    "summary": "Integracion de mensajeria WhatsApp con plantillas, mensajes y anuncios",
    "category": "Medical",
    "version": "19.0.1.0.1",
    "author": "tagre.pe",
    "maintainer": "cvjuan270@gmail.com",
    "website": "https://tagre.pe",
    "license": "Other proprietary",
    "depends": ["hr"],
    "description": "",
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/data.xml",
        "wizard/create_whatsapp_message_view.xml",
        "wizard/whatsapp_messages_view.xml",
        "views/message_template_view.xml",
        "views/message_view.xml",
        "views/announcement_view.xml",
        "views/partner_view.xml",
        "views/company_view.xml",
        "views/menu_item.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "tgr_whatsapp/static/src/scss/custom_backend.scss",
        ]
    },
    "images": [
        "static/description/tgr_odoo_whatsapp_almightycs_cover.jpg",
    ],
    "installable": True,
    "application": False,
    "sequence": 2,
}
