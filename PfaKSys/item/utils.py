import os

from flask import current_app
from PIL import Image


def save_picture(form_picture) -> str:
    picture_name = form_picture.filename
    new_name = None
    fails = 0
    picture_path = os.path.join(current_app.root_path, 'static/item_images', picture_name)

    while (True):
        if os.path.isfile(picture_path):
            fails += 1
            new_name, ext = os.path.splitext(picture_name)
            new_name = f'{new_name}_{fails}{ext}'
            picture_path = os.path.join(current_app.root_path, 'static/item_images', new_name)
        else:
            picture_name = new_name if new_name else picture_name
            break

    item_image = Image.open(form_picture)
    item_image.save(picture_path)

    return picture_name