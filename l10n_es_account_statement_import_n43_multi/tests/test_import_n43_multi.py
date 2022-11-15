# Copyright 2016-2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64

from odoo import fields
from odoo.modules.module import get_module_resource

from odoo.addons.edi.tests import common


class L10nEsAccountBankStatementImportN43(
    common.EDIBackendCommonComponentRegistryTestCase
):
    @classmethod
    def setUpClass(cls):
        super(L10nEsAccountBankStatementImportN43, cls).setUpClass()
        cls._load_module_components(cls, "edi_account")
        cls._load_module_components(
            cls, "l10n_es_account_bank_statement_import_n43_multi"
        )
        cls.partner = cls.env["res.partner"].create({"name": "Test partner N43"})
        cls.journal = cls.env["account.journal"].create(
            {
                "type": "bank",
                "name": "Test N43 bank",
                "code": "BNKN43",
                "n43_identifier": "000000000000000000",
            }
        )
        cls.journal_2 = cls.env["account.journal"].create(
            {
                "type": "bank",
                "name": "Test N43 bank2",
                "code": "BNKN432",
                "n43_identifier": "100000000000000000",
            }
        )
        n43_file_path = get_module_resource(
            "l10n_es_account_bank_statement_import_n43_multi",
            "tests",
            "test_multi.n43",
        )
        n43_file = base64.b64encode(open(n43_file_path, "rb").read())
        cls.import_wizard = (
            cls.env["account.bank.statement.import.n43.multi"]
            .with_context(journal_id=cls.journal.id)
            .create({"data_file": n43_file, "filename": "data.txt"})
        )

    def test_import_n43_multi(self):
        statements = self.env["account.bank.statement"].search([])
        action = self.import_wizard.process_file()
        self.assertFalse(action)
        new_statements = self.env["account.bank.statement"].search(
            [("id", "not in", statements.ids)]
        )
        self.assertTrue(new_statements)
        self.assertEqual(2, len(new_statements))
        for statement in new_statements:
            self.assertEqual(statement.date, fields.Date.to_date("2016-02-01"))
            self.assertEqual(len(statement.line_ids), 3)
            self.assertEqual(
                statement.line_ids[2].date,
                fields.Date.to_date("2016-05-16"),
            )
            self.assertAlmostEqual(statement.balance_start, 0, 2)
            self.assertAlmostEqual(statement.balance_end, 101.96, 2)
