# -*- coding:utf-8 -*-
from addons import hr
from odoo import api, fields, models


class PME(models.Model):
    _name = 'cabinet'
    _description = "la liste des Cabinet"

    name = fields.Char('Name', required=True)
    code = fields.Char('Code')
    type = fields.Selection([
        ('comptable', 'comptable'),
        ('fiscalite', 'Fiscalité'),
        ('formation', 'Formation'),
        ('conseil', 'Conseil'),
        ('conseil', 'Autre'), ], string='Type de cabinet')

    localisation = fields.Char('Localisation')
    domaine = fields.Char('Domaine activité')
    contact = fields.Char('Les contacts')
    site_web = fields.Char('Le site web du cabinet')
    description = fields.Html('Qui sommes nous?', help="Une petite description du cabinet")
    service_offerts = fields.One2many('service', 'cabinet_id', string='Service disponibles', )


class Service(models.Model):
    _name = 'service'
    _description = 'La liste des services offerts'

    nom = fields.Char('Service')
    description = fields.Char('Description')
    cabinet_id = fields.Many2one('cabinet', invisible=1)
    pme_id = fields.Many2one('pme', invisible=1)