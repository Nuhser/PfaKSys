from flask_wtf import FlaskForm
from pandas import isnull

from PfaKSys import db
from PfaKSys.item.item_condition import ItemCondition
from PfaKSys.models import Item, ItemCategory, ItemLocation


def from_excel_file(excel_data: dict, excel_form: FlaskForm) -> tuple[list, list, list]:
    new_items = []
    new_categories = []
    new_locations = []

    condition_mapping = {}
    for field in excel_form._fields:
        if field.startswith('condition_'):
            condition_mapping[excel_form._fields[field].label.text] = excel_form._fields[field].data

    category_mapping = {}
    for field in excel_form._fields:
        if field.startswith('category_'):
            category_mapping[excel_form._fields[field].label.text] = excel_form._fields[field].data

    location_mapping = {}
    for field in excel_form._fields:
        if field.startswith('location_'):
            location_mapping[excel_form._fields[field].label.text] = excel_form._fields[field].data

    for i in range(len(excel_data['name'])):
        # get name
        name = list(excel_data['name'].values())[i]

        if isnull(name):
            continue

        j = 1
        while Item.query.filter_by(name=name).first():
            name = f'{list(excel_data["name"].values())[i]} ({j})'
            j += 1

        # get quantity
        has_count = not isnull(list(excel_data['quantity'].values())[i])
        quantity = int(list(excel_data['quantity'].values())[i]) if has_count else 0

        # get condition
        condition_name = list(excel_data['condition'].values())[i]
        condition = condition_mapping[condition_name] if not isnull(condition_name) else ItemCondition.unknown

        # get description and comment
        description = list(excel_data['description'].values())[i]
        comment = list(excel_data['comment'].values())[i]

        # get category
        category_name = list(excel_data['category'].values())[i]
        if isnull(category_name):
            category = None
        else:
            if category_mapping[category_name] == 'None':
                if ItemCategory.query.filter_by(name=category_name).first():
                    category = ItemCategory.query.filter_by(name=category_name).first()
                else:
                    category = ItemCategory(name=category_name)
                    db.session.add(category)
                    db.session.commit()

                    new_categories.append((category.id, category.name))
            else:
                category = ItemCategory.query.get(int(category_mapping[category_name]))

        # get location
        location_name = list(excel_data['location'].values())[i]
        if isnull(location_name):
            location = None
        else:
            if location_mapping[location_name] == 'None':
                if ItemLocation.query.filter_by(name=location_name).first():
                    location = ItemLocation.query.filter_by(name=location_name).first()
                else:
                    location = ItemLocation(name=location_name)
                    db.session.add(location)
                    db.session.commit()

                    new_locations.append((location.id, location.name))
            else:
                location = ItemLocation.query.get(int(location_mapping[location_name]))

        item = Item(
            name=name,
            has_count=has_count,
            count=quantity,
            condition=condition,
            category=category,
            location=location,
            description=description if not isnull(description) else '',
            comment=comment if not isnull(comment) else ''
        )

        db.session.add(item)
        db.session.commit()

        new_items.append((item.id, item.name))

    return new_items, new_categories, new_locations
