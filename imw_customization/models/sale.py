# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class SaleOrderOption(models.Model):
    _inherit = 'sale.order.option'

    imw_measurement = fields.Float(string='Measurement', default=1)
    otherUnitMeasure = fields.Many2one('uom.uom', 'Other Unit of Measure')
    imw_qty = fields.Float(string='Quantity')

    # @api.multi
    @api.onchange('imw_qty', 'imw_measurement')
    def _ChangeQty(self):
        for rec in self:
            if float(rec.imw_measurement) == 0:
                rec.imw_measurement = 1

            rec.quantity = float(rec.imw_qty) * float(rec.imw_measurement)

    # @api.multi
    @api.onchange('quantity')
    def _change_uom_qty(self):
        for rec in self:
            if float(rec.imw_measurement) == 0:
                rec.imw_measurement = 1
            # self.product_uom_qty = float(self.imw_qty) * float(self.imw_measurement)
            imwQty = float(rec.imw_qty) if float(rec.imw_qty) > 0 else 1
            rec.imw_measurement = float(rec.quantity) / imwQty

    @api.onchange('product_id', 'uom_id')
    def _onchange_product_id(self):
        ret = super(SaleOrderOption, self)._onchange_product_id()
        for rec in self:
            rec.otherUnitMeasure = rec.product_id.otherUnitMeasure
            if float(rec.imw_measurement) == 0:
                rec.imw_measurement = 1
        return ret

    # @api.multi
    # @api.onchange('product_id')
    # def _onchangeProductId(self):
    #     self.product_uom_change()
    #     self.otherUnitMeasure = self.product_id.otherUnitMeasure
    #     if float(self.imw_measurement) == 0:
    #         self.imw_measurement = 1

    #     if float(self.imw_qty) == 0:
    #         self.imw_qty = 1
    #     if float(self.product_uom_qty) == 0:
    #         self.product_uom_qty = 1


# class SaleOrder(models.Model):
#     _inherit = 'sale.order'

#     @api.multi
#     def sale_order_alltotalhide(self):
#         self.filtered(lambda s: s.state == 'draft').write({'state': 'sent'})

#         return self.env.ref('sale.action_report_saleorder') \
#             .with_context({'discard_logo_check': True}).report_action(self, data=1)

#     def sale_order_totalhide(self):
#         self.filtered(lambda s: s.state == 'draft').write({'state': 'sent'})

#         return self.env.ref('sale.action_report_saleorder') \
#             .with_context({'discard_logo_check': True}).report_action(self, data=2)


class saleorderline(models.Model):
    _inherit = 'sale.order.line'

    imw_qty = fields.Float(string='Quantity')
    imw_measurement = fields.Float(string='Measurement', default=1)
    category_id = fields.Many2one('product.category', 'category')
    otherUnitMeasure = fields.Many2one('uom.uom', 'Other Unit of Measure')

    def _prepare_invoice_line(self, **optional_values):
        """
        Prepare the dict of values to create the new invoice line for a sales order line.

        :param qty: float quantity to invoice
        :param optional_values: any parameter that should be added to the returned invoice line
        """
        self.ensure_one()
        res = {
            'display_type': self.display_type,
            'sequence': self.sequence,
            'name': self.name,
            'product_id': self.product_id.id,
            'product_uom_id': self.product_uom.id,
            'quantity': self.qty_to_invoice,
            'discount': self.discount,
            'price_unit': self.price_unit,
            'tax_ids': [(6, 0, self.tax_id.ids)],
            'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
            'sale_line_ids': [(4, self.id)],
            'imw_qty': self.imw_qty,
            'imw_measurement': self.imw_measurement,
            'otherUnitMeasure': self.otherUnitMeasure.id,
            'category_id': self.category_id,
        }
        if self.order_id.analytic_account_id:
            res['analytic_account_id'] = self.order_id.analytic_account_id.id
        if optional_values:
            res.update(optional_values)
        if self.display_type:
            res['account_id'] = False
        return res

    # @api.multi
    @api.onchange('imw_qty', 'imw_measurement')
    def _ChangeQty(self):
        for rec in self:
            if float(rec.imw_measurement) == 0:
                rec.imw_measurement = 1
            rec.product_uom_qty = float(rec.imw_qty) * float(rec.imw_measurement)

    # @api.multi
    @api.onchange('product_uom_qty')
    def _change_uom_qty(self):
        for rec in self:
            if float(rec.imw_measurement) == 0:
                rec.imw_measurement = 1
            # self.product_uom_qty = float(self.imw_qty) * float(self.imw_measurement)
            imwQty = float(rec.imw_qty) if float(rec.imw_qty) > 0 else 1
            rec.imw_measurement = float(rec.product_uom_qty) / imwQty

    # @api.multi
    @api.onchange('product_id')
    def _onchangeProductId(self):
        for rec in self:
            rec.product_uom_change()
            rec.otherUnitMeasure = rec.product_id.otherUnitMeasure
            if float(rec.imw_measurement) == 0:
                rec.imw_measurement = 1
            if float(rec.imw_qty) == 0:
                rec.imw_qty = 1
            if float(rec.product_uom_qty) == 0:
                rec.product_uom_qty = 1

    @api.onchange('product_uom')  # , 'product_uom_qty')
    def product_uom_change(self):
        for rec in self:
            if not rec.product_uom or not rec.product_id:
                rec.price_unit = 0.0
                return
            if rec.order_id.pricelist_id and rec.order_id.partner_id:
                product = rec.product_id.with_context(
                    lang=rec.order_id.partner_id.lang,
                    partner=rec.order_id.partner_id,
                    quantity=rec.product_uom_qty,
                    date=rec.order_id.date_order,
                    pricelist=rec.order_id.pricelist_id.id,
                    uom=rec.product_uom.id,
                    fiscal_position=rec.env.context.get('fiscal_position')
                )
                rec.price_unit = self.env['account.tax']._fix_tax_included_price_company(rec._get_display_price(product),
                                                                                          product.taxes_id, rec.tax_id,
                                                                                          rec.company_id)
