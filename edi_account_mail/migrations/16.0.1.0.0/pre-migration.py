from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    env.ref("edi_account_mail.mail_exchange_type").rule_ids.unlink()
