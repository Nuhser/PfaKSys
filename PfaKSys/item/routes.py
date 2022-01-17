from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_babel import gettext
from flask_login import login_required

from PfaKSys import db
from PfaKSys.item.forms import NewItemForm
from PfaKSys.item.item_condition import ItemCondition
from PfaKSys.models import Item


item_blueprint = Blueprint('item', __name__)


@item_blueprint.route('/items/new', methods=['GET', 'POST'])
@login_required
def new():
    form = NewItemForm()

    if form.validate_on_submit():
        item = Item(name=form.name.data, count=form.count.data, condition=(form.condition.data if form.condition.data else ItemCondition.unknown), description=form.description.data)
        db.session.add(item)
        db.session.commit()

        flash(gettext('flash.success.item.created', item_name=item.name), 'success')
        return redirect(url_for('item.overview'))

    return render_template('item/new.html', title=gettext('page.item_new.title'), form=form)


@item_blueprint.route('/items/')
@login_required
def overview():
    page = request.args.get('page', 1, type=int)
    pagination = Item.query.order_by(Item.name.asc()).paginate(page=page, per_page=10)

    return render_template('item/overview.html', title=gettext('page.item_overview.title'), sidebar=gettext('ui.common.menu'), pagination=pagination)