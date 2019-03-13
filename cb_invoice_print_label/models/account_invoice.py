# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class AccountInvoice(models.Model):
    _name = 'account.invoice'
    _inherit = ['account.invoice', 'hash.search.mixin']

    def action_print_label(self):
        self.ensure_one()
        label_action = self.env.ref(
            'cb_invoice_print_label.account_invoice_print_label'
        )
        content = label_action.render_label(self)
        behaviour = self.remote.with_context(
            printer_usage='label'
        ).get_printer_behaviour()
        if 'printer' not in behaviour:
            return False
        printer = behaviour.pop('printer')
        printer.with_context(
            print_report_name='labels_%s_%s' % (self._name, self.id)
        ).print_document(
            report=self.env['ir.actions.report'],
            content=content.encode('ascii'), doc_format='txt'
        )
        return True
