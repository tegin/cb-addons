# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json
from lxml import etree
from odoo.osv.orm import setup_modifiers
from odoo import api, models, _
from odoo.exceptions import UserError


class Base(models.AbstractModel):
    _inherit = 'base'

    @api.model
    def _get_quick_access_buttons(self, rules):
        result = []
        for rule in rules:
            result.append(etree.Element(
                'button', attrib={
                    'name': 'action_print_document_label',
                    'type': 'object',
                    'class': 'oe_stat_button',
                    'context': json.dumps({
                        'rule_id': rule.id,
                        'label_id': rule.label_id.id,
                    }),
                    'attrs': rule._get_button_attrs(),
                    'string': rule.label_name or rule.label_id.name,
                    'icon': rule.icon or 'fa-print'
                }
            ))
        return result

    def _get_document_quick_access_label_printer(self):
        behaviour = self.remote.with_context(
            printer_usage='label'
        ).get_printer_behaviour()
        if 'printer' in behaviour:
            return behaviour.pop('printer')
        if self.env.user.printing_printer_id:
            return self.env.user.printing_printer_id
        raise UserError(_('Printer function not defined'))

    def action_print_document_label(self):
        label = self.env['printing.label.zpl2'].browse(
            self.env.context.get('label_id'))
        self._get_document_quick_access_label_printer().print_document(
            report=self.env['ir.actions.report'],
            content=label._generate_zpl2_data(self),
            doc_format='txt'
        )
        return True

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):
        res = super().fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu)
        rules = self.env['document.quick.access.rule'].search([
            ('model_id.model', '=', self._name),
            ('label_id', '!=', False)
        ])
        if rules and view_type == 'form':
            doc = etree.XML(res['arch'])
            nodes = doc.xpath("//form/sheet/div[@name='button_box']")
            if nodes:
                node = nodes[0]
            else:
                sheet = doc.xpath('//sheet')
                if sheet:
                    node = etree.Element(
                        'div',
                        attrib={
                            'name': 'button_box',
                            'class': 'oe_button_box'
                        }
                    )
                    sheet[0].insert(0, node)
                else:
                    node = None
            if node is not None:
                buttons = self._get_quick_access_buttons(rules)
                for button in buttons:
                    setup_modifiers(button)
                    node.append(button)
            res['arch'] = etree.tostring(doc, encoding='unicode')
        return res
