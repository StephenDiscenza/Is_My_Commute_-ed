import app.database_helpers as db_helpers
import app.mta_data_helpers as mta_data_helpers
from tests import db_tests, unit_tests

class TestClass:
    def test_dbhelpers(self):
        db_tests.db_setup_test(db_helpers)

    def test_alerts(self):
        unit_tests.fetch_mta_alerts(mta_data_helpers)
