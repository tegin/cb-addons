import setuptools

setuptools.setup(
    setup_requires=['setuptools-odoo'],
    odoo_addon={
        "depends_override": {
            "archive_management": "odoo14-addon-archive_management @ git+https://github.com/tegin/archive-management.git@14.0#subdirectory=setup/archive_management"
        }
    },
)
