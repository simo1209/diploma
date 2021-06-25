
from os import name
from flask_admin.contrib.sqla import ModelView, filters
from flask_login import current_user, login_required
from werkzeug.exceptions import Unauthorized, Forbidden
from sqlalchemy import func, or_
from backoffice.models import Administrator, Permission, Role

class TransactionDateFilter(filters.FilterConverter):
    datetime_filters = (
        filters.DateTimeEqualFilter,
        filters.DateTimeBetweenFilter
    )

class AccountModelView(ModelView):

    def is_accessible(self):
        return Permission.query.filter_by(name='view_accounts').first() in current_user.get_permissions()

    def inaccessible_callback(self, name, **kwargs):
        raise Forbidden('You do not have required permission')

    @property
    def can_create(self):
        return Permission.query.filter_by(name='create_accounts').first() in current_user.get_permissions()

    @property
    def can_edit(self):
        return Permission.query.filter_by(name='edit_accounts').first() in current_user.get_permissions()


class AdministratorModelView(ModelView):

    def is_accessible(self):
        return Permission.query.filter_by(name='view_administrators').first() in current_user.get_permissions()

    def inaccessible_callback(self, name, **kwargs):
        raise Forbidden('You do not have required permission')

    @property
    def can_create(self):
        return Permission.query.filter_by(name='create_administrators').first() in current_user.get_permissions()

    @property
    def can_edit(self):
        return Permission.query.filter_by(name='edit_administrators').first() in current_user.get_permissions()

class TransactionModelView(ModelView):

    def is_accessible(self):
        return Permission.query.filter_by(name='view_transactions').first() in current_user.get_permissions()

    def inaccessible_callback(self, name, **kwargs):
        raise Forbidden('You do not have required permission')

    @property
    def can_create(self):
        return Permission.query.filter_by(name='create_transactions').first() in current_user.get_permissions()

    @property
    def can_edit(self):
        return Permission.query.filter_by(name='edit_transactions').first() in current_user.get_permissions()

class RoleModelView(ModelView):

    def is_accessible(self):
        return Permission.query.filter_by(name='view_roles').first() in current_user.get_permissions()

    def inaccessible_callback(self, name, **kwargs):
        raise Forbidden('You do not have required permission')

    @property
    def can_create(self):
        return Permission.query.filter_by(name='create_roles').first() in current_user.get_permissions()

    @property
    def can_edit(self):
        return Permission.query.filter_by(name='edit_roles').first() in current_user.get_permissions()


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
