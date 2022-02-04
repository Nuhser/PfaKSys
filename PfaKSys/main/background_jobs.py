import os
import shutil

from PfaKSys import scheduler


@scheduler.task('cron', id='database_backup', name='Database Backup', hour='4')
def database_backup():
    backup_path = os.path.join(scheduler.app.root_path, 'backups')

    # create backup folder if needed
    if not os.path.isdir(backup_path):
        os.mkdir(backup_path)

    if not os.path.isfile(os.path.join(backup_path, 'db.sqlite')):
        shutil.copy(os.path.join(scheduler.app.root_path, 'db.sqlite'), os.path.join(backup_path, 'db.sqlite'))
