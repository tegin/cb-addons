# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import os
import shutil
from odoo import api, models
from odoo.addons.queue_job.job import job
from odoo.modules.registry import Registry
import time


class HashSearch(models.Model):
    _inherit = 'hash.search'

    @api.model
    def cron_move_documents(self, limit=False, path=False):
        if not path:
            path = self.env['ir.config_parameter'].sudo().get_param(
                'hash_search_document_scanner_queue.preprocess_path',
                default=False)
        dest_path = self.env['ir.config_parameter'].sudo().get_param(
            'hash_search_document_scanner.path', default=False)
        if not path or not dest_path:
            return False
        elements = [os.path.join(
            path, f
        ) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
        if limit:
            elements = elements[:limit]
        min_time = int(time.time()) - 60
        for element in elements:
            if os.path.getmtime(element) > min_time:
                continue
            filename = os.path.basename(element)
            new_element = os.path.join(dest_path, filename)
            shutil.copy(element, new_element)
            new_cr = Registry(self.env.cr.dbname).cursor()
            try:
                env = api.Environment(new_cr, self.env.uid, self.env.context)
                env[self._name].browse().with_delay().process_document(
                    new_element)
                new_cr.commit()
            except Exception:
                os.unlink(new_element)
                new_cr.rollback()  # error, rollback everything atomically
                raise
            finally:
                new_cr.close()
            os.unlink(element)
        return True

    @api.model
    @job(default_channel='root.scanner')
    def process_document(self, element):
        return super().process_document(element)
