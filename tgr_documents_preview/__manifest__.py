# -*- coding: utf-8 -*-
{
    "name": "Vista Previa de Documentos",
    "summary": "Vista previa de documentos del hospital y pacientes.",
    "description": """
Vista Previa de Documentos
==========================
Permite previsualizar documentos del hospital y pacientes
directamente desde el sistema.
    """,
    "version": "19.0.1.0.1",
    "category": "Medical",
    "author": "tagre.pe",
    "maintainer": "cvjuan270@gmail.com",
    "website": "https://tagre.pe",
    "license": "Other proprietary",
    "depends": ["portal", "tgr_document_base"],
    "data": [
        "views/template.xml",
    ],
    "images": [
        "static/description/tgr_document_preview_almightycs_cover.jpg",
    ],
    "cloc_exclude": [
        "static/**/*",
    ],
    "application": False,
    "sequence": 0,
}
