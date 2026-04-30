# -*- coding: utf-8 -*-
{
    "name": "Gestion de Documentos Base",
    "summary": "Gestionar documentos en un solo lugar o ver todos los documentos relacionados directamente.",
    "description": """
Gestion de Documentos Base
==========================
Gestionar documentos en un solo lugar o ver todos los documentos
relacionados directamente en el paciente.
    """,
    "version": "19.0.1.0.1",
    "category": "Medical",
    "author": "tagre.pe",
    "maintainer": "cvjuan270@gmail.com",
    "website": "https://tagre.pe",
    "license": "Other proprietary",
    "depends": ["mail", "hr"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "view/document_view.xml",
        "view/attachment_view.xml",
        "view/menu_item.xml",
    ],
    "images": [
        "static/description/document_management_system_almightycs_cover.jpg",
    ],
    "application": False,
    "sequence": 2,
}
