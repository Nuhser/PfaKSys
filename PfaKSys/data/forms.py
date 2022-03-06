from flask_babel import lazy_gettext
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from pandas import isnull
from wtforms import BooleanField, SelectField, SubmitField
from wtforms.validators import ValidationError

from PfaKSys.item.item_condition import ItemCondition
from PfaKSys.models import ItemCategory, ItemLocation


class ExcelItemImportForm(FlaskForm):
    excel_file = FileField(lazy_gettext('ui.import.excel_file'), validators=[FileAllowed(['xls', 'xlsx', 'odt'])])
    has_header_row = BooleanField(lazy_gettext('ui.import.has_header_row'), default=True)
    submit_excel_item_import = SubmitField(lazy_gettext('ui.common.import'))

    def validate_excel_file(self, excel_file: FileField) -> None:
        if excel_file.data == None:
            raise ValidationError(lazy_gettext('validation_error.no_file_selected'))


class ExcelItemImportModalFormBase(FlaskForm):
    submit_excel_item_import_modal = SubmitField(lazy_gettext('ui.common.import'))


def excel_item_import_modal_form_builder(import_data: dict):
    class ExcelItemImportModalForm(ExcelItemImportModalFormBase):
        pass

    for condition in set(import_data['condition'].values()):
        if isnull(condition):
            continue

        setattr(
            ExcelItemImportModalForm,
            f'condition_{condition}',
            SelectField(f'{condition}', choices=[(condition.name, condition.value) for condition in ItemCondition])
        )

    for category in set(import_data['category'].values()):
        if isnull(category):
            continue

        setattr(
            ExcelItemImportModalForm,
            f'category_{category}',
            SelectField(
                f'{category}',
                choices=[(None, lazy_gettext('ui.data_import.new_category'))] + [(category.id, category.name) for category in ItemCategory.query.order_by(ItemCategory.name.collate('NOCASE').asc()).all()]
            )
        )

    for location in set(import_data['location'].values()):
        if isnull(location):
            continue

        setattr(
            ExcelItemImportModalForm,
            f'location_{location}',
            SelectField(
                f'{location}',
                choices=[(None, lazy_gettext('ui.data_import.new_location'))] + [(location.id, location.name) for location in ItemLocation.query.order_by(ItemLocation.name.collate('NOCASE').asc()).all()]
            )
        )

    return ExcelItemImportModalForm()
