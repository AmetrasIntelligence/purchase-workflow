# Copyright 2021 Ametras
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import api, models


class PurchaseOrderLine(models.Model):

    _inherit = "purchase.order.line"

    def get_packaging_qty(self, vals=None):
        if not vals:
            vals = []
        product = (
            self.env["product.product"].browse(vals["product_id"])
            if "product_id" in vals
            else self.product_id
        )

        quantity = vals["product_qty"] if "product_qty" in vals else self.product_qty
        uom = (
            self.env["uom.uom"].browse(vals["product_uom"])
            if "product_uom" in vals
            else self.product_uom
        )
        packaging = (
            self.env["product.packaging"].browse(vals["product_packaging_id"])
            if "product_packaging_id" in vals
            else self.product_packaging_id
        )

        return product._convert_purchase_packaging_qty(
            quantity,
            uom or product.uom_po_id,
            packaging=packaging,
        )

    @api.depends("product_id", "product_uom_qty", "product_uom")
    def _compute_product_packaging_id(self):
        for rec in self:
            rec.product_packaging_id = False
            rec._force_packaging()
            rec._force_qty_with_package()
        return super()._compute_product_packaging_id()

    def _get_product_packaging_having_multiple_qty(self, product, qty, uom):
        if uom != product.uom_po_id:
            qty = uom._compute_quantity(qty, product.uom_po_id)
        return product.get_first_purchase_packaging_with_multiple_qty(qty)

    def _inverse_product_packaging_qty(self):
        # Force skipping of auto assign
        # if we are writing the product_qty directly via inverse
        return super(
            PurchaseOrderLine, self.with_context(_skip_auto_assign=True)
        )._inverse_product_packaging_qty()

    def write(self, vals):
        """Auto assign packaging if needed"""
        if vals.get("product_packaging_id") or self.env.context.get(
            "_skip_auto_assign"
        ):
            # setting the packaging directly, skip auto assign
            return super().write(vals)
        for line in self:
            line_vals = vals.copy()
            if line_vals.get("product_id", False):
                packaging = line._get_autoassigned_packaging(line_vals)
                if packaging:
                    line_vals.update({"product_packaging_id": packaging})
            if (
                line_vals.get("product_qty")
                or line_vals.get("product_id")
                or line_vals.get("product_packaging_id")
                or line_vals.get("product_uom")
            ):
                product_qty = line.get_packaging_qty(line_vals)
                line_vals.update({"product_qty": product_qty})
            super(PurchaseOrderLine, line).write(line_vals)
        return True

    @api.model_create_multi
    def create(self, vals_list):
        """Auto assign packaging if needed"""
        # Fill the packaging if they are empty and the quantity is a multiple
        for vals in vals_list:
            if not vals.get("product_packaging_id"):
                if "product_qty" not in vals:
                    vals["product_qty"] = 1.0
                packaging = self._get_autoassigned_packaging(vals)
                if packaging:
                    vals.update({"product_packaging_id": packaging})
                    if vals.get("product_id") and vals.get("product_uom"):
                        product_qty = self.get_packaging_qty(vals)
                        vals.update({"product_qty": product_qty})
        return super().create(vals_list)

    def _get_autoassigned_packaging(self, vals=None):
        if not vals:
            vals = []
        product = (
            self.env["product.product"].browse(vals["product_id"])
            if "product_id" in vals
            else self.product_id
        )
        if product and product.purchase_only_by_packaging:
            quantity = (
                vals["product_qty"] if "product_qty" in vals else self.product_qty
            )
            uom = (
                self.env["uom.uom"].browse(vals["product_uom"])
                if "product_uom" in vals
                else self.product_uom
            )
            packaging = self._get_product_packaging_having_multiple_qty(
                product, quantity, uom
            )
            if packaging:
                return packaging.id
        return None

    def _force_packaging(self):
        if not self.product_packaging_id and self.product_id.purchase_only_by_packaging:
            packaging_id = self._get_autoassigned_packaging()
            if packaging_id:
                self.update({"product_packaging_id": packaging_id})
