
from re import T
from flask.globals import request
from flask_admin import expose
from flask_admin.contrib.sqla import ModelView, filters
from flask_admin.model.template import TemplateLinkRowAction
from flask_admin.model.template import EndpointLinkRowAction

from flask_login import current_user
from werkzeug.exceptions import Forbidden
from backoffice import db
from backoffice.models import Account
from flask_admin.contrib.sqla.ajax import QueryAjaxModelLoader

class TransactionDateFilter(filters.FilterConverter):
    datetime_filters = (
        filters.DateTimeEqualFilter,
        filters.DateTimeBetweenFilter
    )

class AccountModelView(ModelView):

    column_exclude_list = ['password']
    column_searchable_list = ['first_name', 'last_name', 'email']
    form_excluded_columns = ['categoriess', 'login_attempts', 'registered_on', 'balance']
    column_filters = ['balance']

    list_template = "my_list.html"  # Override the default template
    column_extra_row_actions = [  # Add a new action button
        EndpointLinkRowAction("glyphicon glyphicon-list-alt", ".history_view"),
    ]

    @expose("/history", methods=["GET"])
    def history_view(self):
        
        args = dict(request.args)
        print(args['id'])

        id = args['id']
        
        result = db.session.execute('SELECT * FROM transaction_history(:val)', {'val': id})
        print(result)
        rows = [row for row in result]
        print(rows)

        return self.render('transaction_history.html', rows=rows)

    def is_accessible(self):
        return 'view_accounts' in current_user.get_permissions()

    def inaccessible_callback(self, name, **kwargs):
        raise Forbidden('You do not have required permission')

    @property
    def can_create(self):
        return 'create_accounts' in current_user.get_permissions()

    @property
    def can_edit(self):
        return 'edit_accounts' in current_user.get_permissions()

    @property
    def can_export(self):
        return 'export_accounts' in current_user.get_permissions()


class AdministratorModelView(ModelView):

    def is_accessible(self):
        return 'view_administrators' in current_user.get_permissions()

    def inaccessible_callback(self, name, **kwargs):
        raise Forbidden('You do not have required permission')

    @property
    def can_create(self):
        return 'create_administrators' in current_user.get_permissions()

    @property
    def can_edit(self):
        return 'edit_administrators' in current_user.get_permissions()

class TransactionDateFilter(filters.FilterConverter):

    # float_filters = (
    #     filters.FloatGreaterFilter,
    #     filters.FloatSmallerFilter
    # )

    datetime_filters = (
        filters.DateTimeBetweenFilter
    )



class TransactionModelView(ModelView):

    column_searchable_list = ['seller.first_name', 'seller.last_name', 'seller.email', 'buyer.first_name', 'buyer.last_name', 'buyer.email', 'description']
    form_excluded_columns = ['categories', 'creation_time', 'status_update_time', 'transaction_type', 'transaction_status']

    column_filters = ['amount', 'status_update_time']

    form_ajax_refs = {
        'seller': QueryAjaxModelLoader('seller', db.session, Account, fields=['email'], page_size=10),
        'buyer': QueryAjaxModelLoader('buyer', db.session, Account, fields=['email'], page_size=10)
    }

    def is_accessible(self):
        return 'view_transactions' in current_user.get_permissions()

    def inaccessible_callback(self, name, **kwargs):
        raise Forbidden('You do not have required permission')

    @property
    def can_create(self):
        return 'create_transactions' in current_user.get_permissions()

    @property
    def can_edit(self):
        return 'edit_transactions' in current_user.get_permissions()

    @property
    def can_export(self):
        return 'export_transactions' in current_user.get_permissions()

class RoleModelView(ModelView):

    def is_accessible(self):
        return 'view_roles' in current_user.get_permissions()

    def inaccessible_callback(self, name, **kwargs):
        raise Forbidden('You do not have required permission')

    @property
    def can_create(self):
        return 'create_roles' in current_user.get_permissions()

    @property
    def can_edit(self):
        return 'edit_roles' in current_user.get_permissions()


# class AccountModelView(ModelView):

#     can_create = False

#     column_exclude_list = ['password']
#     form_excluded_columns = ['balance', 'password', 'registered_on', 'is_admin']


#     def is_accessible(self):
#         return current_user.is_authenticated

#     def inaccessible_callback(self, name, **kwargs):
#         raise Unauthorized('Please log in')

# class TransactionModelView(ModelView):

#     can_edit = False
#     can_export = True
#     can_delete = False

#     form_excluded_columns = ['buyer', 'status', 'creation_time']
#     filter_converter = TransactionDateFilter()
#     column_filters = ['creation_time', 'transaction_type', 'transaction_status']


#     def is_accessible(self):
#         return current_user.is_authenticated

#     def inaccessible_callback(self, name, **kwargs):
#         raise Unauthorized('Please log in')
