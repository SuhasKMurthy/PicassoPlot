from sqlalchemy import create_engine
from sqlalchemy import text

dict_tpch_8 = {'acc1':10, 'quan1':10}
tpch_8_query = 'SELECT o_year, sum(case when nation = \'BRAZIL\' then volume else 0 end) / sum(volume) as mkt_share ' \
               'FROM ( SELECT extract(year from o_orderdate) as o_year, l_extendedprice * (1-l_discount) as volume, n2.n_name as nation ' \
               'FROM part, supplier, lineitem, orders, customer, nation n1, nation n2, region ' \
               'WHERE s_acctbal < :acc1 and l_quantity < :quan1 and p_partkey = l_partkey and s_suppkey = l_suppkey ' \
               'and l_orderkey = o_orderkey and o_custkey = c_custkey and c_nationkey = n1.n_nationkey ' \
               'and n1.n_regionkey = r_regionkey and r_name = \'AMERICA\' and s_nationkey = n2.n_nationkey ' \
               'and o_orderdate between date \'1995-01-01\' and date \'1996-12-31\' ' \
               'and p_type = \'ECONOMY ANODIZED STEEL\') as all_nations ' \
               'group by o_year ' \
               'order by o_year;'

divide_s_acctbal_query = 'SELECT ntile, min(s_acctbal), max(s_acctbal) ' \
                         'FROM ( SELECT s_acctbal, ntile(:num_partition_s_acctbal) over (order by s_acctbal) ' \
                         'FROM supplier) x ' \
                         'GROUP BY ntile ' \
                         'ORDER BY ntile'

divide_l_quantity_query = 'SELECT ntile, min(l_quantity), max(l_quantity) ' \
                         'FROM ( SELECT l_quantity, ntile(:num_partition_l_quantity) over (order by l_quantity) ' \
                         'FROM lineitem) x ' \
                         'GROUP BY ntile ' \
                         'ORDER BY ntile'

USER_NAME = 'skeshavamurt_645f18'
PASSWORD = 'b7549996ce'

class Sql:
    def __init__(self, query_grid_size):

        self.engine = create_engine('postgresql://'+USER_NAME+':'+PASSWORD+
                                    '@cs645-community-f18.cxbepp9iqfon.us-east-1.rds.amazonaws.com:5432/tpch_sf1')

        self.partition_acctbal, self.partition_lineitem = query_grid_size


    # this method is used to get partitions related to equiheight histograms for selectivity in the plans
    def get_partitions(self):
        dict_divide_s_acctbal = {'num_partition_s_acctbal': self.partition_acctbal}
        s_acctbal_divisions = []
        results = self.execute_query(divide_s_acctbal_query, dict_divide_s_acctbal)
        for _, _, max_partition in results:
            s_acctbal_divisions.append(max_partition)

        dict_divide_l_quantity = {'num_partition_l_quantity': self.partition_lineitem}
        l_quantity_divisions = []
        results = self.execute_query(divide_l_quantity_query, dict_divide_l_quantity)
        for _, _, max_partition in results:
            l_quantity_divisions.append(max_partition)

        return s_acctbal_divisions, l_quantity_divisions

    def execute_query(self, query_text, params):
        sql = text(query_text)
        results = self.engine.execute(sql, **params)
        return results