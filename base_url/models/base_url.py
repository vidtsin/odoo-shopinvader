# -*- coding: utf-8 -*-
#    Copyright (C) 2016 Akretion (http://www.akretion.com)
#    @author EBII MonsieurB <monsieurb@saaslys.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api, fields, _
import logging
from openerp.exceptions import Warning as UserError
_logger = logging.getLogger(__name__)
try:
    from slugify import slugify
except ImportError:
    _logger.debug('Cannot `import slugify`.')


class UrlUrl(models.Model):

    _name = "url.url"

    url_key = fields.Char(string="Url Id")
    model_id = fields.Reference(selection='_reference_models',
                                help="The id of product or category.",
                                readonly=True, string="Model")
    redirect = fields.Boolean('Redirect', help="this url is active or has"
                                               " to redirect to an other")

    _sql_constraints = [('urlurl unique key',
                         'unique(url_key)',
                         'Already exists in database')]

    @api.model
    def _reference_models(self):
        return []

    @api.multi
    def _get_object(self, url):
        """
        :return: return object attach to the url
        """
        object = self.search([('url_key', "=", url)]).model_id
        return object


class AbstractUrl(models.AbstractModel):
    _name = 'abstract.url'

    url_key = fields.Char(compute='_compute_url', inverse='_inverse_set_url',
                          string='Url Key', help='partie d url pour accès')
    redirect_url_key_ids = fields.One2many(compute='_compute_redirect_url',
                                           comodel_name='url.url')

    def _get_model_id_reference(self):
        return "%s,%s" % (self._name, self.id)

    def _prepare_url(self):

        url_key = slugify(self.name)

        return url_key

    @api.multi
    def _inverse_set_url(self):
        """
        backup old url

        1 find url redirect true and same model_id
        if other model id refuse
        2 if exists set to False

        3 write the new one
        """

        model_ref = self._get_model_id_reference()

        # key exist ?
        already_exist_url = self.env['url.url'].search(
            [('url_key', '=', self.url_key)])

        if already_exist_url:
            # existing key in wich object ?
            for url in already_exist_url:
                model = url.model_id
                model_txt = "%s,%s" % (model._name, model.id)
                if model_txt != model_ref:
                    # existing key for other model
                    raise UserError(
                        _("Url_key already exist in other model"
                          " %s" % (model.name)))
                else:  # existing key for same object toggle redirect to False
                    already_exist_url.redirect = False
        else:
            # no existing key creating one
            vals = {'url_key': self.url_key,
                    'model_id': model_ref,
                    'redirect': False}
            self.env['url.url'].create(vals)
            # other url of object set redirect to True
        redirect_urls = self.env['url.url'].search([
            ('model_id', '=', model_ref),
            ('url_key', '!=', self.url_key),
            ('redirect', '=', False)])

        for exist_url in redirect_urls:
                exist_url.redirect = True

    @api.multi
    def _compute_url(self):
        for record in self:
            model_ref = record._get_model_id_reference()
            _logger.info("used model  : %s ", model_ref)
            # import pdb; pdb.set_trace()
            url = record.env["url.url"].search([('model_id', '=', model_ref),
                                                ('redirect', '=', False)])
            if url:
                record.url_key = url.url_key

    @api.multi
    def _compute_redirect_url(self):
        for record in self:
            model_ref = record._get_model_id_reference()

            record.redirect_url_key_ids = record.env["url.url"].search(
                [('model_id', '=', model_ref), ('redirect', '=', True)])

    @api.onchange('name')
    def on_name_change(self):
        for record in self:
            if record.name:
                url_key = record._prepare_url()
                record.url_key = url_key

    @api.onchange('url_key')
    def on_url_key_change(self):

        for record in self:
            if record.url_key:
                url = slugify(record.url_key)
                if url != record.url_key:
                    record.url_key = url
                    return {'value': {},
                            'warning': {
                                'title': 'Adapt text rules',
                                'message': 'it will will be adapted to %s' %
                                           (url)}}