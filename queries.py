import re

def get_input(file_path):
    with open(file_path, 'r') as file:
        lines = [line.strip() for line in file if line.strip()]

    esql = {
        "S": [],
        "n": 1,
        "V": [],
        "F-VECT": [],
        "SUCH-THAT": {},
        "HAVING": {}
    }

    line_idx = 0

    while line_idx < len(lines):
        line = lines[line_idx].strip().lower()
        #lower = line.lower()

        if "select attribute" in line:
            line_idx += 1
            esql["S"] = [x.strip() for x in lines[line_idx].split(',')]

        elif "number of grouping variable" in line:
            line_idx += 1
            esql["n"] = int(lines[line_idx].strip())

        elif "grouping attributes" in line:
            line_idx += 1
            esql["V"] = [x.strip() for x in lines[line_idx].split(',')]

        elif "f-vect" in line:
            line_idx += 1
            f_items = [x.strip() for x in lines[line_idx].split(',')]
            for aggF in f_items:
                # Accept alphanumeric group var names (e.g., A_sum_quant, Q1_avg_sales)
                match = re.match(r'([A-Za-z]\w*)_(sum|avg|count|max|min)_(\w+)', aggF)
                if match:
                    gvar, agg, attr = match.groups()
                    esql["F-VECT"].append({
                        "name": aggF,
                        "group_var": gvar,
                        "agg": agg,
                        "attribute": attr
                    })

        elif "select condition" in line:
            line_idx += 1
            i = 1
            while line_idx < len(lines) and not any(inp in lines[line_idx].lower() for inp in ["having", "select", "f-vect", "grouping", "number"]):
                match = re.match(r"([A-Za-z]\w*)\.(\w+)\s*=\s*(.+)", lines[line_idx])
                if match:
                    gvar, attr, value = match.groups()
                    value = value.strip()

                    # Parse value as list or quoted string or number
                    if value.startswith("[") and value.endswith("]"):
                        value = eval(value)
                    elif value.isdigit():
                        value = int(value)
                    elif (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
                        value = value[1:-1]
                    
                    esql["SUCH-THAT"][f"var{i}"] = {
                        "group_var": gvar,
                        "attribute": attr,
                        "value": value
                    }
                    i += 1
                line_idx += 1
            continue


        elif "having_condition" in line:
            line_idx += 1
            if line_idx < len(lines):
                condition = lines[line_idx].strip()
                if condition:
                    # Determine logic: OR or AND
                    if " or " in condition.lower():
                        logic = "OR"
                        conds = re.split(r"\s+or\s+", condition, flags=re.IGNORECASE)
                    elif " and " in condition.lower():
                        logic = "AND"
                        conds = re.split(r"\s+and\s+", condition, flags=re.IGNORECASE)
                    else:
                        logic = "AND"  # default fallback
                        conds = [condition]

                    esql["HAVING"] = {}

                    if logic:
                        esql["HAVING"]["logic"] = logic

                    for i, cond in enumerate(conds, 1):
                        match = re.match(r'(\w+)\s*(=|!=|>|<|>=|<=)\s*(.+)', cond.strip())
                        if match:
                            left, op, right = match.groups()
                            right = right.strip()

                            # If right is a digit, convert to int
                            if right.isdigit():
                                right = int(right)
                            esql["HAVING"][f"cond{i}"] = {
                                "left": left.strip(),
                                "op": op.strip(),
                                "right": right
                            }

        line_idx += 1

    return esql
