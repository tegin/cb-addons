# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools import float_compare


class SafeBoxMove(models.Model):
    _name = 'safe.box.move'

    name = fields.Char(required=True, default='/', readonly=True, )
    safe_box_group_id = fields.Many2one(
        comodel_name='safe.box.group',
        string='Safe box group',
        required=True,
        delete='restrict',
    )
    line_ids = fields.One2many(
        comodel_name='safe.box.move.line',
        inverse_name='safe_box_move_id',
    )
    account_move_ids = fields.One2many(
        comodel_name='account.move',
        inverse_name='safe_box_move_id',
        readonly=True,

    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('closed', 'Closed'),
        ('cancelled', 'Cancelled')
    ], required=True, readonly=True, default='draft')

    def validate(self):
        amount = sum(self.line_ids.mapped('amount'))
        amount -= sum(self.account_move_ids.mapped('line_ids').filtered(
            lambda r: r.account_id.id in self.safe_box_group_id.account_ids.ids
        ).mapped('balance'))
        if float_compare(amount, 0, precision_digits=6):
            raise ValidationError(_('Move must be balanced'))
        for safe_box in self.line_ids.mapped('safe_box_id'):
            if (
                self.env.user.id not in safe_box.user_ids.ids and
                not self.env.user.has_group('safe_box.group_safe_box_manager')
            ):
                raise ValidationError(
                    _('You are not allowed to move/take money from %s')
                    % safe_box.name
                )
            safe_box.sudo().recompute_amount()
            if float_compare(safe_box.amount + sum(
                    self.line_ids.filtered(
                        lambda r: r.safe_box_id == safe_box
                    ).mapped('amount')), 0, precision_digits=6) < 0:
                raise ValidationError(_(
                    'Safe box cannot have a negative value'))

    @api.multi
    def close(self):
        self.ensure_one()
        self.validate()
        self.write({
            'state': 'closed',
            'name': self.safe_box_group_id.sequence_id.next_by_id(),
        })
        self.line_ids.mapped('safe_box_id').sudo().recompute_amount()


class SafeBoxMoveLine(models.Model):
    _name = 'safe.box.move.line'

    safe_box_move_id = fields.Many2one(
        comodel_name='safe.box.move',
        required=True,
        string='Move',
    )
    safe_box_id = fields.Many2one(
        comodel_name='safe.box',
        string='Safe box',
        required=True,
        domain="[('safe_box_group_id', '=', safe_box_group_id)]",
        delete='restrict'
    )
    state = fields.Selection(
        related='safe_box_move_id.state'
    )
    safe_box_group_id = fields.Many2one(
        comodel_name='safe.box.group',
        string='Safe box group',
        related='safe_box_move_id.safe_box_group_id',
    )
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        related='safe_box_group_id.currency_id',
        readonly=True,
    )
    amount = fields.Monetary(
        required=True,
        default=0,
        currency_field='currency_id',
    )
