# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from mock import patch
from odoo.tests.common import TransactionCase
from lxml import etree
import json


class TestQuickAccessLabel(TransactionCase):
    def setUp(self):
        super(TestQuickAccessLabel, self).setUp()
        name = "testing_remote_server"
        self.remote = self.env["res.remote"].search([("name", "=", name)])
        if not self.remote:
            self.remote = self.env["res.remote"].create(
                {"name": name, "ip": "127.0.0.1"}
            )

        self.server = self.env["printing.server"].create(
            {"name": "Server", "address": "localhost", "port": 631}
        )
        self.printer = self.env["printing.printer"].create(
            {
                "name": "Printer 1",
                "system_name": "P1",
                "server_id": self.server.id,
            }
        )
        self.env["res.remote.printer"].create(
            {
                "remote_id": self.remote.id,
                "printer_id": self.printer.id,
                "is_default": True,
            }
        )
        self.env["res.remote.printer"].create(
            {
                "remote_id": self.remote.id,
                "printer_id": self.printer.id,
                "is_default": True,
                "printer_usage": "label",
            }
        )
        self.model = self.browse_ref("base.model_res_partner")
        self.label = self.env["printing.label.zpl2"].create(
            {
                "name": "LABEL NAME",
                "model_id": self.model.id,
                "component_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "QR",
                            "component_type": "qr_code",
                            "data": "object.get_quick_access_code()",
                        },
                    )
                ],
            }
        )
        self.rule = self.env["document.quick.access.rule"].create(
            {"model_id": self.model.id, "name": "TEST PARTNER RULE"}
        )
        self.partner = self.env.user.partner_id

    def test_views_no_button(self):
        data = self.partner.fields_view_get()
        xml = etree.XML(data["arch"])
        buttons = xml.xpath(
            "//div[@name='button_box']/"
            "button[@name='action_print_document_label']"
        )
        self.assertFalse(
            any(
                json.loads(button.attrib["context"]).get("rule_id", False)
                == self.rule.id
                for button in buttons
            )
        )

    def test_views_button(self):
        self.rule.label_id = self.label
        data = self.partner.fields_view_get()
        xml = etree.XML(data["arch"])
        buttons = xml.xpath(
            "//div[@name='button_box']/"
            "button[@name='action_print_document_label']"
        )
        self.assertTrue(
            any(
                json.loads(button.attrib["context"]).get("rule_id", False)
                == self.rule.id
                for button in buttons
            )
        )

    def test_views_button_no_options(self):
        self.rule.label_id = self.label
        data = self.partner.fields_view_get()
        xml = etree.XML(data["arch"])
        buttons = xml.xpath(
            "//div[@name='button_box']/"
            "button[@name='action_print_document_label']"
        )
        final_button = False
        for button in buttons:
            if (
                json.loads(button.attrib["context"]).get("rule_id", False)
                == self.rule.id
            ):
                final_button = button
                break
        self.assertNotEqual(final_button, None)
        self.assertEqual(final_button.attrib["attrs"], "{}")
        self.assertEqual(final_button.attrib["string"], self.label.name)

    @patch(
        "odoo.addons.base_report_to_printer.models.printing_printer."
        "PrintingPrinter.print_file"
    )
    def test_printing(self, print_file_patch):
        self.rule.label_id = self.label
        data = self.partner.fields_view_get()
        xml = etree.XML(data["arch"])
        buttons = xml.xpath(
            "//div[@name='button_box']/"
            "button[@name='action_print_document_label']"
        )
        final_button = False
        for button in buttons:
            if (
                json.loads(button.attrib["context"]).get("rule_id", False)
                == self.rule.id
            ):
                final_button = button
                break
        context = json.loads(final_button.attrib["context"])
        with patch(
            "odoo.addons.base_remote.models.base.Base.remote", new=self.remote
        ):
            print_file_patch.assert_not_called()
            self.partner.with_context(**context).action_print_document_label()
            print_file_patch.assert_called()

    def test_views_button_options(self):
        self.rule.write(
            {
                "label_id": self.label.id,
                "label_attrs": "{'invisible': [('is_company', '=', False)]}",
                "label_name": "NEW LABEL NAME",
            }
        )
        data = self.partner.fields_view_get()
        xml = etree.XML(data["arch"])
        buttons = xml.xpath(
            "//div[@name='button_box']/"
            "button[@name='action_print_document_label']"
        )
        final_button = False
        for button in buttons:
            if (
                json.loads(button.attrib["context"]).get("rule_id", False)
                == self.rule.id
            ):
                final_button = button
                break
        self.assertNotEqual(final_button, None)
        self.assertNotEqual(final_button.attrib["attrs"], "{}")
        self.assertNotEqual(final_button.attrib["string"], self.label.name)
        self.assertEqual(final_button.attrib["attrs"], self.rule.label_attrs)
        self.assertEqual(final_button.attrib["string"], self.rule.label_name)
