import pandas as pd

from flask import Blueprint, redirect, render_template, request, session
from flask_babel import gettext
from flask_login import login_required

from PfaKSys.data.forms import ExcelItemImportForm, excel_item_import_modal_form_builder
from PfaKSys.data.item_import import from_excel_file
from PfaKSys.main.permissions import Permission, permission_required
from PfaKSys.main.utils import _url_for


data_blueprint = Blueprint('data', __name__)


@data_blueprint.route('/import_data', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.data_import)
def import_data():
    excel_item_import_form = ExcelItemImportForm()
    excel_item_import_modal_form = None
    excel_item_import_data = session.pop('excel_item_import_data', None)
    excel_item_import_filename = session.pop('excel_item_import_filename', '')

    new_items = session.pop('import_new_items', [])
    new_categories = session.pop('import_new_categories', [])
    new_locations = session.pop('import_new_locations', [])

    modals_visible = session.pop('modals_visible', [])

    if 'submit_excel_item_import' in request.form:
        if excel_item_import_form.validate_on_submit():
            excel_item_import_data = pd.read_excel(
                excel_item_import_form.excel_file.data,
                header=(0 if excel_item_import_form.has_header_row.data else None),
                names=['name', 'quantity', 'condition', 'category', 'location', 'description', 'comment']
            ).to_dict()

            session['excel_item_import_data'] = excel_item_import_data
            session['excel_item_import_filename'] = excel_item_import_form.excel_file.data.filename
            session['modals_visible'] = ['excel-item-import-modal']

            return redirect(_url_for('data.import_data'))

    elif 'submit_excel_item_import_modal' in request.form:
        excel_item_import_modal_form = excel_item_import_modal_form_builder(excel_item_import_data)

        if excel_item_import_modal_form.validate_on_submit():
            session['import_new_items'], session['import_new_categories'], session['import_new_locations'] = from_excel_file(excel_item_import_data, excel_item_import_modal_form)

            session['modals_visible'] = ['excel-item-import-success-modal']

            return redirect(_url_for('data.import_data'))

    elif request.method == 'GET':
        if 'excel-item-import-modal' in modals_visible:
            excel_item_import_modal_form = excel_item_import_modal_form_builder(excel_item_import_data)

        session['excel_item_import_data'] = excel_item_import_data
        session['excel_item_import_filename'] = excel_item_import_filename

    return render_template(
        'data/imports.html',
        title=gettext('page.data_import.title'),
        modals_visible=modals_visible,
        excel_item_import_form=excel_item_import_form,
        excel_item_import_modal_form=excel_item_import_modal_form,
        excel_item_import_data=excel_item_import_data,
        excel_item_import_filename=excel_item_import_filename,
        new_items=new_items,
        new_categories=new_categories,
        new_locations=new_locations
    )
