import app.database_helpers as db_helpers
from tests import db_tests

class TestClass:
    def test_one(self):
        db_tests.db_setup_test(db_helpers)

