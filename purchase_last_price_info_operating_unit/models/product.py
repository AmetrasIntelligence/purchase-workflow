from odoo import fields, models


class Product(models.Model):
    _inherit = "product.product"

    last_purchase_line_ids = fields.One2many(
        domain=lambda self: [
            ("state", "in", ["purchase", "done"]),
            ("operating_unit_id", "=", self.env.user.operating_unit_default_get().id),
        ],
    )
