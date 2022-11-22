# -*- coding: utf-8 -*-
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import date, datetime, timedelta
import logging
from odoo import api, fields, models, exceptions, _

_logger = logging.getLogger(__name__)


class IncomingProductsKardex(models.TransientModel):
    _name = 'incoming.products.kardex'
    _description = "Module to create kardex for the entry of material to the warehouse"

    picking_id = fields.Many2one(
        'stock.picking',
        'Stock Picking',
        required=True)

    # # @api.multi
    def get_stock_picking_data(self):
        stock_kardex_obj = self.env['stock.kardex.line']
        for line in self.picking_id.move_line_ids_without_package:
            stock_kardex_obj.create({
                'stock_kardex_id': self.id,
                'product_name': line.product_id.barcode,
                'ordered_qty': line.qty_done,
                'qty_by_palette': 0,
                'product_conform': False,
                'lot_id': line.lot_id.id})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'incoming.products.kardex',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }

    # # @api.multi
    def get_kardex(self):
        if self.stock_kardex_line_ids:
            msj = ''
            for lines in self.stock_kardex_line_ids:
                if lines.qty_by_palette == 0:
                    msj = 'Quantity per pallet has not been entered for code %s.' % lines.product_name
                    raise exceptions.UserError(msj)
                if lines.ordered_qty < lines.qty_by_palette:
                    msj = 'The amount per pallet should not be greater than the amount requested. Product %s' % lines.product_name
                    raise exceptions.UserError(msj)

            stock_kardex_obj = self.env['stock.kardex.line']
            for line in self.stock_kardex_line_ids:
                if line.qty_by_palette > 0:
                    if line.ordered_qty > line.qty_by_palette:
                        complete = int(
                            (line.ordered_qty // line.qty_by_palette))
                        balance = (line.ordered_qty % line.qty_by_palette)
                        if complete:
                            complete_iterator = 1
                            while complete_iterator < complete:
                                stock_kardex_obj.create({
                                    'stock_kardex_id': self.id,
                                    'product_name': line.product_name,
                                    'ordered_qty': line.ordered_qty,
                                    'qty_by_palette': line.qty_by_palette,
                                    'product_conform': line.product_conform,
                                    'lot_id': line.lot_id.id})
                                complete_iterator = complete_iterator + 1
                        if balance:
                            stock_kardex_obj.create({
                                'stock_kardex_id': self.id,
                                'product_name': line.product_name,
                                'ordered_qty': line.ordered_qty,
                                'qty_by_palette': balance,
                                'product_conform': line.product_conform,
                                'lot_id': line.lot_id.id})
            self.getted = True
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'incoming.products.kardex',
                'view_mode': 'form',
                'view_type': 'form',
                'res_id': self.id,
                'views': [(False, 'form')],
                'target': 'new',
            }

    def print_kardex(self, data=None):
        if self.getted:
            report = self.env['ir.actions.report']._get_report_from_name(
                'incoming_products_kardex.incoming_products_kardex_report_template')
            return report.report_action(self)
        else:
            raise exceptions.Warning('No se han generado los kardex')

    date = fields.Date(
        string="Date", required=True, default=fields.Date.today)
    lot = fields.Char('Lot', required=True)
    responsible = fields.Char('responsible', required=True)
    getted = fields.Boolean('Getted', default=False)
    supplier = fields.Char('Supplier', required=True)

    stock_kardex_line_ids = fields.One2many(
        'stock.kardex.line', 'stock_kardex_id', 'Lines')


class StockKardexLine(models.TransientModel):
    _name = 'stock.kardex.line'
    _description = "Modulo para crear Kardex de ingreso de material al almacen (lineas)"

    stock_kardex_id = fields.Many2one(
        'incoming.products.kardex', 'Kardex', readonly=True)
    product_name = fields.Char('Product', readonly=True)
    ordered_qty = fields.Float('Ordered qty', readonly=False)
    qty_by_palette = fields.Float('Qty by palette')
    product_conform = fields.Boolean('Conform')
    lot_id = fields.Many2one('stock.lot', 'Lot')
