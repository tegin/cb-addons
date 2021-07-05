import setuptools

setuptools.setup(
    setup_requires=['setuptools-odoo'],
    odoo_addon={
        "depends_override": {
            "pos_session_pay_invoice": "git+https://github.com/OCA/pos.git@refs/pull/674/merge#subdirectory=setup/pos_session_pay_invoice"
        }
    },
)
