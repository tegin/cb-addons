# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import os
from odoo import tools
from odoo.tools import mute_logger
from odoo.tests.common import TransactionCase
from tempfile import TemporaryDirectory
from mock import patch
from io import BytesIO
import time

PATCH_CLASS = (
    "odoo.addons.hash_search_document_scanner_queue_ssh.models."
    "hash_search.SSHClient"
)


class TestConnection:
    def __init__(self, data, filename=""):
        self.data = data
        self.filename = filename

    def connect(self, hostname, port, username, password):
        return

    def open_sftp(self):
        return SftpConnection(self.data, self.filename)

    def close(self):
        return

    def load_system_host_keys(self):
        return

    def get_host_keys(self):
        return Keys()


class Keys:
    def add(self, *args):
        return


class SftpConnection:
    def __init__(self, data, filename):
        self.data = data
        self.filename = filename

    def close(self):
        return

    def normalize(self, path):
        return path

    def chdir(self, path):
        return

    def get(self, path, new_path):
        with open(new_path, mode="wb") as f:
            f.write(self.data)

    def open(self, path, type=""):
        return BytesIO(self.data)

    def listdir_attr(self, path):
        return [TestAttribute(self.filename)]

    def remove(self, filename):
        return


class TestAttribute:
    def __init__(self, name):
        self.filename = name
        self.st_atime = time.time()


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
        self.pre_tmpdir = TemporaryDirectory()
        self.env["ir.config_parameter"].set_param(
            "hash_search_document_scanner.path", self.tmpdir.name
        )
        self.env["ir.config_parameter"].set_param(
            "hash_search_document_scanner_queue.preprocess_path",
            self.pre_tmpdir.name,
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
        with patch(PATCH_CLASS) as mock:
            mock.return_value = TestConnection(file, "test_file.pdf")
            self.env["hash.search"].with_context(
                test_queue_job_no_delay=True,
                scanner_single_commit=True,
                scanner_ignore_time=True,
            ).cron_ssh_move_documents()
        self.assertFalse(
            os.path.exists(
                os.path.join(self.no_ok_tmpdir.name, "test_file.pdf")
            )
        )
        self.assertFalse(
            os.path.exists(os.path.join(self.pre_tmpdir.name, "test_file.pdf"))
        )
        self.assertFalse(
            os.path.exists(os.path.join(self.tmpdir.name, "test_file.pdf"))
        )
        self.assertTrue(
            os.path.exists(os.path.join(self.ok_tmpdir.name, "test_file.pdf"))
        )
        self.assertTrue(
            self.env["ir.attachment"].search(
                [
                    ("res_model", "=", partner._name),
                    ("res_id", "=", partner.id),
                ]
            )
        )

    def test_no_ok_assign(self, mck):
        file = tools.file_open(
            "test_file.pdf",
            mode="rb",
            subdir="addons/hash_search_document_scanner/tests",
        ).read()
        with patch(PATCH_CLASS) as mock:
            mock.return_value = TestConnection(file, "test_file.pdf")
            self.env["hash.search"].with_context(
                test_queue_job_no_delay=True,
                scanner_single_commit=True,
                scanner_ignore_time=True,
            ).cron_ssh_move_documents()
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
        with patch(PATCH_CLASS) as mock:
            mock.return_value = TestConnection(file, "test_file.pdf")
            self.env["hash.search"].with_context(
                test_queue_job_no_delay=True,
                scanner_single_commit=True,
                scanner_ignore_time=True,
            ).cron_ssh_move_documents()
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
        with mute_logger(
            "odoo.addons.hash_search_document_scanner.models.hash_search"
        ):
            with patch(PATCH_CLASS) as mock:
                mock.return_value = TestConnection(
                    file[: int(len(file) / 2)], "test_file.pdf"
                )
                self.env["hash.search"].with_context(
                    test_queue_job_no_delay=True,
                    scanner_single_commit=True,
                    scanner_ignore_time=True,
                ).cron_ssh_move_documents()
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
