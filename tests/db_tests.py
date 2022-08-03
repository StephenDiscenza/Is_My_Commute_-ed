
def db_setup_test(db_helpers):
    db_helpers.setup_db()
    cxn = db_helpers.create_cxn_on_db('commute_check.db')
    cursor = cxn.cursor()
    result = cursor.execute('SELECT station_id from stations WHERE gtfs_stop_id = ?', ('R01',)).fetchall()[0][0]
    assert result == 1, f'The result for the query was {result} but 1 was expected'

