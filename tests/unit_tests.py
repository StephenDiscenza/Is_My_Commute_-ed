
def fetch_mta_alerts(mta_data_helpers):
    # This depends on there being at least one commute in the database. 
    # It probably makes sense to insert a test commute with id 1 when the db is created
    alerts = mta_data_helpers.get_commute_alets(1)
    assert type(alerts) == list