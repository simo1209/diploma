
from re import T
from flask.globals import request
from flask.helpers import url_for
from flask_admin import expose
from flask_admin import BaseView
from flask_admin.contrib.sqla import ModelView, filters
from flask_admin.model.template import TemplateLinkRowAction
from flask_admin.model.template import EndpointLinkRowAction

from flask_login import current_user
from sqlalchemy.orm import query
from werkzeug.exceptions import Forbidden
from backoffice import db
from backoffice.models import Account
from flask_admin.contrib.sqla.ajax import QueryAjaxModelLoader

from backoffice.utils import aggregate_result

class TransactionDateFilter(filters.FilterConverter):
    datetime_filters = (
        filters.DateTimeEqualFilter,
        filters.DateTimeBetweenFilter
    )

class CustomModelView(ModelView):

    def inaccessible_callback(self, name, **kwargs):
        raise Forbidden('You do not have required permission')

class AccountModelView(CustomModelView):

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
        id = args['id']
        
        result = db.session.execute('SELECT * FROM transaction_history(:val) ORDER BY date', {'val': id})
        rows = [row for row in result]

        return self.render('transaction_history.html', rows=rows)

    def is_accessible(self):
        return 'view_accounts' in current_user.get_permissions()

    @property
    def can_create(self):
        return 'create_accounts' in current_user.get_permissions()

    @property
    def can_edit(self):
        return 'edit_accounts' in current_user.get_permissions()

    @property
    def can_export(self):
        return 'export_accounts' in current_user.get_permissions()


class AdministratorModelView(CustomModelView):

    def is_accessible(self):
        return 'view_administrators' in current_user.get_permissions()

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



class TransactionModelView(CustomModelView):

    column_searchable_list = ['seller.first_name', 'seller.last_name', 'seller.email', 'buyer.first_name', 'buyer.last_name', 'buyer.email', 'description']
    form_excluded_columns = ['categories', 'creation_time', 'status_update_time', 'transaction_type', 'transaction_status']

    column_filters = ['amount', 'status_update_time']

    form_ajax_refs = {
        'seller': QueryAjaxModelLoader('seller', db.session, Account, fields=['email'], page_size=10),
        'buyer': QueryAjaxModelLoader('buyer', db.session, Account, fields=['email'], page_size=10)
    }

    def is_accessible(self):
        return 'view_transactions' in current_user.get_permissions()

    @property
    def can_create(self):
        return 'create_transactions' in current_user.get_permissions()

    @property
    def can_edit(self):
        return 'edit_transactions' in current_user.get_permissions()

    @property
    def can_export(self):
        return 'export_transactions' in current_user.get_permissions()


class TransactionInquiryView(BaseView):
    @expose('/', methods=['GET','POST'])
    def inquiry(self):
        group_fields = {
            'time_group': {'year':('time', 'to_char(creation_time, \'YYYY\')'),'month':('time', 'to_char(creation_time, \'YYYY-MM\')'),'day':('time', 'to_char(creation_time, \'YYYY-MM-DD\')')},
            'type_group':{'all':('type','type')},
            'status_group':{'all':('status','status')}
            # 'amount_group':('range','amount_range_func(amount)')
        }

        filter_fields = {
            'start_date_filter' : 'creation_time >= :start_date_filter',
            'end_date_filter' : 'creation_time < :end_date_filter',
            'type_filter': 'type = :type_filter',
            'status_filter': 'status = :status_filter',
            'min_amount_filter': 'amount >= :min_amount_filter',
            'max_amount_filter': 'amount < :max_amount_filter'
        }

        if request.method == 'POST':

            filter_keys = []
            filter_values = []

            groups = []

            for key,value in request.form.items():
                if key in filter_fields and value and value != 'none':
                    filter_keys.append(key)
                    filter_values.append(value)
                if key in group_fields:
                    if group_fields[key].get(value):
                        groups.append(group_fields[key][value])

            filter_query = ' AND '.join( [ filter_fields[filter_key] for filter_key in filter_keys ] )
            query_args = dict(zip(filter_keys, filter_values))
            query = ''
            aggregations = []
            if groups:
                
                aggregation_column_names = []
                for group in groups:
                    aggregations.append(f'{group[1]} as {group[0]}')
                    aggregation_column_names.append(group[0])

                aggregation_query = ', '.join(aggregations)
                aggregation_column_query = ', '.join(aggregation_column_names)
                query = f'SELECT {aggregation_query}, COUNT(*), SUM(amount) FROM transaction_inquiry WHERE {filter_query} GROUP BY {aggregation_column_query} LIMIT 32;'
            else:
                query = f'SELECT * FROM transaction_inquiry WHERE {filter_query} LIMIT 32;'
            result = db.session.execute(query, query_args )
            return self.render('transaction_inquiry.html', transactions = result, aggregations = aggregations)

        return self.render('transaction_inquiry.html')

class RoleModelView(CustomModelView):

    def is_accessible(self):
        return 'view_roles' in current_user.get_permissions()

    @property
    def can_create(self):
        return 'create_roles' in current_user.get_permissions()

    @property
    def can_edit(self):
        return 'edit_roles' in current_user.get_permissions()


