import copy
from odoo import _, api, fields, models, modules,tools
from odoo.exceptions import UserError
from odoo.tools import safe_eval



class ApprovalRequest(models.Model):
    _inherit = 'approval.request'

    model_id = fields.Many2one('ir.model', string='Model')    
    record = fields.Integer(string='Record', ondelete="set null",index=True)

class ApprovalCategory(models.Model):
    _inherit = 'approval.category'

    model_id = fields.Many2one(
        "ir.model",
        "Model",
        help="Select model for which you want to create approval category.",
        ondelete="set null",
        index=True,
    )
    related_model_name = fields.Char(related='model_id.model', string='Model Name')
    condition = fields.Char(string='Condition', help="If present, this condition must be satisfied for operations.")

    states={"subscribed": [("readonly", True)]},
    model_name = fields.Char(readonly=True)
    model_model = fields.Char(string="Technical Model Name", readonly=True)

    approval_create = fields.Boolean(
        "Approval Creates",
        default=True,
        states={"subscribed": [("readonly", True)]},
    )
    approval_write = fields.Boolean(
            "Approval Writes",
            default=True,
            states={"subscribed": [("readonly", True)]},
        )
    state = fields.Selection(
        [("draft", "Draft"), ("subscribed", "Subscribed")],
        required=True,
        default="draft",
    )
    action_id = fields.Many2one(
        "ir.actions.act_window",
        string="Action",
        states={"subscribed": [("readonly", True)]},
    )
    body_html = fields.Html(string='Body template for Approval Request', sanitize_attributes=False)

   
    _sql_constraints = [
        (
            "model_uniq",
            "unique(model_id)",
            (
                "There is already a category defined on this model\n"
                "You cannot define another: please edit the existing one."
            ),
        )
    ]

    def _register_hook(self):
        super(ApprovalCategory, self)._register_hook()
        if not hasattr(self.pool, "_approval_category_field_cache"):
            self.pool._approval_category_field_cache = {}
        if not hasattr(self.pool, "_approval_category_model_cache"):
            self.pool._approval_category_model_cache = {}
        if not self:
            self = self.search([("state", "=", "subscribed")])
        return self._patch_methods()

    def _patch_methods(self):
        """Patch ORM methods of models defined in Approval categories."""
        updated = False
        model_cache = self.pool._approval_category_model_cache
        for category in self:
            if category.state != "subscribed":
                continue
            if not self.pool.get(category.model_id.model or category.model_model):
                # ignore categories for models not loadable currently
                continue
            model_cache[category.model_id.model] = category.model_id.id
            model_model = self.env[category.model_id.model or category.model_model]
            # CRUD
            #   -> create
            check_attr = "approval_category_create"
            # if category.approval_create and not hasattr(model_model, check_attr):
            if not hasattr(model_model, check_attr):
                model_model._patch_method("create", category._make_create())
                setattr(type(model_model), check_attr, True)
                updated = True
            #   -> write
            check_attr = "approval_category_write"
            if not hasattr(model_model, check_attr):
                model_model._patch_method("write", category._make_write())
                setattr(type(model_model), check_attr, True)
                updated = True

        return updated

    def _revert_methods(self):
        """Restore original ORM methods of models defined in categorys."""
        updated = False
        for category in self:
            model_model = self.env[category.model_id.model or category.model_model]
            for method in ["create","write"]:
                if getattr(category, "approval_%s" % method) and hasattr(
                    getattr(model_model, method), "origin"
                ):
                    model_model._revert_method(method)
                    delattr(type(model_model), "approval_category_%s" % method)
                    updated = True
        if updated:
            modules.registry.Registry(self.env.cr.dbname).signal_changes()

    @api.model
    def create(self, vals):
        """Update the registry when a new category is created."""
        if "model_id" not in vals or not vals["model_id"]:
            raise UserError(_("No model defined to create line."))
        model = self.env["ir.model"].browse(vals["model_id"])
        vals.update({"model_name": model.name, "model_model": model.model})
        new_record = super().create(vals)
        if new_record._register_hook():
            modules.registry.Registry(self.env.cr.dbname).signal_changes()
        return new_record

    def write(self, vals):
        """Update the registry when existing categories are updated."""
        if "model_id" in vals:
            if not vals["model_id"]:
                raise UserError(_("Field 'model_id' cannot be empty."))
            model = self.env["ir.model"].browse(vals["model_id"])
            vals.update({"model_name": model.name, "model_model": model.model})
        res = super().write(vals)
        if self._register_hook():
            modules.registry.Registry(self.env.cr.dbname).signal_changes()
        return res

    def unlink(self):
        """Unsubscribe categories before removing them."""
        self.unsubscribe()
        return super(ApprovalCategory, self).unlink()

    # @api.model
    # def get_approval_category_fields(self, model):
    #     """
    #     Get the list of category fields for a model
    #     By default it is all stored fields only, but you can
    #     override this.
    #     """
    #     return list(
    #         n
    #         for n, f in model._fields.items()
    #         if (not f.compute and not f.related) or f.store
    #     )

    def _make_create(self):
        """Instanciate a create method that create approval request records."""
        self.ensure_one()
        category_type = 'full'

        @api.model_create_multi
        @api.returns("self", lambda value: value.id)
        def create_full(self, vals_list, **kwargs):
            self = self.with_context(auditlog_disabled=True)
            # category_model = self.env["approval.category"]
            new_record = create_full.origin(self, vals_list, **kwargs)
            # res_ids = new_record.ids,
            res_model = self._name
            model_model = self.env[res_model]
            model_id = self.pool._approval_category_model_cache[res_model]
            approval_category = self.env["approval.category"].search([("model_id", "=", model_id)])
            if approval_category:
                approval_request_creation = True
                if approval_category.condition:
                    domain = safe_eval.safe_eval(approval_category.condition)
                    if new_record.filtered_domain(domain):
                        approval_request_creation = True
                    else:
                        approval_request_creation = False

                if approval_request_creation:
                    request = self.env["approval.request"]
                    body_html = ''
                    if approval_category.body_html:
                        # mail_template_object = self.env["mail.render.mixin"]
                        mail_template_object = self.env["mail.template"]
                        data = {
                            'name':approval_category.name,
                            'model_id':approval_category.model_id.id,
                            'body_html':approval_category.body_html
                        }
                        mail_template_result = mail_template_object.create(data)
                        # for lang, (template, template_res_ids) in mail_template_object._classify_per_lang([new_record.id]).items():
                        for lang, (template, template_res_ids) in mail_template_result._classify_per_lang([new_record.id]).items():
                            for field in ['body_html']:
                                result = generated_field_values = template._render_field(
                                    field, template_res_ids,
                                    post_process=(field == 'body_html'))
                            for res_id in template_res_ids:
                                body_html = result[res_id]
                        mail_template_result.unlink()


                    vals = {
                        "name": new_record.display_name,
                        "request_owner_id":self.env.uid,
                        "category_id": approval_category.id,
                        "request_status": 'new',
                        "model_id": model_id,
                        "record": new_record.id,
                        "reason": body_html,
                        }
                    approval_request = request.create(vals)
            return new_record

        return create_full


    def _make_write(self):
        """Instanciate a write method that capture its calls."""
        print("inside write method")
        self.ensure_one()
        category_type = 'full'
        # users_to_exclude = self.mapped("users_to_exclude_ids")

        def write_full(self, vals, **kwargs):
            self = self.with_context(auditlog_disabled=True)
            result = write_full.origin(self, vals, **kwargs)

            res_model = self._name
            model_model = self.env[res_model]
            model_id = self.pool._approval_category_model_cache[res_model]
            approval_category = self.env["approval.category"].search([("model_id", "=", model_id)])
            if approval_category:
                approval_request_updation = True
                if approval_category.condition:
                    domain = safe_eval.safe_eval(approval_category.condition)
                    if self.filtered_domain(domain):
                        approval_request_updation = True
                    else:
                        approval_request_updation = False
                    
                if approval_request_updation:
                    request = self.env["approval.request"].search([('record','=',self.id)])
                    body_html = ''
                    if approval_category.body_html:
                        mail_template_object = self.env["mail.template"]
                        data = {
                            'name':approval_category.name,
                            'model_id':approval_category.model_id.id,
                            'body_html':approval_category.body_html
                        }
                        mail_template_result = mail_template_object.create(data)
                        for lang, (template, template_res_ids) in mail_template_result._classify_per_lang([self.id]).items():
                            for field in ['body_html']:
                                result = generated_field_values = template._render_field(
                                    field, template_res_ids,
                                    post_process=(field == 'body_html'))
                            for res_id in template_res_ids:
                                body_html = result[res_id]
                        
                        vals = {
                        # "name": approval_category.name,
                        "name": self.display_name,
                        "reason": body_html,
                        }
                        approval_request = request.write(vals)
                        
            return result
        return write_full



    def _get_field(self, model, field_name):
        cache = self.pool._approval_category_field_cache
        if field_name not in cache.get(model.model, {}):
            cache.setdefault(model.model, {})
            # - we use 'search()' then 'read()' instead of the 'search_read()'
            #   to take advantage of the 'classic_write' loading
            # - search the field in the current model and those it inherits
            field_model = self.env["ir.model.fields"]
            all_model_ids = [model.id]
            all_model_ids.extend(model.inherited_model_ids.ids)
            field = field_model.search(
                [("model_id", "in", all_model_ids), ("name", "=", field_name)]
            )
            # The field can be a dummy one, like 'in_group_X' on 'res.users'
            if not field:
                cache[model.model][field_name] = False
            else:
                field_data = field.read(load="_classic_write")[0]
                cache[model.model][field_name] = field_data
        return cache[model.model][field_name]

    def subscribe(self):
        """Subscribe Category for changes on model and apply shortcut
        to categories on that model.
        """
        act_window_model = self.env["ir.actions.act_window"]
        for category in self:
            # Create a shortcut to categories
            domain = "[('model_id', '=', %s), ('res_id', '=', active_id)]" % (
                category.model_id.id
            )
            vals = {
                "name": _("Make Approval Request"),
                # "res_model": "approval.request",
                "res_model": "approval.category",
                "binding_model_id": category.model_id.id,
                "domain": domain,
            }
            act_window = act_window_model.sudo().create(vals)
            category.write({"state": "subscribed", "action_id": act_window.id})
        return True

    def unsubscribe(self):
        """Unsubscribe category on model."""
        # Revert patched methods
        self._revert_methods()
        for category in self:
            # Remove the shortcut to categories
            act_window = category.action_id
            if act_window:
                act_window.unlink()
        self.write({"state": "draft"})
        return True
