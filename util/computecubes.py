from util import covdb
cdb = covdb.CorrDB()
cdb.mark_updated()
cdb.populate_incidence_db()
cdb.compute_variances()