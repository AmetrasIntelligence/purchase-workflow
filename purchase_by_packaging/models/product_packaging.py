# Copyright 2021 Ametras
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import api, fields, models


class ProductPackaging(models.Model):
    _inherit = "product.packaging"

    purchase_rounding = fields.Float(
        string="Purchase Rounding Precision",
        digits="Product Unit of Measure",
        required=True,
        default=0.1,
        help="The allowed package quantity will be a multiple of this value. "
        "Use 1.0 for a package that cannot be further split.",
    )

    actual_purchase_qty = fields.Float(compute="_compute_actual_purchase_qty")

    @api.depends("purchase_rounding", "qty")
    def _compute_actual_purchase_qty(self):
        for record in self:
            record.actual_purchase_qty = record.purchase_rounding * record.qty
