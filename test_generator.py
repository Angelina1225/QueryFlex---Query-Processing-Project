def test_generator():
    num = input("Query number(Give a number from 1 - 6): ")
    import subprocess
    import io
    import contextlib
    import importlib.util

    subprocess.run(["python", "generator.py", num], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["python", "sql.py", num], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    spec = importlib.util.spec_from_file_location("_generated", "_generated.py")
    generated_module = importlib.util.module_from_spec(spec)

    with contextlib.redirect_stdout(io.StringIO()):
        spec.loader.exec_module(generated_module)
        esql = generated_module.query()

    from sql import query as sql_query
    with contextlib.redirect_stdout(io.StringIO()):
        sql = sql_query(num, print_output=False)

    from sql import query as sql_query
    sql = sql_query(num, print_output=False)

    esql_data = [line.strip() for line in esql.strip().split('\n') if line.strip()]
    sql_data = [line.strip() for line in sql.strip().split('\n') if line.strip()]

    esql_results = [line for i, line in enumerate(esql_data) if i > 2 and i % 2 == 1]
    sql_results = [line for i, line in enumerate(sql_data) if i > 2 and i % 2 == 1]

    assert sorted(esql_results) == sorted(sql_results)
