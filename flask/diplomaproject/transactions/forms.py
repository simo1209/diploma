from flask_wtf import FlaskForm
from wtforms import TextAreaField, DecimalField
from wtforms.validators import DataRequired, ValidationError


class TransactionForm(FlaskForm):
    amount = DecimalField('Amount', [DataRequired()])
    description = TextAreaField('Description', [DataRequired()])

    def validate_amount(form, field):
        if float(field.data) < 0:
            raise ValidationError('Amount must be positive')