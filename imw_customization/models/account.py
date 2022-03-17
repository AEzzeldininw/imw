# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

from num2words import num2words


class AccountInvoice(models.Model):
    _inherit = "account.move"
    _description = "Invoice"

    imw_ref2 = fields.Char('Reference2')

    # @api.multi
    def amount_to_word(self, amount):
        return num2words(amount, lang='en').title()


class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"

    referenceRecive = fields.Char(string='R Reference', states={'open': [('readonly', False)]}, copy=False,
                                  readonly=True,
                                  help="Used to hold the reference of the external mean that created this statement (name of imported file, reference of online synchronization...)")


class AccountInvoiceLine(models.Model):
    _inherit = 'account.move.line'

    imw_qty = fields.Float(string='Quantity')
    imw_measurement = fields.Float(string='Measurement', default=1)
    category_id = fields.Many2one('product.category', 'category')
    otherUnitMeasure = fields.Many2one('uom.uom', 'Other Unit of Measure')

    @api.onchange('imw_qty', 'imw_measurement')
    def _ChangeQty(self):
        for rec in self:
            if float(rec.imw_measurement) == 0:
                rec.imw_measurement = 1
            rec.quantity = float(rec.imw_qty) * float(rec.imw_measurement)

    @api.onchange('product_id')
    def _onchangeProductId(self):
        for rec in self:
            rec.otherUnitMeasure = rec.product_id.otherUnitMeasure
            if float(rec.imw_qty) == 0:
                rec.imw_qty = 1
            if float(rec.imw_measurement) == 0:
                rec.imw_measurement = 1
                # rec.product_uom_qty = float(rec.imw_qty) * float(rec.imw_measurement)
            imwQty = float(rec.imw_qty) if float(rec.imw_qty) > 0 else 1
            rec.imw_measurement = float(rec.quantity) / imwQty
