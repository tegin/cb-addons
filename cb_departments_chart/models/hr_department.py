# Part of Odoo. See LICENSE file for full copyright and licensing details.
import base64
from odoo import api, fields, models
from odoo import tools
from odoo.modules.module import get_module_resource


class Department(models.Model):
    _name = "hr.department"
    _inherit = "hr.department"

    child_all_count = fields.Integer(
        'Indirect Surbordinates Count',
        compute='_compute_child_all_count', store=False)

    @api.model
    def _default_image(self):
        image_path = get_module_resource('hr',
                                         'static/src/img',
                                         'default_image.png')
        return tools.image_resize_image_big(
            base64.b64encode(open(image_path, 'rb').read()))

    image = fields.Binary(
        "Photo", attachment=True,
        default=_default_image,
        help="This field holds the image used as photo for the department,"
             " limited to 1024x1024px.")
    image_medium = fields.Binary(
        "Medium-sized photo", attachment=True,
        compute='_compute_image_medium',
        help="Medium-sized photo of the employee. It is automatically "
             "resized as a 128x128px image, with aspect ratio preserved. "
             "Use this field in form views or some kanban views.",
        store=True
    )

    @api.depends('child_ids.child_all_count')
    def _compute_child_all_count(self):
        for department in self:
            department.child_all_count = len(
                department.child_ids) + sum(
                child.child_all_count for child in department.child_ids)

    @api.depends('image')
    def _compute_image_medium(self):
        for record in self:
            record.image_medium = tools.image_resize_image_medium(
                record.image)
