import atexit
import os
import shutil

from datetime import datetime

from PfaKSys import scheduler
from PfaKSys.models import SystemSettings


@scheduler.task('cron', id='database_backup', name='Database Backup', hour='4')
def database_backup():
    """
    This background job saves a backup of the database to the backups-folder every night at 4 o'clock and when PfaKSys is closed.
    It keeps the current backup plus as many backups as `database_backup_quantity` in the system settings says.
    """

    backup_path = os.path.join(scheduler.app.root_path, 'backups/db')

    # create backup folder if needed
    if not os.path.isdir(backup_path):
        os.makedirs(backup_path)

    # get max backups to keep from db
    with scheduler.app.app_context():
        system_settings = SystemSettings.query.first()
        backup_quantity = system_settings.database_backup_quantity

    # delete backups if there are to many
    backup_list = [os.path.join(backup_path, name) for name in os.listdir(backup_path) if os.path.isfile(os.path.join(backup_path, name))]
    while len(backup_list) > backup_quantity:
        oldest_backup = backup_list.pop(backup_list.index(min(backup_list, key=os.path.getctime)))
        os.remove(oldest_backup)

    # backup db
    shutil.copy(os.path.join(scheduler.app.root_path, 'db.sqlite'), os.path.join(backup_path, f'backup_{datetime.now().strftime("%d-%m-%Y_%H-%M-%S")}.sqlite'))

# save database when shutting down PfaKSys
atexit.register(database_backup)
