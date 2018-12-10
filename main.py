from sql import Sql, tpch_8_query
from collections import Counter

import pandas as pd
import plot as plt

GRID_SIZE = 30
TPCH_QUERY = '8'

columns = ['foo', 'bar', 'plan', 'cost', 'plan_id', 'color', 'coverage']

db = Sql(TPCH_QUERY, (GRID_SIZE,GRID_SIZE))
p1, p2 = db.get_partitions()

plans = []
i = 0
j = 0
rows_list = []
for s in p1:
    i += 1
    j = 0
    for l in p2:
        j += 1
        dict_tpch_params = {'foo': s, 'bar': l}
        tpch_query = db.query['query']

        # Get plans without COST information
        query = 'EXPLAIN (FORMAT JSON, COSTS FALSE ) ' + tpch_query
        results = db.execute_query(query, dict_tpch_params)
        dict_row = {}
        for result in results:
            plan = str(result)
            plans.append(plan)
            dict1 = {'foo':i, 'bar':j, 'plan':plan}
            dict_row.update(dict1)

        # Get plans with COST information
        query = 'EXPLAIN (FORMAT JSON) ' + tpch_query
        results = db.execute_query(query, dict_tpch_params)
        for result in results:
            cost = result[0][0]['Plan']['Total Cost']
            dict2 = {'cost':cost}
            dict_row.update(dict2)
        rows_list.append(dict_row)

df = pd.DataFrame(rows_list)

plt.plot(df, db.query['base_relations'])

