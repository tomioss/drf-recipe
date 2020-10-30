from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import TestCase

from unittest.mock import patch


class CommandTests(TestCase):

    def test_wait_for_db_ready(self):
        '''
        Test waiting for db when db is available
        '''
        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            gi.return_value = True
            call_command('wait_for_db')

            self.assertEqual(gi.call_count, 1)
