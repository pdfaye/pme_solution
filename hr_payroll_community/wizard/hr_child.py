# -*- coding: utf-8 -*-

from odoo import fields, models


class Enfant(models.TransientModel):
    _name = 'hr.children'
    _description = 'Children employee'

    nom = fields.Char(string='Nom et prénom')
    date_naissance = fields.Date(string='Date de naissance')
    age = fields.Integer(string='Age')

    def to_add_child(self):
        data = {}
        data['nom'] = self.nom
        data['date_naissance'] = self.date_naissance
        data['age'] = self.age

    def wizard_children(self):
        return {
            'name': "Enfant en charge",
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'hr.children',
            'view_id': self.env.ref('children').id,
            'target': '_blank'
        }
