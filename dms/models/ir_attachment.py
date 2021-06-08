# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import api, models
import collections
import logging
import mimetypes
import os.path

from odoo import models, api

_logger = logging.getLogger(__name__)

class IrAttachment(models.Model):

    _inherit = "ir.attachment"

    @api.model
    def get_binary_extension(self, model, ids, binary_field,
                             filename_field=None):
        result = {}
        ids_to_browse = ids if isinstance(ids, collections.Iterable) else [ids]

        # First pass: load fields in bin_size mode to avoid loading big files
        #  unnecessarily.
        if filename_field:
            for this in self.env[model].with_context(
                    bin_size=True).browse(ids_to_browse):
                if not this.id:
                    result[this.id] = False
                    continue
                extension = ''
                if this[filename_field]:
                    filename, extension = os.path.splitext(
                        this[filename_field])
                if this[binary_field] and extension:
                    result[this.id] = extension
                    _logger.debug('Got extension %s from filename %s',
                                  extension, this[filename_field])
        # Second pass for all attachments which have to be loaded fully
        #  to get the extension from the content
        ids_to_browse = [_id for _id in ids_to_browse if _id not in result]
        for this in self.env[model].with_context(
                bin_size=True).browse(ids_to_browse):
            if not this[binary_field]:
                result[this.id] = False
                continue
            try:
                import magic
                if model == self._name and binary_field == 'datas' \
                        and this.store_fname:
                    mimetype = magic.from_file(
                        this._full_path(this.store_fname), mime=True)
                    _logger.debug('Magic determined mimetype %s from file %s',
                                  mimetype, this.store_fname)
                else:
                    mimetype = magic.from_buffer(
                        this[binary_field], mime=True)
                    _logger.debug('Magic determined mimetype %s from buffer',
                                  mimetype)
            except ImportError:
                (mimetype, encoding) = mimetypes.guess_type(
                    'data:;base64,' + this[binary_field], strict=False)
                _logger.debug('Mimetypes guessed type %s from buffer',
                              mimetype)
            extension = mimetypes.guess_extension(
                mimetype.split(';')[0], strict=False)
            result[this.id] = extension
        for _id in result:
            result[_id] = (result[_id] or '').lstrip('.').lower()
        return result if isinstance(ids, collections.Iterable) else result[ids]

    @api.model
    def get_attachment_extension(self, ids):
        return self.get_binary_extension(
            self._name, ids, 'datas', 'datas_fname')
    def _get_dms_directories(self, res_model, res_id):
        return self.env["dms.directory"].search(
            [("res_model", "=", res_model), ("res_id", "=", res_id)]
        )

    def _dms_directories_create(self):
        items = self._get_dms_directories(self.res_model, False)
        for item in items:
            model_item = self.env[self.res_model].sudo().browse(self.res_id)
            ir_model_item = self.env["ir.model"].search(
                [("model", "=", self.res_model)]
            )
            self.env["dms.directory"].create(
                {
                    "name": model_item.display_name,
                    "model_id": ir_model_item.id,
                    "res_model": self.res_model,
                    "res_id": self.res_id,
                    "parent_id": item.id,
                    "storage_id": item.storage_id.id,
                }
            )

    def _dms_operations(self):
        for attachment in self:
            if not attachment.res_model or not attachment.res_id:
                continue
            directories = self._get_dms_directories(
                attachment.res_model, attachment.res_id
            )
            if not directories:
                attachment._dms_directories_create()
                # Get dms_directories again (with items previously created)
                directories = self._get_dms_directories(
                    attachment.res_model, attachment.res_id
                )
            # Auto-create_files
            for directory in directories:
                self.env["dms.file"].create(
                    {
                        "name": attachment.name,
                        "directory_id": directory.id,
                        "attachment_id": attachment.id,
                        "res_model": attachment.res_model,
                        "res_id": attachment.res_id,
                    }
                )

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        if not self.env.context.get("dms_file"):
            records._dms_operations()
        return records

