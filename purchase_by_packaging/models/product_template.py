# Copyright 2021 Ametras
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import api, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.onchange("purchase_ok")
    def _change_purchase_ok(self):
        if not self.purchase_ok and self.purchase_only_by_packaging:
            self.purchase_only_by_packaging = False
