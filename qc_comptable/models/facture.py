# -*- coding: utf-8 -*-

from odoo import models, fields, api, SUPERUSER_ID


class qc_submission(models.Model):
    _name = 'qc_comptable.soumission'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'utm.mixin', 'format.address.mixin']

    name = fields.Char('Soumission', tracking=True)
    submit_on = fields.Date('Soumis le:', tracking=True)
    submit_by = fields.Many2one('res.partner', string='Soumis par', tracking=True)
#    fichier = fields.Binary(string="Batch", attachment=True, tracking=True,)
    stage = fields.Selection([('Traitement en cours','Traitement en cours'),('Traitement terminé','Traitement terminé'),('Fichier invalidé','Fichier invalidé')], string="Etape", group_expand='_read_group_stage_ids', default='Traitement en cours')
    user_id = fields.Many2one('res.users', string='Agent traitant', index=True, tracking=True, required=True,
                              default=lambda self: self.env.user)
    note = fields.Text('Note')

    def upload_valid(self):
        self.stage = 'Traitement terminé'

    def upload_reject(self):
        self.stage = 'Fichier invalidé'

    def _read_group_stage_ids(self, stages, domain, order):
        return [key for key, val in type(self).stage.selection]



class qc_facture(models.Model):
    _name = 'qc_comptable.facture'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'utm.mixin', 'format.address.mixin']

    name = fields.Char('Reference')
    date_facture = fields.Date('Date Facture', tracking=True)
    total_facture = fields.Float('Montant Total Facture', tracking=True)
    article_ids = fields.One2many('qc_comptable.article', 'facture_id', string='Article')
    stage = fields.Selection(
        [('Traitement à faire', 'Traitement à faire'), ('Traitement en cours', 'Traitement en cours'),
         ('Traitement terminé', 'Traitement terminé')], string="Etape", group_expand='_read_group_stage_ids',
        default='Traitement à faire')
    user_id = fields.Many2one('res.users', string='Agent traitant', index=True, tracking=True, required=True,
                              default=lambda self: self.env.user)
    partner_id = fields.Many2one('res.partner', string="Partenaire")
    attachment_ids = fields.One2many('ir.attachment', compute='_compute_attachment_ids', string="Main Attachments",
                                     help="Attachment that don't come from message.")

    def _compute_attachment_ids(self):
        for facture in self:
            attachment_ids = self.env['ir.attachment'].search([('res_id', '=', facture.id), ('res_model', '=', 'qc_comptable.fature')]).ids
            message_attachment_ids = facture.mapped('message_ids.attachment_ids').ids  # from mail_thread
            facture.attachment_ids = [(6, 0, list(set(attachment_ids) - set(message_attachment_ids)))]

    def upload_get(self):
        self.stage = 'Traitement en cours'

    def upload_reviewed(self):
        self.stage = 'Traitement terminé'

    def upload_cancel(self):
        self.stage = 'Traitement en cours'

    def _read_group_stage_ids(self, stages, domain, order):
        return [key for key, val in type(self).stage.selection]


class qc_line(models.Model):
    _name = 'qc_comptable.article'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'utm.mixin', 'format.address.mixin']

    name = fields.Char('Article', tracking=True)
    qty = fields.Float('Quantite', tracking=True)
    prix_unitaire_ht = fields.Float('Prix unitaire', tracking=True)
    prix_total_ht = fields.Float('Prix total HT', tracking=True)
    tva = fields.Float('TVA (%)')
    prix_ttc = fields.Float('Prix total TTC', tracking=True)
    description = fields.Text('Description')
    facture_id = fields.Many2one('qc_comptable.facture', tracking=True)

