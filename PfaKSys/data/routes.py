from flask import Blueprint
from flask_login import login_required

from PfaKSys.main.permissions import Permission, permission_required


data_blueprint = Blueprint('data', __name__)


@data_blueprint.route('/import_data', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.data_import)
def import_data():
    pass
