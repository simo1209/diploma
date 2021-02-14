
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, login_required
from werkzeug.exceptions import Unauthorized, Forbidden
from sqlalchemy import func, or_

from diplomaproject.models import Account, Transaction


class UserAccountModelView(ModelView):
    can_create = False
    can_delete = False

    column_exclude_list = ['password', 'is_admin', 'login_attempts', 'registered_on']
    form_excluded_columns = ['balance', 'password', 'is_admin', 'login_attempts', 'registered_on']


    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        raise Unauthorized('Please log in')

    def get_query(self):
        return self.session.query(self.model).filter(self.model.id == current_user.id)
    
    def get_count_query(self):
        return self.session.query(func.count('*')).filter(self.model.id == current_user.id)

class UserTransactionModelView(ModelView):

    can_create = False
    can_delete = False
    can_edit = False
    can_export = True

    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        raise Unauthorized('Please log in')

    def get_query(self):
        return self.session.query(self.model).filter(
            or_(
                self.model.seller_id == current_user.id,
                self.model.buyer_id == current_user.id
            )
        )

    def get_count_query(self):
      return self.session.query(func.count('*')).filter(
          or_(
              self.model.seller_id == current_user.id,
              self.model.buyer_id == current_user.id
          )
      )


class AdminAccountModelView(ModelView):

    can_create = False

    column_exclude_list = ['password']
    form_excluded_columns = ['balance', 'password', 'registered_on']


    def is_accessible(self):
        return current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        raise Forbidden('This is accessable only by administrators')

class AdminTransactionModelView(ModelView):

    can_edit = False
    can_export = True
    can_delete = False

    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        raise Unauthorized('Please log in')
