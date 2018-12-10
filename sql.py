from sqlalchemy import create_engine
from sqlalchemy import text

#NATION1 = "UNITED STATES"
#NATION2 = "CHINA"
NATION1 = "FRANCE"
NATION2 = "GERMANY"


tpch_7_query = 'SELECT supp_nation, cust_nation, l_year, sum(volume) as revenue ' \
               'FROM(SELECT n1.n_name as supp_nation, n2.n_name as cust_nation, extract(year from l_shipdate) as l_year, ' \
                            'l_extendedprice * (1 - l_discount) as volume ' \
               'FROM supplier, lineitem, orders, customer, nation n1, nation n2 ' \
                    'WHERE s_suppkey = l_suppkey and o_orderkey = l_orderkey and c_custkey = o_custkey and o_orderkey < :foo and c_custkey < :bar ' \
                            'and s_nationkey = n1.n_nationkey and c_nationkey = n2.n_nationkey and ( ' \
                            '(n1.n_name = \''+NATION1+'\' and n2.n_name = \''+NATION2+'\') or (n1.n_name = \''+NATION2+'\' and n2.n_name = \''+NATION1+'\')) ' \
                            'and l_shipdate between date \'1992-01-01\' and date \'1999-12-31\') as shipping ' \
               'GROUP BY supp_nation, cust_nation, l_year ' \
               'ORDER BY supp_nation, cust_nation, l_year;'

def get_equal_height_histogram_query(column, table):
    return 'SELECT ntile, min({}), max({}) ' \
            'FROM ( SELECT {}, ntile(:num_partition) over (order by {}) ' \
            'FROM {}) x ' \
            'GROUP BY ntile ' \
            'ORDER BY ntile'.format(column, column, column, column, table)


dict_tpch_7 = {'query': tpch_7_query,
               'partition_queries': [('c_custkey', 'customer'), ('o_orderkey', 'orders')],
               'base_relations': ('ORDERS', 'CUSTOMER')}

tpch_8_query = 'SELECT o_year, sum(case when nation = \'BRAZIL\' then volume else 0 end) / sum(volume) as mkt_share ' \
               'FROM ( SELECT extract(year from o_orderdate) as o_year, l_extendedprice * (1-l_discount) as volume, n2.n_name as nation ' \
               'FROM part, supplier, lineitem, orders, customer, nation n1, nation n2, region ' \
               'WHERE s_acctbal < :foo and l_quantity < :bar and p_partkey = l_partkey and s_suppkey = l_suppkey ' \
               'and l_orderkey = o_orderkey and o_custkey = c_custkey and c_nationkey = n1.n_nationkey ' \
               'and n1.n_regionkey = r_regionkey and r_name = \'AMERICA\' and s_nationkey = n2.n_nationkey ' \
               'and o_orderdate between date \'1995-01-01\' and date \'1996-12-31\' ' \
               'and p_type = \'ECONOMY ANODIZED STEEL\') as all_nations ' \
               'group by o_year ' \
               'order by o_year;'

dict_tpch_8 = {'query': tpch_8_query,
               'partition_queries': [('s_acctbal', 'supplier'), ('l_quantity', 'lineitem')],
               'base_relations': ('SUPPLIER', 'LINEITEM')}


tpch_9_query = 'select nation, o_year, sum(amount) as sum_profit from (select n_name as nation, ' \
               'extract(year from o_orderdate) as o_year, l_extendedprice * (1 - l_discount) - ps_supplycost * l_quantity as amount ' \
               'from part, supplier, lineitem, partsupp, orders, nation ' \
               'where s_suppkey < :foo and ps_partkey < :bar and s_suppkey = l_suppkey and ps_suppkey = l_suppkey and ps_partkey = l_partkey and p_partkey = l_partkey' \
		'and o_orderkey = l_orderkey and s_nationkey = n_nationkey and p_name like \'%yellow%\') as profit ' \
                'group by nation, o_year ' \
                'order by nation, o_year desc;'
               
#'where s_suppkey < :foo and ps_suppkey < :foo and ps_partkey < :bar and p_partkey < :bar ' \

dict_tpch_9 = {'query': tpch_9_query,
               'partition_queries': [('s_suppkey', 'supplier'), ('ps_partkey', 'partsupp')],
               'base_relations': ('SUPPLIER', 'PARTSUPP')}

USER_NAME = 'skeshavamurt_645f18'
PASSWORD = 'b7549996ce'
HOST = 'cs645-community-f18.cxbepp9iqfon.us-east-1.rds.amazonaws.com:5432'
DATABASE = 'tpch_sf1'
DB_CONNECTION_STRING = 'postgresql://{}:{}@{}/{}'.format(USER_NAME,PASSWORD,HOST,DATABASE)

dict_tpch = {'7': dict_tpch_7, '8': dict_tpch_8, '9': dict_tpch_9}

class Sql:
    def __init__(self, tpch_query='8', query_grid_size=10):

        #self.engine = create_engine(DB_CONNECTION_STRING,connect_args={ 'use_batch_mode':True} )
        self.engine = create_engine(DB_CONNECTION_STRING )
        self.query = dict_tpch[tpch_query]
        self.partition1, self.partition2 = query_grid_size


    # this method is used to get partitions related to equiheight histograms for selectivity in the plans
    def get_partitions(self):
        part1, part2 = self.query['partition_queries']

        dict_divide_1 = {'num_partition': self.partition1}
        part1_divisions = []
        results = self.execute_query(get_equal_height_histogram_query(part1[0], part1[1]), dict_divide_1)
        for _, _, max_partition in results:
            part1_divisions.append(max_partition)

        dict_divide_2 = {'num_partition': self.partition2}
        part2_divisions = []
        results = self.execute_query(get_equal_height_histogram_query(part2[0], part2[1]), dict_divide_2)
        for _, _, max_partition in results:
            part2_divisions.append(max_partition)

        return part1_divisions, part2_divisions

    def execute_query(self, query_text, params):
        sql = text(query_text)
        results = self.engine.execute(sql, **params)
        return results
