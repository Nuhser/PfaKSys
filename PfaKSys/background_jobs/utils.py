import atexit

from flask import Blueprint
from threading import Thread


background_blueprint = Blueprint('background_jobs', __name__)

BACKGROUND_JOBS = {}


class BackgroundJob():
    def __init__(self, id: int, name: str):
        self._running = True
        self.id = id
        self.name = name
        BACKGROUND_JOBS[self.id] = self
        
    def run(self):
        while self._running:
            self.job()

    def terminate(self):
        self._running = False

    def job(self):
        '''
        This method contains the code which gets executed by the threads.\n
        Please overwrite it.
        '''
        pass


def start_jobs():
    for id in BACKGROUND_JOBS:
        job = BACKGROUND_JOBS[id]
        job_thread = Thread(None, job.run, job.name, daemon=True)
        job_thread.start()


def stop_jobs():
    for id in BACKGROUND_JOBS:
        job = BACKGROUND_JOBS[id]
        job.terminate()


atexit.register(stop_jobs)
