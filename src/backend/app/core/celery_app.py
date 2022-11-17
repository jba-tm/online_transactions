from celery import Celery, Task
from app.conf.config import settings
from app.db.session import SessionLocal

celery_app = Celery("worker", broker=settings.REDIS_URL)

celery_app.autodiscover_tasks([
    'app.contrib.transaction.tasks',
])


class DatabaseTask(Task):
    # _session = None

    @staticmethod
    def get_session():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    # @property
    # def session(self):
    #     db = SessionLocal()
    #     try:
    #         yield db
    #     finally:
    #         db.close()
        # if self._session is None:
        #     self._session = SessionLocal()
        # return self._session

    # @session.setter
    # def session(self, value):
    #     self._session = value

celery_app.conf.task_routes = {"app.worker.test_celery": "main-queue"}
