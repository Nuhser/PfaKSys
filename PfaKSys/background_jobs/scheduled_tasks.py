import time

from PfaKSys.background_jobs.utils import BackgroundJob, start_jobs


class PrintTest(BackgroundJob):
    def job(self):
        print('Foo')
        time.sleep(5)


# print_test = PrintTest(1, 'Print')
# start_jobs()
