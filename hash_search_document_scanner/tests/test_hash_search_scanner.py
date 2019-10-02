# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import os
from odoo import tools
from odoo.tools import mute_logger
from odoo.tests.common import TransactionCase
from tempfile import TemporaryDirectory
from mock import patch


@patch(
    "odoo.addons.hash_search.models.hash_search.HashSearch.hash_search_models",
    return_value=["res.partner"],
)
class TestHashSearchScanner(TransactionCase):
    def setUp(self):
        super(TestHashSearchScanner, self).setUp()
        self.tmpdir = TemporaryDirectory()
        self.ok_tmpdir = TemporaryDirectory()
        self.no_ok_tmpdir = TemporaryDirectory()
        self.env["ir.config_parameter"].set_param(
            "hash_search_document_scanner.path", self.tmpdir.name
        )
        self.env["ir.config_parameter"].set_param(
            "hash_search_document_scanner.ok_path", self.ok_tmpdir.name
        )
        self.env["ir.config_parameter"].set_param(
            "hash_search_document_scanner.failure_path", self.no_ok_tmpdir.name
        )

    def tearDown(self):
        super().tearDown()
        self.tmpdir.cleanup()
        self.ok_tmpdir.cleanup()
        self.no_ok_tmpdir.cleanup()

    def test_ok_pdf(self, mck):
        partner = self.env["res.partner"].create({"name": "Partner"})
        hash = self.env["hash.search"].create(
            {
                "res_id": partner.id,
                "model": partner._name,
                "object_id": "%s,%s" % (partner._name, partner.id),
                "name": "HOLAHOLAHOLA",
            }
        )
        self.assertEqual(hash.object_id, partner)
        file = tools.file_open(
            "test_file.pdf",
            mode="rb",
            subdir="addons/hash_search_document_scanner/tests",
        ).read()
        with open(os.path.join(self.tmpdir.name, "test_file.pdf"), "wb") as f:
            f.write(file)
        self.env["hash.search"].cron_scan_documents()
        self.assertTrue(
            self.env["ir.attachment"].search(
                [
                    ("res_model", "=", partner._name),
                    ("res_id", "=", partner.id),
                ]
            )
        )
        self.assertTrue(
            os.path.exists(os.path.join(self.ok_tmpdir.name, "test_file.pdf"))
        )

    def test_no_ok_assign(self, mck):
        file = tools.file_open(
            "test_file.pdf",
            mode="rb",
            subdir="addons/hash_search_document_scanner/tests",
        ).read()
        with open(os.path.join(self.tmpdir.name, "test_file.pdf"), "wb") as f:
            f.write(file)
        self.env["hash.search"].cron_scan_documents()
        self.assertTrue(
            os.path.exists(
                os.path.join(self.no_ok_tmpdir.name, "test_file.pdf")
            )
        )
        missing = self.env["hash.missing.document"].search(
            [("name", "=", "test_file.pdf"), ("state", "=", "pending")]
        )
        partner = self.env["res.partner"].create({"name": "Partner"})
        self.assertTrue(missing)
        hash = self.env["hash.search"].create(
            {
                "res_id": partner.id,
                "model": partner._name,
                "object_id": "%s,%s" % (partner._name, partner.id),
            }
        )
        missing.assign_hash(hash)

    def test_no_ok_reject(self, mck):
        file = tools.file_open(
            "test_file.pdf",
            mode="rb",
            subdir="addons/hash_search_document_scanner/tests",
        ).read()
        with open(os.path.join(self.tmpdir.name, "test_file.pdf"), "wb") as f:
            f.write(file)
        self.env["hash.search"].cron_scan_documents()
        self.assertTrue(
            os.path.exists(
                os.path.join(self.no_ok_tmpdir.name, "test_file.pdf")
            )
        )
        missing = self.env["hash.missing.document"].search(
            [("name", "=", "test_file.pdf"), ("state", "=", "pending")]
        )
        self.assertTrue(missing)
        missing.reject_assign_document()
        self.assertEqual(missing.state, "deleted")

    def test_corrupted(self, mck):
        file = tools.file_open(
            "test_file.pdf",
            mode="rb",
            subdir="addons/hash_search_document_scanner/tests",
        ).read()
        with open(os.path.join(self.tmpdir.name, "test_file.pdf"), "wb") as f:
            f.write(file[: int(len(file) / 2)])
        with mute_logger(
            "odoo.addons.hash_search_document_scanner.models.hash_search"
        ):
            self.env["hash.search"].cron_scan_documents()
        self.assertFalse(
            os.path.exists(os.path.join(self.ok_tmpdir.name, "test_file.pdf"))
        )
        self.assertFalse(
            os.path.exists(
                os.path.join(self.no_ok_tmpdir.name, "test_file.pdf")
            )
        )
        self.assertFalse(
            os.path.exists(os.path.join(self.tmpdir.name, "test_file.pdf"))
        )
