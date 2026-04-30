# -*- coding: utf-8 -*-
{
    "name": "Widget de Temporizador Web",
    "summary": "Agrega un widget de temporizador en las vistas del backend",
    "category": "Technical",
    "version": "19.0.1.0.1",
    "author": "tagre.pe",
    "maintainer": "cvjuan270@gmail.com",
    "website": "https://tagre.pe",
    "license": "Other proprietary",
    "depends": ["base", "web"],
    "data": [],
    "assets": {
        "web.assets_backend": [
            "web_timer_widget/static/src/js/tgr_timer.js",
            "web_timer_widget/static/src/js/tgr_timer.xml",
        ]
    },
    "images": [
        "static/description/timer.png",
    ],
    "installable": True,
    "auto_install": False,
    "application": False,
}
