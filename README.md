
# Objects - Tables - Functions - Tests

A Python REST API project with template forms and default views.

There are for 4 main components.

There will be Object (or Schema) this will be the attributes and the attribute type.

There will be Tables (or Samples) this will be rows of data, where the columns are the attributes and this will be a table all of a single Object.

There will be Functions (or Processes) this will have a name, summary, and one or more input tables, and one or more output tables. This just defines the input and output objects really.

There will be TestCases (or Examples) this will have a name, summary and the same as a function but the tables will have sample data, rows. A TestCase is saying that "when this function is called with these input tables, it *should* produce these output tables".

How to use this API?

You can use the API by making HTTP requests to the endpoints defined in the API.

The API has the following endpoints:

/api/v1/objects: GET, POST, PUT, DELETE
/api/v1/tables: GET, POST, PUT, DELETE
/api/v1/functions: GET, POST, PUT, DELETE
/api/v1/test_cases: GET, POST, PUT, DELETE

You can use the endpoints to create, read, update, and delete objects, tables, functions, and test cases.

How to start the API?

You can start the API by running the following command:

```bash
python -m app.main
```

For development, you can use the following command:

```bash
python -m app.main --reload
```

or 

```bash
uvicorn app.main:app --reload
```

This will start the API on http://localhost:8000.

You can also use the API documentation by visiting http://localhost:8000/docs.

How to stop the API?

You can stop the API by pressing Ctrl+C in the terminal.
