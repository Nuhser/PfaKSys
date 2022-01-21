from datetime import datetime
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_babel import gettext
from flask_login import login_required

from PfaKSys import db
from PfaKSys.item.forms import ItemForm, ItemCategoryForm, ItemLocationForm
from PfaKSys.item.item_condition import ItemCondition
from PfaKSys.models import Item, ItemCategory, ItemLocation


item_blueprint = Blueprint('item', __name__)


@item_blueprint.route('/categories', methods=['GET', 'POST'])
@login_required
def categories():
    new_category_form = ItemCategoryForm()    
    if 'category_name' in request.form:
        if new_category_form.validate_on_submit():
            item_category = ItemCategory(name=new_category_form.category_name.data)
            db.session.add(item_category)
            db.session.commit()

            flash(gettext('flash.success.item_category.created', category_name=item_category.name), 'success')
            return redirect(url_for('item.categories'))

    page = request.args.get('page', 1, type=int)
    pagination = ItemCategory.query.order_by(ItemCategory.name.collate('NOCASE').asc()).paginate(page=page, per_page=10)

    return render_template('item/categories.html',
                            title=gettext('page.item_categories.title'),
                            sidebar=gettext('ui.common.menu'),
                            pagination=pagination,
                            new_category_form=new_category_form)


@item_blueprint.route('/items/<int:item_id>/delete', methods=['POST'])
@login_required
def delete(item_id):
    item = Item.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()

    flash(gettext('flash.success.item.deleted', item_name=item.name), 'success')
    return redirect(url_for('item.overview'))


@item_blueprint.route('/categories/<int:category_id>/delete', methods=['POST'])
@login_required
def delete_category(category_id):
    category = ItemCategory.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()

    flash(gettext('flash.success.category.deleted', category_name=category.name), 'success')
    return redirect(url_for('item.categories'))


@item_blueprint.route('/locations/<int:location_id>/delete', methods=['POST'])
@login_required
def delete_location(location_id):
    location = ItemLocation.query.get_or_404(location_id)
    db.session.delete(location)
    db.session.commit()

    flash(gettext('flash.success.location.deleted', location_name=location.name), 'success')
    return redirect(url_for('item.locations'))


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

            item.has_count = form.has_count.data
            item.count = form.count.data
            item.condition = form.condition.data
            item.category = ItemCategory.query.get(form.category.data)
            item.location = ItemLocation.query.get(form.location.data)
            item.description = form.description.data
            item.comment = form.comment.data
            item.date_checked = datetime.utcnow()

            db.session.commit()

        flash(gettext('flash.success.item.edited', item_name=item.name), 'success')
        return redirect(url_for('item.details', item_id=item.id))

    elif request.method == 'GET':
        form.name.data = item.name
        form.has_count.data = item.has_count
        form.count.data = item.count
        form.condition.process_data(item.condition.name)
        form.category.process_data(item.category.id if item.category else None)
        form.location.process_data(item.location.id if item.location else None)
        form.description.data = item.description
        form.comment.data = item.comment

    return render_template('item/edit.html', title=f'{item.name} ({gettext("ui.common.edit")})', item=item, form=form)


@item_blueprint.route('/categories/<int:category_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_category(category_id):
    category = ItemCategory.query.get_or_404(category_id)

    form = ItemCategoryForm()
    form.category_id = category_id

    if form.validate_on_submit():
        category.name = form.category_name.data
        db.session.commit()

        flash(gettext('flash.success.category.edited', category_name=category.name), 'success')
        return redirect(url_for('item.categories'))

    elif request.method == 'GET':
        form.category_name.data = category.name

    return render_template('category/edit.html', title=f'{category.name} ({gettext("ui.common.edit")})', form=form)


@item_blueprint.route('/locations/<int:location_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_location(location_id):
    location = ItemLocation.query.get_or_404(location_id)

    form = ItemLocationForm()
    form.location_id = location_id

    if form.validate_on_submit():
        location.name = form.location_name.data
        db.session.commit()

        flash(gettext('flash.success.location.edited', location_name=location.name), 'success')
        return redirect(url_for('item.locations'))

    elif request.method == 'GET':
        form.location_name.data = location.name

    return render_template('location/edit.html', title=f'{location.name} ({gettext("ui.common.edit")})', form=form)


@item_blueprint.route('/locations', methods=['GET', 'POST'])
@login_required
def locations():
    new_location_form = ItemLocationForm()
    if 'location_name' in request.form:
        if new_location_form.validate_on_submit():
            item_location = ItemLocation(name=new_location_form.location_name.data)
            db.session.add(item_location)
            db.session.commit()

            flash(gettext('flash.success.item_location.created', location_name=item_location.name), 'success')
            return redirect(url_for('item.locations'))

    page = request.args.get('page', 1, type=int)
    pagination = ItemLocation.query.order_by(ItemLocation.name.collate('NOCASE').asc()).paginate(page=page, per_page=10)

    return render_template('item/locations.html',
                            title=gettext('page.item_locations.title'),
                            sidebar=gettext('ui.common.menu'),
                            pagination=pagination,
                            new_location_form=new_location_form)


@item_blueprint.route('/items', methods=['GET', 'POST'])
@login_required
def overview():
    new_category_form = ItemCategoryForm()
    new_location_form = ItemLocationForm()

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
    filter_categories = request.args.getlist('categories', type=int)
    filter_locations = request.args.getlist('locations', type=int)

    pagination = Item.query

    if (filter_categories != None) and (len(filter_categories) > 0):
        pagination = pagination.filter(Item.category_id.in_(filter_categories))

    if (filter_locations != None) and (len(filter_locations) > 0):
        pagination = pagination.filter(Item.location_id.in_(filter_locations))

    pagination = pagination.order_by(Item.name.collate('NOCASE').asc()).paginate(page=page, per_page=10)

    return render_template('item/overview.html',
                            title=gettext('page.item_overview.title'),
                            sidebar=gettext('ui.common.menu'),
                            filter_categories=filter_categories,
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
                has_count=form.has_count.data,
                count=form.count.data,
                condition=(form.condition.data if form.condition.data else ItemCondition.unknown),
                category=ItemCategory.query.get(form.category.data),
                location=ItemLocation.query.get(form.location.data),
                description=form.description.data,
                comment=form.comment.data)

        db.session.add(item)
        db.session.commit()

        flash(gettext('flash.success.item.created', item_name=item.name), 'success')
        return redirect(url_for('item.details', item_id=item.id))

    return render_template('item/new.html', title=gettext('page.item_new.title'), form=form)
