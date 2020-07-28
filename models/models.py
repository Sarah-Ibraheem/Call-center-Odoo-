# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta


class Calls(models.Model):
    _name = 'my_module.calls'
    _description = 'call_details'
    # _rec_name = 'start_time '  by default make index by name if not found put index value in rec_name

    start_time = fields.Datetime()
    stop_time = fields.Datetime()
    duration = fields.Char(compute='_compute_duration', store=True)
    source = fields.Char()
    destination = fields.Char()
    name = fields.Char(default='NewCustomer')
    station = fields.Many2one(comodel_name='my_module.station')
    tags = fields.Many2many(comodel_name='my_module.tags')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('invoiced', 'Invoiced'),
    ], default='draft', string='Status')
    partner_id = fields.Many2one(comodel_name='res.partner')

    # the default index is name

    @api.constrains('stop_time')
    def _check_stop_time(self):
        for record in self:
            if record.start_time > record.stop_time:
                raise ValidationError("start time must be less than stop time")
            # all records passed the test, don't return anything

    @api.depends('stop_time', 'start_time')
    def _compute_duration(self):
        for record in self:
            record.duration = 0.0
            if record.stop_time and record.start_time:
                record.duration = (record.stop_time - record.start_time).seconds / 60

            # temp = relativedelta(record.stop_time, record.start_time)
            # record.duration = ((temp.days * 24 * 60 * 60) + (temp.hours * 60 * 60) + (temp.minutes * 60)) / 60

    def create_invoice(self):
            inv_obj = self.env['account.move'].create({
                'partner_id': self.partner_id.id,
                'move_type':'out_invoice',
            })
            invoice_line_object = self.env['account.move.line'].create({
                'name': 'call cost',
                'move_id': inv_obj.id,
                'price_unit': float(self.duration) * 0.30,
                'account_id': self.partner_id.property_account_receivable_id.id,
            })


class Station(models.Model):
    _name = 'my_module.station'

    name = fields.Char()
    calls = fields.One2many(comodel_name='my_module.calls', inverse_name='station')


class Tags(models.Model):
    _name = 'my_module.tags'

    name = fields.Char()
