from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError
import time

class Command(BaseCommand):
    """Django command to pause execution until database is available"""

    def handle(self, *args, **options):
        self.stdout.write('Waiting for database...')
        db_conn = None
        while not db_conn:
            try:
                # Try to get the default database connection
                # https://stackoverflow.com/questions/32098797/how-can-i-check-database-connection-to-mysql-in-django
                db_conn = connections['default'].cursor()
            except OperationalError:
                # If connection failed, print a message and wait a bit before retrying
                self.stdout.write('Database unavailable, waiting 3 seconds...')
                time.sleep(3)
        self.stdout.write(self.style.SUCCESS('Database available!'))