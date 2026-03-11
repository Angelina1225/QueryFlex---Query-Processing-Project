"""
    Program: MF Query Processor
    Author: Angelina Mande & Raj Kumar Pulgari
"""

sales_table_schema = {
    "cust": ["char", 20],
    "prod": ["char", 20],
    "day": "int",
    "month": "int",
    "year": "int",
    "state": ["char", 2],
    "quant": "int",
    "date": "date"
}
sales_table_columns = ["cust", "prod", "day", "month", "year", "state", "quant", "date"]
mf_struct_header = []
mf_table = [] #Store the Output of the result

# ************************* Print Table Rows Test Function **************************
def print_table_rows():
    print("******************** \n    MF Table \n********************")

    data = []

    # Iterate through each row in mf_table
    for row in mf_table:
        new_row = []

        # For each column in the header, get the corresponding value from the row
        for header in mf_struct_header:
            if header in row:
                new_row.append(row[header])  # Append the value under the correct column
            else:
                new_row.append('NULL')  # If a column doesn't exist in the row, append an empty string

        data.append(new_row)

    return data


# ************************* Get MF Structure  **************************
def get_mf_structure(phi):
    print("********************\n     MF Structure \n********************")
    print("struct {")

    # Loop through each attribute in V
    for col_name in phi["V"]:
        if col_name in sales_table_schema:
            col_def = sales_table_schema[col_name]
            if isinstance(col_def, list):
                col_type, col_size = col_def
            else:
                col_type, col_size = col_def, None # no size for int/date types

        if col_type == "char":
            print(f"       {col_type}   {col_name} [{col_size}];")
        else:
            print(f"       {col_type}    {col_name};")
        mf_struct_header.append(col_name)

    # Add aggregation attributes
    for agg in phi["F-VECT"]:
        col_name = agg["name"]
        col_type = "int"
        print(f"       {col_type}    {col_name};")
        mf_struct_header.append(col_name)

    print("} mf_struct [10000]\n")

# ************************* Lookup Current Row against MF Struct **************************
def lookup(row, indeces):
    #Find the index attribute from the grouping attribute(s) in the table_schema
    if len(mf_table) == 0:
        return [-1, -1]
    else:
        for mf_row_idx in range(len(mf_table)):
            match = 0
            for i in range(len(indeces)):
                index = indeces[i]
                if mf_table[mf_row_idx][mf_struct_header[i]] == row[index]:
                    match += 1
                else:
                    break
            if match == len(indeces):
                return [match, mf_row_idx]
        return [-1, -1]

# ************************* Add Current Row **************************
def add_row(row, indeces):
    mf_index = 0
    new_row = {}
    for index in indeces:
        new_row[mf_struct_header[mf_index]] = row[index]
        mf_index += 1
    mf_table.append(new_row)
