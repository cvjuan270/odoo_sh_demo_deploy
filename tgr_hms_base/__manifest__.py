# -*- coding: utf-8 -*-
{
    "name": "Base - Sistema de Gestion Hospitalaria (HMS)",
    "summary": "Modulo base del sistema de gestion hospitalaria con pacientes, medicos, productos medicos y configuracion general",
    "description": "",
    "version": "19.0.1.0.1",
    "category": "Medical",
    "author": "tagre.pe",
    "maintainer": "cvjuan270@gmail.com",
    "website": "https://tagre.pe",
    "license": "Other proprietary",
    "depends": ["account", "stock", "hr", "product_expiry", "l10n_latam_base"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "report/paper_format.xml",
        "report/report_layout.xml",
        "report/report_invoice.xml",
        "report/report_templates.xml",
        "data/sequence.xml",
        "data/mail_template.xml",
        "data/company_data.xml",
        "views/hms_base_views.xml",
        # Reports
        "views/report_templates.xml",
        # End Reports
        "views/patient_view.xml",
        "views/physician_view.xml",
        "views/product_view.xml",
        "views/drug_view.xml",
        "views/account_view.xml",
        "views/res_config_settings.xml",
        "views/stock_view.xml",
        "views/res_country_view.xml",
        "views/menu_item.xml",
    ],
    "demo": [
        # "demo/company_demo.xml",
    ],
    "assets": {
        # "web.assets_backend": ["tgr_hms_base/static/src/scss/report.scss"],
        "web.assets_common": [
            # "tgr_hms_base/static/src/js/tgr.js",
            # "tgr_hms_base/static/src/scss/tgr.scss",
        ],
        "web.report_assets_common": [
            # "tgr_hms_base/static/src/css/report.css",
        ],
    },
    "images": [
        # "static/description/hms_almightycs_cover.jpg",
    ],
    "installable": True,
    "application": True,
    "sequence": 1,
}
