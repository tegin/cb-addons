# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "HR Org Chart",
    "category": "Hidden",
    "version": "11.0.1.0.0",
    "license": "AGPL-3",
    "author": "Creu Blanca",
    "summary": """Departments Chart
    """,
    "depends": ["hr"],
    "data": ["views/hr_templates.xml", "views/hr_views.xml"],
    "qweb": ["static/src/xml/hr_department_chart.xml"],
}
