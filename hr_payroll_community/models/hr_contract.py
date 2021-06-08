# -*- coding:utf-8 -*-
from datetime import datetime, timedelta

from odoo import api, fields, models


class HrContract(models.Model):
    """
    Employee contract based on the visa, work permits
    allows to configure different Salary structure
    """
    _inherit = 'hr.contract'
    _description = 'Employee Contract'

    struct_id = fields.Many2one('hr.payroll.structure', string='Salary Structure')
    schedule_pay = fields.Selection([
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('semi-annually', 'Semi-annually'),
        ('annually', 'Annually'),
        ('weekly', 'Weekly'),
        ('bi-weekly', 'Bi-weekly'),
        ('bi-monthly', 'Bi-monthly'),
    ], string='Scheduled Pay', index=True, default='monthly',
        help="Defines the frequency of the wage payment.")
    resource_calendar_id = fields.Many2one(required=True, help="Employee's working schedule.")
    hra = fields.Monetary(string='HRA', tracking=True, help="Allocation de loyer.")
    travel_allowance = fields.Monetary(string="Travel Allowance", help="Travel allowance")
    da = fields.Monetary(string="DA", help="Dearness allowance")
    meal_allowance = fields.Monetary(string="Meal Allowance", help="Indemnité de repas")
    medical_allowance = fields.Monetary(string="Medical Allowance", help="Allocation Medical")
    other_allowance = fields.Monetary(string="Other Allowance", help="Other allowances")
    type_cotisation_fiscal = fields.Selection([
        ('ipm', 'IPM'),
        ('ipres', 'IPRES'),
        ('css', 'CSS'), ], string='Cotisation fiscal', help="Defines the frequency of the wage payment.")
    type_contract = fields.Selection([
        ('cdd', 'CDD'),
        ('cdi', 'CDI'),
        ('cee', 'contrat d\'engagement à l\'essai'),
        ('stage', 'contrat de stage'),
    ], string='Type de contract', default='cdd',
        help="Cette attribut définit le type de contrat de l\'employé.")

    type_regime = fields.Selection([
                                    ('rg', 'Régime Général'),
                                    ('rc', 'Régime Cadre'),
                                ], string='Type de contract', default='rg',
                                    help="Le type de régime de l\'employé.")
    duree_contract = fields.Text(string='Durée du contract',
                                 help="Cette attribut définit la durée du contrat de l\'employé.")

    sursalaire = fields.Monetary(string='Sursalaire')
    heure_sup = fields.Monetary(string='Heures supplémentaire')
    abattement_fiscal = fields.Monetary(string='Abattement fical', help='Il représente 30% du salaire brut social et '
                                                                        'est plafonné à 75 000 CFA/mois',
                                        compute='compute_abattement_fiscal')

    @api.onchange('wage')
    def compute_abattement_fiscal(self):
        self.abattement_fiscal = self.wage * float(0.30)
    salaire_net = fields.Monetary(string='Salaire net')

    @api.onchange('wage')
    def compute_salaire_brut_fiscal(self):
        self.salaire_net = self.salaire_brut_social - (self.ipm + self.ipres + self.css)

    salaire_net_a_payer = fields.Monetary(string='Salaire net à payer')

    @api.onchange('wage')
    def compute_salaire_brut_fiscal(self):
        self.salaire_net_a_payer = self.salaire_net + self.pcrf

    salaire_brut_fiscal = fields.Monetary(string='Salaire brut fical')

    salaire_brut_social = fields.Monetary(string='Salaire brut social')

    @api.onchange('wage')
    def compute_salaire_brut_fiscal(self):
        self.salaire_brut_fiscal = self.salaire_brut_social - self.abattement_fiscal

    @api.onchange('wage')
    def compute_salaire_brut_social(self):
        self.salaire_brut_social = (self.wage + self.sursalaire + self.prime_enciennete + self.heure_sup + self.pcs) - \
                                   self.retenue_abscence_non_justifiee

    ipm = fields.Monetary(string='cotisation IPM', compute='compute_ipm')

    @api.onchange('wage')
    def compute_ipm(self):
        self.ipm = self.salaire_brut_social * float(0.075)

    ipres = fields.Monetary(string='cotisation IPRES')

    @api.onchange('wage', 'type_regime')
    def compute_ipres(self):
        if self.type_regime == 'rg':
            self.ipres = self.salaire_brut_social * float(0.056)
        elif self.type_regime == 'rc':
            self.ipres = self.salaire_brut_social * float(0.56) + self.salaire_brut_social * float(0.024)

    css = fields.Monetary(string='cotisation CSS', help='Caisse de sécurité Social')

    @api.onchange('wage')
    def compute_css(self):
        self.css = self.salaire_brut_social * float(0.07)

    cotisation_fiscal = fields.Monetary(string='Montant Cotisation Fiscal', compute='compute_cotistaion_fiscal')

    @api.onchange('wage')
    def compute_prime_enciennete(self):
        self.cotisation_fiscal = self.salaire_brut_fiscal * float(0.03)
    type_cotisation_social = fields.Selection([
        ('cfce', 'CFCE(Contribution forfataire à la charge de l\'employeur)'),
        ('trimf', 'TRIMF(Taxe Reprèsentative du Minimum Fiscal)'),
        ('ir', 'IR(L\'Impot sur le Revenu)'), ], string='Cotisation Social',
        help="Defines the frequency of the wage payment.")
    cotisation_social = fields.Monetary(string='Montant Cotisation Social')
    indemnite_transport = fields.Monetary(string='Indemnité de transport imposable')
    retenue_assurance_maladie = fields.Monetary(string='Ressources Assurance maladie')
    retenue_abscence_non_justifiee = fields.Monetary(string='Retenue pour abscence non jutifiée')
    taux_horaire = fields.Monetary(string='Taux horaire')
    nombre_part = fields.Integer(string='Nombre de part')
    numero_cnps = fields.Integer(string='Numéro cnps')
    pcs = fields.Monetary(string='PRIME A CARACTERES DE SALAIRE')
    enciennete = fields.Integer('Encienneté', compute='get_enciennete')

    @api.onchange('date_start')
    def get_enciennete(self):
        if self.date_start is not False:
            self.enciennete = (datetime.today().date() - datetime.strptime(str(self.date_start),
                                                                    '%Y-%m-%d').date()) // timedelta(days=365)

    prime_enciennete = fields.Monetary(string='PRIME ENCIENNETE', help="""Ce prime vari en fonction 
                                            des années et commance aprés deux années dans l'entrprise. Au premier moi de 
                                            la troisieme année on reçoi 2% de 
                                            la salaire de base et est incrémenté de 1% chaque année""",
                                       compute='compute_prime_enciennete')
    pcrf = fields.Monetary(string='PRIME A CARACTERES DE REMBOURESSEMENT DE FRAIS', help="""Ce prime est versé par l'employeur au
                                employé pour le rempbouressement des frais fait par l'employé au profil de l'entreprise""",
                                       compute='compute_prime_enciennete')

    @api.onchange('wage')
    def compute_prime_enciennete(self):
        self.prime_enciennete = self.wage * float(0.01)

    @api.onchange('wage')
    def compute_cotistaion_fiscal(self):
        self.cotisation_fiscal = self.wage * float(0.024)

    salaire_brut = fields.Monetary('Salaire brut')

    @api.onchange('prime_enciennete', 'cotisation_fiscal')
    def get_salaire_brut(self):
        self.salaire_brut = self.cotisation_fiscal + self.prime_enciennete

    def get_all_structures(self):
        """
        @return: the structures linked to the given contracts, ordered by hierachy (parent=False first,
                 then first level children and so on) and without duplicata
        """
        structures = self.mapped('struct_id')
        if not structures:
            return []
        # YTI TODO return browse records
        return list(set(structures._get_parent_structure().ids))

    def get_attribute(self, code, attribute):
        return self.env['hr.contract.advantage.template'].search([('code', '=', code)], limit=1)[attribute]

    def set_attribute_value(self, code, active):
        for contract in self:
            if active:
                value = self.env['hr.contract.advantage.template'].search([('code', '=', code)], limit=1).default_value
                contract[code] = value
            else:
                contract[code] = 0.0


class HrContractAdvandageTemplate(models.Model):
    _name = 'hr.contract.advantage.template'
    _description = "Employee's Advantage on Contract"

    name = fields.Char('Name', required=True)
    code = fields.Char('Code', required=True)
    lower_bound = fields.Float('Lower Bound', help="Lower bound authorized by the employer for this advantage")
    upper_bound = fields.Float('Upper Bound', help="Upper bound authorized by the employer for this advantage")
    default_value = fields.Float('Default value for this advantage')
