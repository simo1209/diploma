
from re import T
from flask.globals import request
from flask_admin import expose
from flask_admin import BaseView
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
        if request.method == 'POST':
            if request.form['begin_date'] and request.form['end_date']:
                begin_date, end_date = request.form.get('begin_date'), request.form.get('end_date')
                
                aggregation = request.form.get('aggregation')
                if aggregation == 'day':
                    result = db.session.execute('SELECT date_trunc(\'day\', creation_time)::date as date, count(*) FROM transactions WHERE creation_time BETWEEN date :begin_date AND date :end_date GROUP BY date_trunc(\'day\', creation_time) LIMIT 32;', {'begin_date':begin_date, 'end_date':end_date} )
                elif aggregation == 'month':
                    result = db.session.execute('SELECT date_trunc(\'month\', creation_time)::date as date, count(*) FROM transactions WHERE creation_time BETWEEN date :begin_date AND date :end_date GROUP BY date_trunc(\'month\', creation_time) LIMIT 32;', {'begin_date':begin_date, 'end_date':end_date} )
                elif aggregation == 'year':
                    result = db.session.execute('SELECT date_trunc(\'year\', creation_time)::date as date, count(*) FROM transactions WHERE creation_time BETWEEN date :begin_date AND date :end_date GROUP BY date_trunc(\'year\', creation_time) LIMIT 32;', {'begin_date':begin_date, 'end_date':end_date} )
                elif aggregation == 'type':
                    result = db.session.execute('SELECT type, count(*) FROM transaction_inquiry WHERE creation_time BETWEEN date :begin_date AND date :end_date GROUP BY type LIMIT 32;', {'begin_date':begin_date, 'end_date':end_date} )
                elif aggregation == 'status':
                    result = db.session.execute('SELECT status, count(*) FROM transaction_inquiry WHERE creation_time BETWEEN date :begin_date AND date :end_date GROUP BY status LIMIT 32;', {'begin_date':begin_date, 'end_date':end_date} )
                elif aggregation == 'amount':
                    result = db.session.execute('SELECT amount, count(*) FROM transaction_inquiry WHERE creation_time BETWEEN date :begin_date AND date :end_date GROUP BY amount LIMIT 32;', {'begin_date':begin_date, 'end_date':end_date} )
                else:
                    result = db.session.execute('SELECT * FROM transaction_inquiry WHERE creation_time BETWEEN date :begin_date AND date :end_date + interval \'1 day\' LIMIT 32;', {'begin_date':begin_date, 'end_date':end_date} )
                    return self.render('transaction_inquiry.html', begin_date = begin_date, end_date = end_date, transactions = result)
                
                return self.render('transaction_inquiry.html', begin_date = begin_date, end_date = end_date, aggregations = result, aggregation=aggregation)
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


