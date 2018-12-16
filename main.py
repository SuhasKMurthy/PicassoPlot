from sql import Sql, DATABASE
from collections import Counter

import pandas as pd
import plot as plt
import copy



#GRID_SIZE = 30
GRID_SIZE = 100
TPCH_QUERY = '9'
#TPCH_QUERY = '8'
#TPCH_QUERY = '7'

diff_mode = "par"
#diff_mode = "opt"

columns = ['foo', 'bar', 'plan', 'cost', 'plan_id', 'color', 'coverage']
plan_file_prefix = './plan_log/q'+str(TPCH_QUERY)+'_g'+str(GRID_SIZE)+'_'+DATABASE+'_d_'+diff_mode+'_i_'

db = Sql(TPCH_QUERY, (GRID_SIZE,GRID_SIZE))
print("Getting partition")
p1, p2 = db.get_partitions()


#keep_nodes_set = set(['Node Type', 'Plans', 'Relation Name', 'Parent Relationship', 'Strategy'])
keep_nodes_set = set(['Node Type', 'Plans', 'Strategy'])
def remove_parameters_from_plan(plan):
    if type(plan) == list:
        for element in plan:
            remove_parameters_from_plan(element)
        return
    if type(plan) == dict:
        for key in plan.keys():
            if key not in plan:
                continue
            if key not in keep_nodes_set:
                #plan.pop(key, None)
                plan.pop(key)
                continue
            if type(plan[key]) == dict or type(plan[key]) == list:
                remove_parameters_from_plan(plan[key])
        return

#plans = []
i = 0
j = 0
rows_list = []
print p1
print p2
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
        part1, part2 = db.query['partition_queries']
        replace_part1_prefix = part1[0]+" < "
        replace_part2_prefix = part2[0]+" < "
        for result in results:
            #print(result)
            #print(result[0][0]['Plan'])
            if diff_mode == "par":
                plan = str(result[0][0]['Plan']).replace("'","").replace(replace_part1_prefix+str(s),"").replace(replace_part2_prefix+str(l),"").replace(replace_part1_prefix+str(int(s)),"").replace(replace_part2_prefix+str(int(l)),"")
                dict1 = {'foo':i, 'bar':j, 'plan':plan, 'plan_raw': result[0][0]['Plan']}
            elif diff_mode == "opt":
                plan_dict = copy.deepcopy(result[0][0]['Plan'])
                remove_parameters_from_plan( plan_dict )
                plan = str(plan_dict)
                dict1 = {'foo':i, 'bar':j, 'plan':plan, 'plan_raw': plan_dict}

            #print(plan)
            #plans.append(plan)
            
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

