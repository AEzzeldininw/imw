# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)
 

class imw_product_template(models.Model):
    _inherit = 'product.template'

    otherUnitMeasure = fields.Many2one('uom.uom', 'Other Unit of Measure')



 


