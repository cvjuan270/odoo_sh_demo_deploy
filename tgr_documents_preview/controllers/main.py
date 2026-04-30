# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
from odoo.tools.translate import _


class TgrImageZoom(http.Controller):

    @http.route(["/my/tgr/image/<string:model>/<int:record>"], type="http", auth="user", website=True, sitemap=False)
    def tgr_image_preview(self, model=False, record=False, **kwargs):
        record = request.env[model].browse([record])
        attachments = request.env["ir.attachment"].search(
            [
                ("id", "in", record.attachment_ids.ids),
                ("mimetype", "in", ["image/jpeg", "image/jpg", "image/png", "image/gif"]),
            ]
        )
        return request.render("tgr_documents_preview.tgr_image_preview", {"attachments": attachments})


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

