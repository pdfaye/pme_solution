# -*- coding:utf-8 -*-

from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    _description = 'Employee'

    slip_ids = fields.One2many('hr.payslip', 'employee_id', string='Payslips', readonly=True, help="payslip")
    payslip_count = fields.Integer(compute='_compute_payslip_count', string='Payslip Count')

    def _compute_payslip_count(self):
        payslip_data = self.env['hr.payslip'].sudo().read_group([('employee_id', 'in', self.ids)],
                                                                  ['employee_id'], ['employee_id'])
        result = dict((data['employee_id'][0], data['employee_id_count']) for data in payslip_data)
        for employee in self:
            employee.payslip_count = result.get(employee.id, 0)

    def _user_left_days(self):
        for employee in self:
            legal_leave = employee.company_id.legal_holidays_status_id
            values = legal_leave.get_days(employee.id)
            employee.leaves_taken = values.get("leaves_taken")
            employee.max_leaves = values.get("max_leaves")

    # social_parts = fields.Float(
    #     compute="_calculate_social_parts",
    #     method=True,
    #     string="Nombre de parts sociales",
    #     store=False,
    # )
    def _calculate_coefficient(self):
        for line in self:
            if line.marital == "married" and line.status_spouse == "non_salaried":
                coef = 2
            else:
                coef = 1
            line.coef = coef

    ipres_id = fields.Char("N° IPRES")
    css_id = fields.Char("N° Sécurité Sociale")
    ipm_id = fields.Char("N° IPM")
    cni_id = fields.Char("N° CNI")
    status_spouse = fields.Selection(
        (("salaried", "Salarié(e)"), ("non_salaried", "Non-salarié(e)")),
        string="Statut du/de la conjoint(e)",
        default="salaried",
    )
    coef = fields.Integer(
        compute="_calculate_coefficient",
        method=True,
        string="Coefficient de TRIMF",
        store=True,
    )
    matricule = fields.Char("Matricule", size=64)
    # max_leaves = fields.Float(
    #     compute="_user_left_days",
    #     string="Acquis",
    #     help="This value is given by the sum of all holidays requests with a positive value.",
    # )
    # leaves_taken = fields.Float(
    #     compute="_user_left_days",
    #     string="Pris",
    #     help="This value is given by the sum of all holidays requests with a negative value.",
    # )