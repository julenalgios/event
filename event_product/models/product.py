# -*- coding: utf-8 -*-
# © 2015 Grupo ESOC Ingeniería de Servicios, S.L.U. - Jairo Llopis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models
from .. import exceptions as ex


class ProductBase(models.AbstractModel):
    _name = "event_product.product"

    @api.multi
    @api.constrains("event_ok", "is_event")
    def _check_ticket_is_not_event(self):
        """Ensure events are not tickets."""
        for s in self:
            if s.event_ok and s.is_event:
                raise ex.EventAndTicketError()

    @api.multi
    @api.onchange("is_event")
    def _onchange_is_event(self):
        """Avoid conflicts between :attr:`~.event_ok` and :attr:`~.is_event`.

        Products cannot be an event and a ticket at the same time.
        """
        for s in self:
            if s.is_event:
                s.event_ok = False
                s.type = "service"


class ProductTemplate(models.Model):
    _name = "product.template"
    _inherit = ["product.template", ProductBase._name]

    is_event = fields.Boolean(
        "Is an event",
        help="This product defines an event (NOT an event ticket).")

    @api.multi
    def onchange_event_ok(self, type, event_ok):
        """Inverse of :meth:`~._onchange_is_event`.

        Cannot declare in ``event_product.product`` because it gets ignored.
        """
        # TODO Merge with `_onchange_is_event` when core updates to new api
        result = super(ProductTemplate, self).onchange_event_ok(type, event_ok)
        if event_ok:
            result.setdefault("value", dict())
            result["value"]["is_event"] = False
        return result


class ProductProduct(models.Model):
    _name = "product.product"
    _inherit = ["product.product", ProductBase._name]

    event_ids = fields.One2many(
        "event.event",
        "product_id",
        "Events")

    @api.multi
    @api.constrains("is_event", "event_type_id", "event_ids")
    def _check_event_type_consistent(self):
        """Avoid changing type if it creates an inconsistency."""
        self.mapped("event_ids")._check_product_type()

    @api.multi
    def onchange_event_ok(self, type, event_ok):
        """Inverse of :meth:`~._onchange_is_event`.

        Cannot declare in ``event_product.product`` because it gets ignored.
        """
        # TODO Merge with `_onchange_is_event` when core updates to new api
        result = super(ProductProduct, self).onchange_event_ok(type, event_ok)
        if event_ok:
            result.setdefault("value", dict())
            result["value"]["is_event"] = False
        return result
