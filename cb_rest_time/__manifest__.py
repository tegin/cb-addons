# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Cb Rest Time",
    "summary": """
        Añadir tiempo de descanso en los calendarios.""",
    "version": "11.0.1.0.0",
    "license": "AGPL-3",
    "author": "Creu Blanca",
    "website": "www.creublanca.es",
    "depends": ["hr_attendance"],
    "data": ["views/resource_calendar_attendance.xml"],
    "post_load": "post_load_hook",
}
