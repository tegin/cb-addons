# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import os
import base64
import mimetypes
import shutil
from odoo import api, models
import logging
_logger = logging.getLogger(__name__)
try:
    from pyzbar.pyzbar import decode, ZBarSymbol
    import pdf2image
    from pdf2image.exceptions import (
        PDFInfoNotInstalledError,
        PDFPageCountError,
        PDFSyntaxError
    )
except (ImportError, IOError) as err:
    _logger.debug(err)


class OCRException(Exception):
    def __init__(self, name):
        self.name = name


class HashSearch(models.Model):
    _inherit = 'hash.search'

    @api.model
    def cron_attach_documents(self, limit=False, path=False):
        if not path:
            path = self.env['ir.config_parameter'].sudo().get_param(
                'hash_search_document_attacher.path', default=False)
        if not path:
            return False
        elements = [os.path.join(
            path, f
        ) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
        if limit:
            elements = elements[:limit]
        for element in elements:
            try:
                self.process_document(element)
            except OCRException:
                _logger.warning('Element %s was corrupted' % element)
                os.unlink(element)
        return True

    @api.model
    def process_document(self, element):
        result = self._search_document(element)
        return self._postprocess_document(element, result)

    def _attach_document(self, filename, datas):
        self.env['ir.attachment'].create({
            'name': filename,
            'datas': datas,
            'datas_fname': filename,
            'res_model': self.model,
            'res_id': self.res_id,
            'mimetype': mimetypes.guess_type(filename)
        })

    @api.model
    def _postprocess_document(self, path, results):
        filename = os.path.basename(path)
        datas = base64.b64encode(open(path, 'rb').read())
        if results:
            for result in results:
                result._attach_document(filename, datas)
            new_path = self.env['ir.config_parameter'].sudo().get_param(
                'hash_search_document_attacher.ok_path', default=False)
        else:
            new_path = self.env['ir.config_parameter'].sudo().get_param(
                'hash_search_document_attacher.failure_path', default=False)
            self.env['hash.missing.document'].create({
                'name': filename,
                'data': datas,
            })
        if new_path:
            shutil.copy(path, os.path.join(new_path, filename))
        os.unlink(path)
        return bool(results)

    @api.model
    def _search_document_pdf(self, path):
        hashes = self.env['hash.search']
        try:
            images = pdf2image.convert_from_bytes(
                open(path, 'rb').read())
        except (
            PDFInfoNotInstalledError, PDFPageCountError, PDFSyntaxError
        ) as e:
            raise OCRException(str(e))
        for im in images:
            hashes |= self._search_pil_image(im)
        return hashes

    @api.model
    def _search_pil_image(self, image):
        results = decode(image, symbols=[ZBarSymbol.QRCODE])
        hashes = self.env['hash.search']
        for result in results:
            hashes |= self.search([
                ('name', '=', result.data.decode('utf-8'))], limit=1)
        return hashes

    @api.model
    def _search_document(self, path):
        filename, extension = os.path.splitext(path)
        if extension == '.pdf':
            return self._search_document_pdf(path)
        return self.env['hash.search']
