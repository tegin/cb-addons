import setuptools

setuptools.setup(
    setup_requires=['setuptools-odoo'],
    odoo_addon={
        "depends_override": {
            "multicompany_property_account": "git+https://github.com/forgeflow/multicompany-fixes.git@14.0#subdirectory=setup/multicompany_property_account",
            "multicompany_property_product": "git+https://github.com/forgeflow/multicompany-fixes.git@14.0#subdirectory=setup/multicompany_property_product",
            "multicompany_property_base": "git+https://github.com/forgeflow/multicompany-fixes.git@14.0#subdirectory=setup/multicompany_property_base"
        }
    },
)
