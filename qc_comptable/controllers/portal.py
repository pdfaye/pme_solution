# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import OrderedDict
from operator import itemgetter

from odoo import http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
import datetime
from datetime import date
from odoo.tools import groupby as groupbyelem
import base64

from odoo.osv.expression import OR


class CustomerPortal(CustomerPortal):


    def _prepare_portal_layout_values(self):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        values['batch_count'] = request.env['qc_comptable.soumission'].search_count([])
        values['facture_count'] = request.env['qc_comptable.facture'].search_count([])
        return values


    # ------------------------------------------------------------
    # My Batch
    # ------------------------------------------------------------
    def _facture_get_page_view_values(self, facture, access_token, **kwargs):
        values = {
            'page_name': 'Facture Envoyé',
            'facture': facture,
        }
        return self._get_page_view_values(facture, access_token, values, 'my_facture_history', False, **kwargs)


    @http.route(['/my/msa/accounting', '/my/msa/accounting/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_soumissions(self, page=1, date_begin=None, date_end=None, sortby=None, form_ref='', **kw):
        values = self._prepare_portal_layout_values()
        Batch = request.env['qc_comptable.soumission']
        domain = []

        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Name'), 'order': 'name'},
        }
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]
        # batch count
        batch_count = Batch.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/msa/accounting",
            url_args={'sortby': sortby},
            total=batch_count,
            page=page,
            step=self._items_per_page
        )

        # content according to pager and archive selected
        batchs = Batch.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_batch_history'] = batchs.ids[:100]

        values.update({
            'batchs': batchs,
            'page_name': 'MS Associates',
            'default_url': '/my/msa/accounting',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby
        })
        if form_ref == 'batch_submit':
            x = datetime.datetime.now()
            x = str(x)
            name = 'Soumis le' + x
            today = date.today()
            user = request.env.user
            if kw.get('attachment', False):
                Soumissions = request.env['qc_comptable.soumission']
                soumission_id = Soumissions.sudo().create({
                    'name': name,
                    'submit_on': today,
                    'submit_by': user.id,
                })
                Attachments = request.env['ir.attachment']
                name = kw.get('attachment').filename
                file = kw.get('attachment')
                attachment = file.read()
                attachment = base64.b64encode(attachment)
                attachment_id = Attachments.sudo().create({
                    'name': name,
                    'datas_fname': name,
                    'res_name': name,
                    'type': 'binary',
                    'res_model': 'qc_comptable.soumission',
                    'res_id': soumission_id,
                    'datas': attachment,
                })
            return request.redirect('/my/msa/accounting')
        return request.render("qc_comptable.portal_my_batchs", values)

    # ------------------------------------------------------------
    # Facture
    # ------------------------------------------------------------
    @http.route(['/my/msa/factures', '/my/msa/facture/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_factures(self, page=1, date_begin=None, date_end=None, sortby=None, form_ref='', **kw):
        values = self._prepare_portal_layout_values()
        Facture = request.env['qc_comptable.facture']
        domain = []

        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Name'), 'order': 'name'},
        }
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]
        # batch count
        facture_count = Facture.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/msa/factures",
            url_args={'sortby': sortby},
            total=facture_count,
            page=page,
            step=self._items_per_page
        )

        # content according to pager and archive selected
        factures = Facture.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_facture_history'] = factures.ids[:100]

        values.update({
            'factures': factures,
            'page_name': 'MS Associates',
            'default_url': '/my/msa/facture',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby
        })
        return request.render("qc_comptable.portal_my_factures", values)

    # ------------------------------------------------------------
    # Facture Specifique
    # ------------------------------------------------------------
    @http.route(['/my/msa/facture/<int:facture_id>'], type='http', auth="user", website=True)
    def portal_my_batch(self, facture_id=None, access_token=None, **kw):
        try:
            facture_sudo = self._document_check_access('qc_comptable.facture', facture_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        values = self._facture_get_page_view_values(facture_sudo, access_token, **kw)
        return request.render("qc_comptable.portal_my_facture", values)

"""
    # ------------------------------------------------------------
    # My Task
    # ------------------------------------------------------------
    def _task_get_page_view_values(self, task, access_token, **kwargs):
        values = {
            'page_name': 'task',
            'task': task,
            'user': request.env.user
        }
        return self._get_page_view_values(task, access_token, values, 'my_tasks_history', False, **kwargs)



    @http.route(['/my/tasks', '/my/tasks/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_tasks(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None, search_in='content', groupby='project', **kw):
        values = self._prepare_portal_layout_values()
        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Title'), 'order': 'name'},
            'stage': {'label': _('Stage'), 'order': 'stage_id'},
            'update': {'label': _('Last Stage Update'), 'order': 'date_last_stage_update desc'},
        }
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
        }
        searchbar_inputs = {
            'content': {'input': 'content', 'label': _('Search <span class="nolabel"> (in Content)</span>')},
            'message': {'input': 'message', 'label': _('Search in Messages')},
            'customer': {'input': 'customer', 'label': _('Search in Customer')},
            'stage': {'input': 'stage', 'label': _('Search in Stages')},
            'all': {'input': 'all', 'label': _('Search in All')},
        }
        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
            'project': {'input': 'project', 'label': _('Project')},
        }

        # extends filterby criteria with project the customer has access to
        projects = request.env['project.project'].search([])
        for project in projects:
            searchbar_filters.update({
                str(project.id): {'label': project.name, 'domain': [('project_id', '=', project.id)]}
            })

        # extends filterby criteria with project (criteria name is the project id)
        # Note: portal users can't view projects they don't follow
        project_groups = request.env['project.task'].read_group([('project_id', 'not in', projects.ids)],
                                                                ['project_id'], ['project_id'])
        for group in project_groups:
            proj_id = group['project_id'][0] if group['project_id'] else False
            proj_name = group['project_id'][1] if group['project_id'] else _('Others')
            searchbar_filters.update({
                str(proj_id): {'label': proj_name, 'domain': [('project_id', '=', proj_id)]}
            })

        # default sort by value
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']
        # default filter by value
        if not filterby:
            filterby = 'all'
        domain = searchbar_filters[filterby]['domain']

        # archive groups - Default Group By 'create_date'
        archive_groups = self._get_archive_groups('project.task', domain)
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # search
        if search and search_in:
            search_domain = []
            if search_in in ('content', 'all'):
                search_domain = OR([search_domain, ['|', ('name', 'ilike', search), ('description', 'ilike', search)]])
            if search_in in ('customer', 'all'):
                search_domain = OR([search_domain, [('partner_id', 'ilike', search)]])
            if search_in in ('message', 'all'):
                search_domain = OR([search_domain, [('message_ids.body', 'ilike', search)]])
            if search_in in ('stage', 'all'):
                search_domain = OR([search_domain, [('stage_id', 'ilike', search)]])
            domain += search_domain

        # task count
        task_count = request.env['project.task'].search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/tasks",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby, 'search_in': search_in, 'search': search},
            total=task_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        if groupby == 'project':
            order = "project_id, %s" % order  # force sort on project first to group by project in view
        tasks = request.env['project.task'].search(domain, order=order, limit=self._items_per_page, offset=(page - 1) * self._items_per_page)
        request.session['my_tasks_history'] = tasks.ids[:100]
        if groupby == 'project':
            grouped_tasks = [request.env['project.task'].concat(*g) for k, g in groupbyelem(tasks, itemgetter('project_id'))]
        else:
            grouped_tasks = [tasks]

        values.update({
            'date': date_begin,
            'date_end': date_end,
            'grouped_tasks': grouped_tasks,
            'page_name': 'task',
            'archive_groups': archive_groups,
            'default_url': '/my/tasks',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_groupby': searchbar_groupby,
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'sortby': sortby,
            'groupby': groupby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
        })
        return request.render("project.portal_my_tasks", values)

    @http.route(['/my/task/<int:task_id>'], type='http', auth="public", website=True)
    def portal_my_task(self, task_id, access_token=None, **kw):
        try:
            task_sudo = self._document_check_access('project.task', task_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        # ensure attachment are accessible with access token inside template
        for attachment in task_sudo.attachment_ids:
            attachment.generate_access_token()
        values = self._task_get_page_view_values(task_sudo, access_token, **kw)
        return request.render("project.portal_my_task", values)
"""