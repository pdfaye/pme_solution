# -*- coding:utf-8 -*-
from addons import hr
from odoo import api, fields, models


class PME(models.Model):
    _name = 'pme'
    _description = "la liste des PME"

    name = fields.Char('Name', required=True)
    code = fields.Char('Code')
    localisation = fields.Char('Localisation')
    domaine = fields.Char('Domaine activité')
    contact_whatsapp = fields.Char('Whatsapp')
    contact_mail = fields.Char('Email:')
    contact_fix = fields.Char('Téléphone fixe')
    site_web = fields.Char('Le site web du l\'entreprise')
    description = fields.Html('Qui sommes nous?', help="Une petite description de l\'entreprise")
    service_offerts = fields.One2many('service', 'pme_id', string='Service disponibles', )