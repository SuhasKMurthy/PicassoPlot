from sql import Sql, tpch_8_query, DATABASE
from collections import Counter

import pandas as pd
import plot as plt

GRID_SIZE = 30
#GRID_SIZE = 100
#TPCH_QUERY = '9'
TPCH_QUERY = '8'
#TPCH_QUERY = '7'

columns = ['foo', 'bar', 'plan', 'cost', 'plan_id', 'color', 'coverage']
plan_file_prefix = './plan_log/q'+str(TPCH_QUERY)+'_g'+str(GRID_SIZE)+'_'+DATABASE+'_i_'

db = Sql(TPCH_QUERY, (GRID_SIZE,GRID_SIZE))
print("Getting partition")
p1, p2 = db.get_partitions()

plans = []
i = 0
j = 0
rows_list = []
for s in p1:
    i += 1
    j = 0
    print("p1 bin", i)
    for l in p2:
        j += 1
        dict_tpch_params = {'foo': s, 'bar': l}
        tpch_query = db.query['query']

        # Get plans without COST information
        query = 'EXPLAIN (FORMAT JSON, COSTS FALSE ) ' + tpch_query
        results = db.execute_query(query, dict_tpch_params)
        dict_row = {}
        for result in results:
            #print(result)
            #print(result[0][0]['Plan'])
            plan = str(result[0][0]['Plan']).replace(str(s),"").replace(str(l),"")
            #print(plan)
            plans.append(plan)
            dict1 = {'foo':i, 'bar':j, 'plan':plan, 'plan_raw': result[0][0]['Plan']}
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

plt.plot(df, db.query['base_relations'], plan_file_prefix)

