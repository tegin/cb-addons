# Copyright 2018 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import fields
from odoo.tests.common import TransactionCase


class TestQueueNsca(TransactionCase):
    def test_cron(self):
        date = fields.Datetime.from_string(fields.Datetime.now()) + timedelta(
            seconds=-2
        )
        job_model = self.env["queue.job"]
        # The sentinel is used to prevent edition sensitive fields (such as
        # method_name) from RPC methods.
        edit_sentinel = job_model.EDIT_SENTINEL
        job_model = job_model.with_context(_job_edit_sentinel=edit_sentinel)
        job_1 = job_model.create(
            {
                "name": "Test",
                "state": "failed",
                "uuid": "1",
                "model_name": "nsca.server",
                "method_name": "_selection_encryption_method",
                "user_id": self.env.user.id,
                "date_created": date,
            }
        )
        job_2 = job_model.create(
            {
                "name": "Test",
                "state": "failed",
                "uuid": "2",
                "model_name": "nsca.server",
                "method_name": "_selection_encryption_method",
                "user_id": self.env.user.id,
                "date_created": date,
            }
        )
        job_3 = job_model.create(
            {
                "name": "Test",
                "state": "failed",
                "uuid": "2",
                "model_name": "nsca.server",
                "method_name": "_selection_encryption_method",
                "user_id": self.env.user.id,
            }
        )
        domain = [
            ("state", "!=", "done"),
            ("id", "in", [job_1.id, job_2.id, job_3.id]),
        ]
        result = self.env["queue.job"].cron_queue_status(
            domain, created_seconds=1, critical=2, warning=1
        )
        self.assertEqual(result[0], 2)
        job_1.write({"state": "done"})
        result = self.env["queue.job"].cron_queue_status(
            domain, created_seconds=1, critical=2, warning=1
        )
        self.assertEqual(result[0], 1)
        job_2.write({"state": "done"})
        result = self.env["queue.job"].cron_queue_status(
            domain, created_seconds=1, critical=1, warning=0
        )
        self.assertEqual(result[0], 0)
