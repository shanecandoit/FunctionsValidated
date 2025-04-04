
# FunctionsValidated API: ObjectSchemas, DataSamples, FunctionSpecs, ValidationSets, and CodeSubmissions

A Python REST API project for managing data schemas, sample data sets, function specifications, validation examples, and code submissions. Includes basic template forms and default views for web interaction.

This project facilitates a workflow where function requirements (specifications and validation examples) can be defined separately from their implementations.

## Core Components

This API manages five core components related to defining, testing, and implementing data processing functions:

1. ObjectSchema:
    * Defines the structure (attributes and their data types) for a type of data.
    * Analogous to a C++ header (`.h`) or an interface, it specifies *what* data looks like.
    * Example: An `ObjectSchema` named "User" might define attributes like `user_id` (integer), `username` (string), `signup_date` (datetime).

2. DataSample:
    * Contains concrete rows of data where columns conform to a specific `ObjectSchema`.
    * Represents a collection of instances or a sample dataset based on a defined schema.
    * Example: A `DataSample` conforming to the "User" `ObjectSchema` might contain rows like `{'user_id': 101, 'username': 'alice', 'signup_date': '2023-10-26T10:00:00Z'}`.

3. FunctionSpec (Function Specification):
    * Defines the *specification* or *signature* of a data processing function.
    * It includes a name, summary, and specifies the required input `ObjectSchema`(s) and the expected output `ObjectSchema`(s).
    * It describes *what* a function should do in terms of data transformation types, but contains no implementation code.
    * Typically created by analysts, QAs, or system designers.
    * Example: A `FunctionSpec` named "AnonymizeUserData" might take an input `ObjectSchema` "RawUser" and produce an output `ObjectSchema` "AnonymizedUser".

4. ValidationSet:
    * Provides concrete examples to validate implementations of a `FunctionSpec`.
    * It links specific input `DataSample`(s) (with real data conforming to the FunctionSpec's input schemas) to the expected output `DataSample`(s) (also with real data conforming to the FunctionSpec's output schemas).
    * It asserts: "When the function specified by `FunctionSpec F` is executed with these input `DataSample`s, it *should* produce these output `DataSample`s".
    * Contains no implementation code.
    * Typically created alongside the `FunctionSpec` to define acceptance criteria.

5. CodeSubmission:
    * Contains the actual implementation code (or reference to it) provided by a developer attempting to fulfill a `FunctionSpec`.
    * Each submission is linked to one `FunctionSpec`.
    * It can be evaluated against the `ValidationSet`(s) associated with that specification to determine correctness (e.g., which `ValidationSet`s pass or fail for this specific code).

## How to Use This API?

You can interact with the API by making standard HTTP requests (GET, POST, PUT, DELETE) to the defined endpoints.

The primary API endpoints are expected to be structured like this (under `/api/v1/`):

* `/objectschemas/`: Manage `ObjectSchema` resources.
* `/datasamples/`: Manage `DataSample` resources.
* `/functionspecs/`: Manage `FunctionSpec` resources.
* `/validationsets/`: Manage `ValidationSet` resources (often linked to a `FunctionSpec`).
* `/codesubmissions/`: Manage `CodeSubmission` resources (linked to a `FunctionSpec`).

You can use these endpoints to create, read, update, and delete the respective resources. Detailed API documentation is available automatically.

## How to Start the API?

Prerequisites: Python 3.9+, pip

1. Clone the repository:

    ```bash
    git clone <your-repo-url>
    cd <your-repo-directory>
    ```

2. Create and activate a virtual environment (recommended):

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. Configure environment variables:
    * Copy `.env.example` to `.env`.
    * Edit `.env` to set your `DATABASE_URL` and any other required settings.
5. Run database migrations (if applicable):

    ```bash
    # Example if using Alembic:
    # alembic upgrade head
    ```

6. Start the development server:

    ```bash
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    ```

    * `--reload`: Automatically restarts the server when code changes.
    * `--host 0.0.0.0`: Makes the server accessible on your local network.
    * `--port 8000`: Specifies the port (default is often 8000).

The API should now be running on `http://localhost:8000` (or `http://<your-local-ip>:8000`).

## API Documentation

Once the API is running, you can access the interactive API documentation (Swagger UI) at:
`http://localhost:8000/docs`

## How to Stop the API?

Press `Ctrl+C` in the terminal where the `uvicorn` process is running.

## How to Run Tests?

You can run the automated tests and check code coverage using `pytest`:

```bash
pytest --cov=app tests/
