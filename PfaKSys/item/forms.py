from flask_babel import lazy_gettext
from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange, ValidationError

from PfaKSys.item.item_condition import ItemCondition
from PfaKSys.models import Item, ItemCategory, ItemLocation


class ItemForm(FlaskForm):
    name = StringField(lazy_gettext('ui.common.name'), validators=[DataRequired(), Length(2, 120)])
    count = IntegerField(lazy_gettext('ui.common.count'), validators=[NumberRange(min=0)])
    condition = SelectField(lazy_gettext('ui.common.condition'), choices=[(condition.name, condition.value) for condition in ItemCondition])
    category = SelectField(lazy_gettext('ui.item.category'))
    location = SelectField(lazy_gettext('ui.item.location'))
    description = TextAreaField(lazy_gettext('ui.common.description'))
    submit = SubmitField(lazy_gettext('ui.common.save'))

    # set if form is used for item editing
    item_id = None

    def validate_name(self, name: StringField) -> None:
        item = Item.query.filter_by(name=name.data).first()
        if item and item.id != self.item_id:
            raise ValidationError(lazy_gettext('validation_error.item.name_already_taken'))


class NewItemCategoryForm(FlaskForm):
    category_name = StringField(lazy_gettext('ui.common.name'), validators=[DataRequired(), Length(2, 60)])
    submit = SubmitField(lazy_gettext('ui.common.save'))

    def validate_category_name(self, category_name: StringField) -> None:
        category = ItemCategory.query.filter_by(name=category_name.data).first()
        if category:
            raise ValidationError(lazy_gettext('validation_error.item_category.name_already_taken'))


class NewItemLocationForm(FlaskForm):
    location_name = StringField(lazy_gettext('ui.common.name'), validators=[DataRequired(), Length(2, 60)])
    submit = SubmitField(lazy_gettext('ui.common.save'))

    def validate_location_name(self, location_name: StringField) -> None:
        location = ItemLocation.query.filter_by(name=location_name.data).first()
        if location:
            raise ValidationError(lazy_gettext('validation_error.item_location.name_already_taken'))
