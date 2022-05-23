# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    integration_field_name = openupgrade.get_legacy_name(
        "account_move_integration_id"
    )
    if not openupgrade.table_exists(env.cr, "account_move_integration"):
        return
    if not openupgrade.table_exists(env.cr, "account_move_integration_method"):
        return
    if not openupgrade.column_exists(
        env.cr, "edi_exchange_record", integration_field_name
    ):
        openupgrade.logged_query(
            env.cr,
            """
                    ALTER TABLE edi_exchange_record
                    ADD COLUMN %s numeric"""
            % integration_field_name,
        )
    openupgrade.logged_query(
        env.cr,
        "SELECT id from account_move_integration_method where code = 'storage'",
    )
    data = env.cr.fetchall()
    if not data:
        return
    method_id = data[0][0]
    backend_type = env.ref("edi_account_storage.backend_type")

    openupgrade.logged_query(
        env.cr,
        """
        SELECT
            rp.id,
            rp.account_integration_report_id,
            rp.account_integration_storage_id,
            rp.account_integration_filename_pattern
        FROM res_partner rp, account_move_integration_method_res_partner_rel amimrpr
        WHERE rp.l10n_es_facturae_sending_code is NULL
            AND amimrpr.res_partner_id = rp.id
            AND amimrpr.account_move_integration_method_id = {method_id}
        """.format(
            method_id=method_id
        ),
    )
    for x in env.cr.fetchall():
        partner = env["res.partner"].browse(x[0])
        backend = env["edi.backend"].create(
            {
                "name": "EDI backend for %s" % partner.name,
                "backend_type_id": backend_type.id,
                "storage_id": x[2],
            }
        )

        exchange_type = env["edi.exchange.type"].create(
            {
                "name": "Storage Invoice Exchange type for %s" % partner.name,
                "backend_type_id": backend_type.id,
                "backend_id": backend.id,
                "code": "edi_account_storage_partner_%s" % partner.id,
                "direction": "output",
                "exchange_filename_pattern": x[3].replace(
                    "{invoice", "{record"
                ),
                "model_ids": [(4, env.ref("account.model_account_move").id)],
                "enable_snippet": "result = not record."
                "_has_exchange_record(exchange_type.code)",
            }
        )
        exchange_type.write(
            {
                "enable_domain": "[('state', '!=', 'draft'), ('partner_id."
                "account_invoice_storage_exchange_type_id'"
                ", '=', %s)]" % exchange_type.id,
            }
        )
        env["edi.exchange.template.output"].create(
            {
                "name": "Storage backend for %s" % partner.name,
                "backend_type_id": backend_type.id,
                "backend_id": backend.id,
                "type_id": exchange_type.id,
                "code": "edi_account_storage_partner_template_%s" % partner.id,
                "output_type": "pdf",
                "generator": "report",
                "report_id": x[1],
            }
        )
        partner.account_invoice_storage_exchange_type_id = exchange_type
        partner.flush()
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO edi_exchange_record (
            {integration_field},
            edi_exchange_state,
            identifier,
            external_identifier,
            type_id,
            backend_id,
            exchange_filename,
            create_date,
            create_uid,
            write_date,
            write_uid,
            model,
            res_id,
            exchanged_on,
            l10n_es_facturae_status,
            l10n_es_facturae_cancellation_status,
            l10n_es_facturae_motive,
            l10n_es_facturae_cancellation_motive
        ) SELECT
            ami.id,
            CASE WHEN ami.state in ('sent', 'cancelled') THEN 'output_sent'
                WHEN ami.state = 'pending' THEN 'output_pending'
                ELSE 'output_error_on_send'
            END,
            ami.name,
            ami.register_number,
            eet.id,
            eet.backend_id,
            ia.name,
            ami.create_date,
            ami.create_uid,
            ami.write_date,
            ami.write_uid,
            'account.move',
            ami.move_id,
            case when ami.state = 'sent' then COALESCE(ami.update_date, ami.write_date)
            END,
            ami.integration_status,
            ami.cancellation_status,
            ami.integration_description,
            ami.cancellation_description
        FROM account_move_integration ami
            LEFT JOIN ir_attachment ia ON ia.id = ami.attachment_id
            LEFT JOIN account_move am ON am.id = ami.move_id
            LEFT JOIN res_partner rp ON rp.id = am.partner_id
            LEFT JOIN edi_exchange_type eet ON eet.id =
                rp.account_invoice_storage_exchange_type_id
        WHERE ami.method_id = {method_id}""".format(
            integration_field=integration_field_name,
            method_id=method_id,
        ),
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE ir_attachment at
        SET res_model = 'edi.exchange.record', res_id = eer.id,
            res_field = 'exchange_file'
        FROM account_move_integration aii
            INNER JOIN edi_exchange_record eer on eer.{integration_field} = aii.id
        WHERE aii.attachment_id = at.id and aii.method_id = {method_id}
        """.format(
            integration_field=integration_field_name,
            method_id=method_id,
        ),
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE ir_attachment at
        SET res_model = 'edi.exchange.record', res_id = eer.id
        FROM account_invoice_integration_ir_attachment_rel aiiia
            INNER JOIN account_move_integration aii
                ON aii.id = aiiia.account_invoice_integration_id
            INNER JOIN edi_exchange_record eer
                ON eer.{integration_field} = aii.id
        WHERE aiiia.ir_attachment_id = at.id
        """.format(
            integration_field=integration_field_name,
        ),
    )
