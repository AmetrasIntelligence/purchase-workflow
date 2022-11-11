from odoo import fields, models


class Product(models.Model):
    _inherit = "product.product"

    last_purchase_line_ids = fields.One2many(
        comodel_name="purchase.order.line",
        inverse_name="product_id",
        domain=lambda self: [
            ("state", "in", ["purchase", "done"]),
            ("operating_unit_id", "in", self.env.user.operating_unit_ids.ids),
        ],
    )
