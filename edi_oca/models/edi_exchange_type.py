# Copyright 2020 ACSONE SA
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models

from odoo.addons.http_routing.models.ir_http import slugify


class EDIExchangeType(models.Model):
    """
    Define a kind of exchange.
    """

    _name = "edi.exchange.type"
    _description = "EDI Exchange Type"

    backend_id = fields.Many2one(
        string="EDI backend",
        comodel_name="edi.backend",
        required=True,
        ondelete="cascade",
    )
    name = fields.Char(required=True)
    code = fields.Char(required=True)
    direction = fields.Selection(
        selection=[("input", "Input"), ("output", "Output")], required=True
    )
    exchange_filename_pattern = fields.Char(default="{record_name}-{type.code}-{dt}")
    exchange_file_ext = fields.Char(required=True)

    ack_needed = fields.Boolean()
    ack_name = fields.Char()
    ack_code = fields.Char()
    ack_filename_pattern = fields.Char(default="{type.exchange_filename_pattern}.ack")
    ack_file_ext = fields.Char(default="")

    def _make_exchange_filename(self, record, ack=False):
        """Generate filename."""
        pattern = self.exchange_filename_pattern
        ext = self.exchange_file_ext
        if ack:
            pattern = self.ack_filename_pattern
            ext = self.ack_file_ext
        pattern = pattern + ".{ext}"
        dt = slugify(fields.Datetime.to_string(fields.Datetime.now()))
        record_name = self._get_record_name(record)
        return pattern.format(
            exchange_record=record,
            record=record.record,
            record_name=record_name,
            type=self,
            dt=dt,
            ext=ext,
        )

    def _get_record_name(self, record):
        if hasattr(record.record, "_get_edi_exchange_record_name"):
            return record.record._get_edi_exchange_record_name(record, self)
        return slugify(record.record.name)

    _sql_constraints = [
        (
            "code_uniq",
            "unique(code, backend_id)",
            "The code must be unique per backend",
        )
    ]
