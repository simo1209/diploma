
from re import T
from flask.globals import request
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
            'year':'to_char(creation_time, \'YYYY\')',
            'month':'to_char(creation_time, \'YYYY-MM\')',
            'day':'to_char(creation_time, \'YYYY-MM-DD\')',
            'type':'type',
            'status':'status',
            'amount':'amount'
        }

        filter_fields = {
            'year': 'to_char(creation_time, \'YYYY\') = :year',
            'month': 'to_char(creation_time, \'YYYY-MM\') = :month',
            'day': 'to_char(creation_time, \'YYYY-MM-DD\') = :day',
            'type': 'type = :type',
            'status': 'status = :status',
            'amount': 'amount = :amount'
        }

        if request.method == 'POST':
            if request.form['begin_date'] and request.form['end_date']:
                begin_date, end_date = request.form.get('begin_date'), request.form.get('end_date')
                
                query_args = {'begin_date':begin_date, 'end_date':end_date}

                aggregations = request.form.getlist('aggregations')

                filter = request.form.get('filter')
                filter_value = request.form.get('filter_value')

                inquiry_filters = 'creation_time >= :begin_date AND creation_time <= :end_date'

                if filter in filter_fields.keys():
                    inquiry_filters = f'creation_time >= :begin_date AND creation_time <= :end_date AND {filter_fields[filter]}'

                inquiry_columns = '*'
                query = f'SELECT {inquiry_columns} FROM transaction_inquiry WHERE {inquiry_filters} LIMIT 32;'

                valid_aggregations = [aggregation for aggregation in aggregations if aggregation in group_fields ]
                if valid_aggregations:
                    groupings = [group_fields[aggregation] for aggregation in valid_aggregations]
                    aggregation_columns = ','.join(groupings)
                    inquiry_columns = f'{aggregation_columns}, COUNT(*)'
                    query = f'SELECT {inquiry_columns} FROM transaction_inquiry WHERE {inquiry_filters} GROUP BY {aggregation_columns} LIMIT 32;'

                result = db.session.execute(query, query_args )
                return self.render('transaction_inquiry.html', filter_fields = filter_fields.keys(), group_fields=group_fields, begin_date = begin_date, end_date = end_date, transactions = result, aggregations = valid_aggregations, filter = filter, filter_value = filter_value)

        return self.render('transaction_inquiry.html', filter_fields = filter_fields.keys(), group_fields=group_fields.keys(), filter_value = 'None')

class RoleModelView(CustomModelView):

    def is_accessible(self):
        return 'view_roles' in current_user.get_permissions()

    @property
    def can_create(self):
        return 'create_roles' in current_user.get_permissions()

    @property
    def can_edit(self):
        return 'edit_roles' in current_user.get_permissions()


