from flask import Blueprint, flash, redirect, render_template, url_for
from flask_babel import gettext
from flask_login import login_required

from PfaKSys import db
from PfaKSys.item.forms import NewItemForm
from PfaKSys.item.item_condition import ItemCondition
from PfaKSys.models import Item


item_blueprint = Blueprint('item', __name__)


@item_blueprint.route('/item/new', methods=['GET', 'POST'])
@login_required
def new():
    form = NewItemForm()

    if form.validate_on_submit():
        item = Item(name=form.name.data, count=form.count.data, condition=(form.condition.data if form.condition.data else ItemCondition.unknown), description=form.description.data)
        db.session.add(item)
        db.session.commit()

        flash(gettext('flash.success.item.created'), 'success')
        return redirect(url_for('main.home'))

    return render_template('item/new.html', title=gettext('page.item_new.title'), form=form)
