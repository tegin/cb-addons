# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PosSessionValidation(models.Model):
    _name = "pos.session.validation"
    _description = "Session validation"
    _order = "id desc"

    name = fields.Char(default="/", required=True, readonly=True)
    date = fields.Date(default=lambda self: fields.Date.today(), readonly=True)
    safe_box_group_id = fields.Many2one(
        "safe.box.group",
        string="Safe box system",
        required=True,
        readonly=True,
    )
    pos_session_ids = fields.One2many(
        "pos.session",
        inverse_name="pos_session_validation_id",
        string="Sessions",
        readonly=True,
    )
    line_ids = fields.One2many(
        comodel_name="pos.session.validation.line",
        inverse_name="pos_session_validation_id",
    )
    state = fields.Selection(
        [("draft", "Draft"), ("closed", "Closed"), ("approved", "Approved")]
    )
    statement_ids = fields.One2many(
        comodel_name="account.bank.statement",
        compute="_compute_statement_ids",
        readonly=True,
    )
    statement_line_ids = fields.One2many(
        comodel_name="account.bank.statement.line",
        compute="_compute_statement_ids",
        readonly=True,
    )
    issue_statement_line_ids = fields.One2many(
        comodel_name="account.bank.statement.line",
        compute="_compute_statement_values",
    )
    currency_id = fields.Many2one(
        "res.currency", related="safe_box_group_id.currency_id", readonly=True
    )
    amount = fields.Monetary(
        currency_field="currency_id", compute="_compute_statement_values"
    )
    coin_amount = fields.Monetary(
        currency_field="currency_id", compute="_compute_amount"
    )
    cash_amount = fields.Monetary(
        currency_field="currency_id", compute="_compute_statement_values"
    )
    closing_move_id = fields.Many2one("safe.box.move", "Closing move", readonly=True)
    closing_date = fields.Datetime(readonly=True)
    approve_move_id = fields.Many2one("safe.box.move", "Approve move", readonly=True)
    approve_date = fields.Datetime(readonly=True)

    @api.depends("pos_session_ids")
    def _compute_statement_ids(self):
        for record in self:
            record.statement_ids = record.pos_session_ids.mapped("statement_ids")
            record.statement_line_ids = record.statement_ids.mapped("line_ids")

    @api.depends("line_ids")
    def _compute_amount(self):
        for record in self:
            record.coin_amount = sum(record.line_ids.mapped("amount"))

    def _compute_statement_amount(self):
        lines = self.pos_session_ids.mapped("cash_register_id.line_ids")
        lines_not_computed = lines.filtered(
            lambda r: r.account_id
            not in r.statement_id.pos_session_id.payment_method_ids.mapped(
                "receivable_account_id"
            )
        )
        payments = self.pos_session_ids.mapped("order_ids.payment_ids")
        amount = sum(lines_not_computed.mapped("amount")) + sum(
            payments.mapped("amount")
        )
        return amount

    @api.depends("statement_ids", "pos_session_ids")
    def _compute_statement_values(self):
        for record in self:
            statements = record.statement_ids
            record.amount = sum(statements.mapped("total_entry_encoding"))
            record.amount = record._compute_statement_amount()
            record.cash_amount = sum(
                statements.filtered(lambda r: r.journal_id.type == "cash").mapped(
                    "total_entry_encoding"
                )
            )
            lines = record.statement_line_ids
            record.issue_statement_line_ids = lines.filtered(lambda r: not r.invoice_id)

    def safe_box_move_vals(self):
        return {"safe_box_group_id": self.safe_box_group_id.id}

    def safe_box_move_line_vals(self, move, safe_box, value):
        return {
            "safe_box_move_id": move.id,
            "safe_box_id": safe_box,
            "amount": value,
        }

    def account_move_vals(self, statement):
        account = self.safe_box_group_id.account_ids.filtered(
            lambda r: r.company_id.id == statement.journal_id.company_id.id
        )
        if not account:
            raise ValidationError(_("Account cannot be found for this company"))
        amount = statement.total_entry_encoding
        if amount > 0:
            statement_account = statement.journal_id.default_credit_account_id
        else:
            statement_account = statement.journal_id.default_debit_account_id
        return {
            "journal_id": statement.journal_id.id,
            "safe_box_move_id": self.closing_move_id.id,
            "line_ids": [
                (
                    0,
                    0,
                    {
                        "account_id": statement_account.id,
                        "credit": amount if amount > 0 else 0,
                        "debit": -amount if amount < 0 else 0,
                    },
                ),
                (
                    0,
                    0,
                    {
                        "account_id": account.id,
                        "credit": -amount if amount < 0 else 0,
                        "debit": amount if amount > 0 else 0,
                    },
                ),
            ],
        }

    def close(self):
        self.ensure_one()
        if self.state != "draft":
            raise ValidationError(_("You can only approve draft moves"))
        if self.coin_amount != self.cash_amount:
            raise ValidationError(_("Coins and Notes must match cash value"))
        self.closing_move_id = self.env["safe.box.move"].create(
            self.safe_box_move_vals()
        )
        lines = {}
        for line in self.line_ids:
            if not lines.get(line.safe_box_coin_id.type):
                lines[line.safe_box_coin_id.type] = 0
            lines[line.safe_box_coin_id.type] += line.amount
        for key in lines.keys():
            safe_box = False
            if key == "note":
                safe_box = self.safe_box_group_id.note_safe_box_id.id
            elif key == "coin":
                safe_box = self.safe_box_group_id.coin_safe_box_id.id
            if not safe_box:
                raise ValidationError(_("Safe boxes are not configured"))
            self.env["safe.box.move.line"].create(
                self.safe_box_move_line_vals(self.closing_move_id, safe_box, lines[key])
            )
        for statement in self.statement_ids.filtered(
            lambda r: (r.journal_id.type == "cash" and r.total_entry_encoding != 0)
        ):
            move = self.env["account.move"].create(self.account_move_vals(statement))
            move.post()
        self.closing_move_id.close()
        self.write({"state": "closed", "closing_date": fields.Datetime.now()})

    def approve(self):
        self.ensure_one()
        if self.state != "closed":
            raise ValidationError(_("You can only approve closed moves"))
        sbg = self.safe_box_group_id
        lines = []
        for initial_safe_box, end_safe_box in [
            (sbg.coin_safe_box_id, sbg.approve_coin_safe_box_id),
            (sbg.note_safe_box_id, sbg.approve_note_safe_box_id),
        ]:
            if end_safe_box:
                value = self.closing_move_id.line_ids.filtered(
                    lambda r: r.safe_box_id.id == initial_safe_box.id
                ).amount
                lines.append({"safe_box_id": end_safe_box.id, "amount": value})
                lines.append({"safe_box_id": initial_safe_box.id, "amount": -value})
        if len(lines) > 0:
            self.approve_move_id = self.env["safe.box.move"].create(
                {
                    "safe_box_group_id": self.safe_box_group_id.id,
                    "line_ids": [(0, 0, line) for line in lines],
                }
            )
            self.approve_move_id.close()
        self.write({"state": "approved", "approve_date": fields.Datetime.now()})

    @api.model
    def get_name(self, vals):
        return self.env["ir.sequence"].next_by_code("pos.session.validation") or "/"

    @api.model
    def create(self, vals):
        if vals.get("name", "/") == "/":
            vals.update({"name": self.get_name(vals)})
        return super(PosSessionValidation, self).create(vals)


class PosSessionValidationLine(models.Model):
    _name = "pos.session.validation.line"
    _description = "Add amount on validation"

    pos_session_validation_id = fields.Many2one(
        "pos.session.validation", required=True, readonly=True
    )
    safe_box_coin_id = fields.Many2one(
        "safe.box.coin", required=True, string="Coin", readonly=True
    )
    value = fields.Integer(required=True, default=0)
    amount = fields.Float(compute="_compute_amount")

    @api.depends("value", "safe_box_coin_id")
    def _compute_amount(self):
        for record in self:
            record.amount = record.safe_box_coin_id.rate * record.value
