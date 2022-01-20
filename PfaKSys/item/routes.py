from datetime import datetime
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_babel import gettext
from flask_login import login_required

from PfaKSys import db
from PfaKSys.item.forms import ItemForm, NewItemCategoryForm, NewItemLocationForm
from PfaKSys.item.item_condition import ItemCondition
from PfaKSys.models import Item, ItemCategory, ItemLocation


item_blueprint = Blueprint('item', __name__)


@item_blueprint.route('/items/<int:item_id>/delete', methods=['POST'])
@login_required
def delete(item_id):
    item = Item.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()

    flash(gettext('flash.success.item.deleted', item_name=item.name), 'success')
    return redirect(url_for('item.overview'))


@item_blueprint.route('/items/<int:item_id>')
@login_required
def details(item_id):
    item = Item.query.get_or_404(item_id)
    return render_template('item/details.html', title=item.name, item=item)


@item_blueprint.route('/items/<int:item_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(item_id):
    item = Item.query.get_or_404(item_id)

    form = ItemForm()
    form.item_id = item.id
    form.category.choices = [(None, '')] + [(category.id, category.name) for category in ItemCategory.query.order_by(ItemCategory.name.collate('NOCASE').asc()).all()]
    form.location.choices = [(None, '')] + [(location.id, location.name) for location in ItemLocation.query.order_by(ItemLocation.name.collate('NOCASE').asc()).all()]

    if form.validate_on_submit():
        with db.session.no_autoflush:
            if item.name != form.name.data:
                _ = Item.query.filter_by(name=form.name.data).first()
                if not _:
                    item.name = form.name.data

            item.count = form.count.data
            item.condition = form.condition.data
            item.category = ItemCategory.query.get(form.category.data)
            item.location = ItemLocation.query.get(form.location.data)
            item.description = form.description.data
            item.date_checked = datetime.utcnow()

            db.session.commit()

        flash(gettext('flash.success.item.edited', item_name=item.name), 'success')
        return redirect(url_for('item.details', item_id=item.id))

    elif request.method == 'GET':
        form.name.data = item.name
        form.count.data = item.count
        form.condition.process_data(item.condition.name)
        form.category.process_data(item.category.id if item.category else None)
        form.location.process_data(item.location.id if item.location else None)
        form.description.data = item.description

    return render_template('item/edit.html', title=f'{item.name} ({gettext("ui.common.edit")})', item=item, form=form)


@item_blueprint.route('/items', methods=['GET', 'POST'])
@login_required
def overview():
    new_category_form = NewItemCategoryForm()
    new_location_form = NewItemLocationForm()

    if 'category_name' in request.form:
        if new_category_form.validate_on_submit():
            item_category = ItemCategory(name=new_category_form.category_name.data)
            db.session.add(item_category)
            db.session.commit()

            flash(gettext('flash.success.item_category.created', category_name=item_category.name), 'success')
            return redirect(url_for('item.overview'))

    elif 'location_name' in request.form:
        if new_location_form.validate_on_submit():
            item_location = ItemLocation(name=new_location_form.location_name.data)
            db.session.add(item_location)
            db.session.commit()

            flash(gettext('flash.success.item_location.created', location_name=item_location.name), 'success')
            return redirect(url_for('item.overview'))
        
    page = request.args.get('page', 1, type=int)
    pagination = Item.query.order_by(Item.name.collate('NOCASE').asc()).paginate(page=page, per_page=10)

    return render_template('item/overview.html',
                            title=gettext('page.item_overview.title'),
                            sidebar=gettext('ui.common.menu'),
                            pagination=pagination,
                            new_category_form=new_category_form,
                            new_location_form=new_location_form)


@item_blueprint.route('/items/new', methods=['GET', 'POST'])
@login_required
def new():
    form = ItemForm()
    form.category.choices = [(None, '')] + [(category.id, category.name) for category in ItemCategory.query.order_by(ItemCategory.name.collate('NOCASE').asc()).all()]
    form.location.choices = [(None, '')] + [(location.id, location.name) for location in ItemLocation.query.order_by(ItemLocation.name.collate('NOCASE').asc()).all()]

    if form.validate_on_submit():
        item = Item(name=form.name.data,
                count=form.count.data,
                condition=(form.condition.data if form.condition.data else ItemCondition.unknown),
                category=ItemCategory.query.get(form.category.data),
                location=ItemLocation.query.get(form.location.data),
                description=form.description.data)

        db.session.add(item)
        db.session.commit()

        flash(gettext('flash.success.item.created', item_name=item.name), 'success')
        return redirect(url_for('item.details', item_id=item.id))

    return render_template('item/new.html', title=gettext('page.item_new.title'), form=form)
