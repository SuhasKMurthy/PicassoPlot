from sql import Sql, tpch_8_query
from collections import Counter

import pandas as pd
import plot as plt

GRID_SIZE = 10

columns = ['s_acctbal_partition', 'l_quantity_partition', 'plan', 'cost', 'plan_id', 'color', 'coverage']

db = Sql((GRID_SIZE,GRID_SIZE))
s_acctbal_divisions, l_quantity_divisions = db.get_partitions()
plans = []
i = 0
j = 0
rows_list = []
for s in s_acctbal_divisions:
    i += 1
    j = 0
    for l in l_quantity_divisions:
        j += 1
        dict_tpch_8 = {'acc1': s, 'quan1': l}

        # Get plans without COST information
        query = 'EXPLAIN (FORMAT JSON, COSTS FALSE ) ' + tpch_8_query
        results = db.execute_query(query, dict_tpch_8)
        dict_row = {}
        for result in results:
            plan = str(result)
            plans.append(plan)
            dict1 = {'s_acctbal_partition':i, 'l_quantity_partition':j, 'plan':plan}
            dict_row.update(dict1)

        # Get plans with COST information
        query = 'EXPLAIN (FORMAT JSON) ' + tpch_8_query
        results = db.execute_query(query, dict_tpch_8)
        for result in results:
            cost = result[0][0]['Plan']['Total Cost']
            dict2 = {'cost':cost}
            dict_row.update(dict2)
        rows_list.append(dict_row)

df = pd.DataFrame(rows_list)

plt.plot(df)

