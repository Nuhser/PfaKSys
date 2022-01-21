from flask_babel import lazy_gettext
from flask_wtf import FlaskForm
from wtforms import BooleanField, IntegerField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, ValidationError

from PfaKSys.item.item_condition import ItemCondition
from PfaKSys.models import Item, ItemCategory, ItemLocation


class ItemForm(FlaskForm):
    name = StringField(lazy_gettext('ui.common.name'), validators=[DataRequired(), Length(2, 120)])
    has_count = BooleanField(lazy_gettext('ui.item.has_count'), default=True)
    count = IntegerField(lazy_gettext('ui.common.count'), default=0)
    condition = SelectField(lazy_gettext('ui.common.condition'), choices=[(condition.name, condition.value) for condition in ItemCondition])
    category = SelectField(lazy_gettext('ui.item.category'))
    location = SelectField(lazy_gettext('ui.item.location'))
    description = TextAreaField(lazy_gettext('ui.common.description'))
    comment = TextAreaField(lazy_gettext('ui.common.comment'))
    submit = SubmitField(lazy_gettext('ui.common.save'))

    # set if form is used for item editing
    item_id = None

    def validate_name(self, name: StringField) -> None:
        item = Item.query.filter_by(name=name.data).first()
        if item and( item.id != self.item_id):
            raise ValidationError(lazy_gettext('validation_error.item.name_already_taken'))

    def validate_count(self, count: IntegerField) -> None:
        if self.has_count.data:
            if (count.data == None) or (count.data < 0):
                raise ValidationError(lazy_gettext('validation_error.item.count_min_zero'))


class ItemCategoryForm(FlaskForm):
    category_name = StringField(lazy_gettext('ui.common.name'), validators=[DataRequired(), Length(2, 60)])
    submit = SubmitField(lazy_gettext('ui.common.save'))

    # set if form is used for category editing
    category_id = None

    def validate_category_name(self, category_name: StringField) -> None:
        category = ItemCategory.query.filter_by(name=category_name.data).first()
        if category and (category.id != self.category_id):
            raise ValidationError(lazy_gettext('validation_error.item_category.name_already_taken'))


class ItemLocationForm(FlaskForm):
    location_name = StringField(lazy_gettext('ui.common.name'), validators=[DataRequired(), Length(2, 60)])
    submit = SubmitField(lazy_gettext('ui.common.save'))

    # set if form is used for location editing
    location_id = None

    def validate_location_name(self, location_name: StringField) -> None:
        location = ItemLocation.query.filter_by(name=location_name.data).first()
        if location and (location.id != self.location_id):
            raise ValidationError(lazy_gettext('validation_error.item_location.name_already_taken'))

class SearchItemForm(FlaskForm):
    search_name = StringField()
    submit = SubmitField(lazy_gettext('ui.common.search'))
