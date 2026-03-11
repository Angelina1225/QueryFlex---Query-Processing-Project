from queries import get_input

import sys
import subprocess

def main(num=None, print_output=True):
    if num is None:
        num = input("Query number(Give a number from 1 - 6): ")

    query = get_input(f"inputs/esql_Query{num}.txt")
    body = f"query = {query}"

    # This is the full generated program as a string
    template = f'''
import psycopg2
from tabulate import tabulate
from QueryProcessor import get_mf_structure, print_table_rows, lookup, add_row
from QueryProcessor import mf_table, sales_table_schema, mf_struct_header

sales_table_columns = ["cust", "prod", "day", "month", "year", "state", "quant", "date"]

def query():
    {body}

    connection = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="Angelina@1238",
        host="localhost",
        port="5432"
    )

    cursor = connection.cursor()
    cursor.execute("SELECT * FROM sales;")
    table_rows = cursor.fetchall()
    cursor.close()
    connection.close()

    # Get MF structure and print
    get_mf_structure(query)
    group_by_attributes = query["V"]
    
    # Get indices of grouping attributes (cust, prod)
    indeces = []
    for attr in group_by_attributes:
        indeces.append(sales_table_columns.index(attr))

    # First Table Scan: Populate the mf_table with distinct values of grouping attributes
    for row in table_rows:
        match = lookup(row, indeces)
        if match[0] == -1:
            add_row(row, indeces)

    # Second Table Scan: Calculate aggregates
    for agg in query["F-VECT"]:
        agg_name = agg["name"]
        agg_type = agg["agg"]
        agg_gv = agg["group_var"]
        attribute = agg["attribute"]

        # Separate predicates based on grouping variables
        group_predicates = {{}}
        for pred in query.get("SUCH-THAT", {{}}).values():
            if pred["group_var"] != agg_gv:
                continue
            key = pred["attribute"]
            if key not in group_predicates:
                group_predicates[key] = []
            value = pred["value"]
            if isinstance(value, list):
                group_predicates[key].extend(value)
            else:
                group_predicates[key].append(value)

        for row in table_rows:
            match = lookup(row, indeces)
            if match[0] > -1:
                pos = match[1]

                # Check all predicates for this group_var
                satisfied = True
                for attr, values in group_predicates.items():
                    allowed_vals = []
                    for val in values:
                        if val in sales_table_columns:
                            allowed_vals.append(row[sales_table_columns.index(val)])
                        else:
                            allowed_vals.append(int(val) if sales_table_schema[attr] == "int" else val)

                    if row[sales_table_columns.index(attr)] not in allowed_vals:
                        satisfied = False
                        break

                if not satisfied:
                    continue

                attribute_index = sales_table_columns.index(attribute)
                attr_value = row[attribute_index]
                current_value = mf_table[pos].get(agg_name, None)

                if agg_type == "sum":
                    mf_table[pos][agg_name] = current_value + attr_value if current_value else attr_value
                elif agg_type == "max":
                    mf_table[pos][agg_name] = max(current_value, attr_value) if current_value is not None else attr_value
                elif agg_type == "min":
                    mf_table[pos][agg_name] = min(current_value, attr_value) if current_value is not None else attr_value
                elif agg_type == "count":
                    mf_table[pos][agg_name] = current_value + 1 if current_value else 1
                elif agg_type == "avg":
                    sum_key = f"{{agg_name}}_sum"
                    count_key = f"{{agg_name}}_count"
                    mf_table[pos][sum_key] = mf_table[pos].get(sum_key, 0) + attr_value
                    mf_table[pos][count_key] = mf_table[pos].get(count_key, 0) + 1
                    mf_table[pos][agg_name] = mf_table[pos][sum_key] / mf_table[pos][count_key]

    if "HAVING" in query and len(query["HAVING"]) > 0:
        logic = query["HAVING"].get("logic", None)
        conditions = {{k: v for k, v in query["HAVING"].items() if k != "logic"}}

        filtered_table = []
        for row in mf_table:
            results = []
            for cond in conditions.values():
                # Extract left and right values                
                left = row.get(cond["left"], None)

                #right can be direct value or col
                if cond["right"] in row: 
                    right = row[cond["right"]]
                else:
                    col_type = sales_table_schema.get(left, "char")
                    if isinstance(cond["right"], str) and cond["right"].isdigit() and col_type == "int":
                        right = int(cond["right"])
                    else:
                        right = cond["right"]

                # Evaluate condition
                result = False
                if cond["op"] == "=":
                    result = left == right
                elif cond["op"] == "!=":
                    result = left != right
                elif cond["op"] == ">":
                    result = left > right
                elif cond["op"] == "<":
                    result = left < right
                elif cond["op"] == ">=":
                    result = left >= right
                elif cond["op"] == "<=":
                    result = left <= right

                results.append(result)

            # Combine all results with AND/OR logic
            if len(results) == 1:
                include = results[0]
            else:
                include = all(results) if logic == "AND" else any(results)

            if include:
                filtered_table.append(row)

        mf_table.clear()
        mf_table.extend(filtered_table)

    data = print_table_rows()
    return tabulate(data, headers=mf_struct_header, tablefmt="grid")

def main():
    print(query())

if __name__ == "__main__":
    main()
'''

    # Write to file
    with open("_generated.py", "w") as f:
        f.write(template)

    if print_output:
        subprocess.run(["python", "_generated.py"])
    else:
        subprocess.run(["python", "_generated.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1], print_output=False)
    else:
        main(print_output=True)
