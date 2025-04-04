import json
from contextlib import asynccontextmanager
from datetime import datetime # Import datetime
from fastapi import FastAPI, Request, Depends, HTTPException # Added Depends, HTTPException
from fastapi.responses import HTMLResponse # Added for HTML response
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlmodel import SQLModel, Session, select # Added Session and select
from pathlib import Path
from .core.database import engine, get_session # Added get_session
from .models.function_def import FunctionDef # Added FunctionDef
from .models.object_schema import ObjectSchema # Added ObjectSchema
from .models.table_data import TableData # Added TableData
from .api.v1.endpoints import objects, tables, functions, test_cases
from typing import List # Added List

# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    print("Creating database tables...")
    create_db_and_tables()
    print("Database tables created.")
    create_sample_data() # Call the new function
    yield
    # Shutdown logic (if any)
    print("Shutting down...")

# Create FastAPI app with lifespan manager
app = FastAPI(
    title="Schema & Process Management API",
    description="API for managing Objects, Tables, Functions, and TestCases",
    version="1.0.0",
    lifespan=lifespan
)

# Setup templates
templates = Jinja2Templates(directory="templates")

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(objects.router, prefix="/api/v1")
app.include_router(tables.router, prefix="/api/v1")
app.include_router(functions.router, prefix="/api/v1")
app.include_router(test_cases.router, prefix="/api/v1")

# Create tables on startup
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# Function to create sample data
def create_sample_data():
    with Session(engine) as session:
        # --- Create/Get Sample Objects ---
        # Check for Sample Customer
        statement_customer = select(ObjectSchema).where(ObjectSchema.name == "Sample Customer")
        customer = session.exec(statement_customer).first()
        if not customer:
            customer = ObjectSchema(
                name="Sample Customer",
                description="A standard customer profile.",
                attributes={"email": "customer@example.com", "tier": "Gold"} # Base attributes
            )
            session.add(customer)
            print("Added Sample Customer.")
        else:
             print("Found existing Sample Customer.")

        # Check for Sample Product
        statement_product = select(ObjectSchema).where(ObjectSchema.name == "Sample Product")
        product = session.exec(statement_product).first()
        if not product:
            product = ObjectSchema(
                name="Sample Product",
                description="A standard product item.",
                 # Base attributes - specific tables might have more/different ones
                attributes={"sku": "PROD-XXX", "price": 0.00, "in_stock": False}
            )
            session.add(product)
            print("Added Sample Product.")
        else:
            print("Found existing Sample Product.")

        # Commit here to ensure objects have IDs before creating tables
        session.commit()
        # Refresh objects to get IDs assigned by the database
        if customer: session.refresh(customer)
        if product: session.refresh(product)
        print("Committed/Refreshed sample objects.")


        # --- Add Sample Table Data ---
        needs_table_commit = False

        # Sample Customer Table
        if customer and customer.id: # Check if customer object exists and has an ID
            customer_table_name = "Sample Customer Data"
            statement_cust_table = select(TableData).where(TableData.name == customer_table_name)
            existing_cust_table = session.exec(statement_cust_table).first()
            if not existing_cust_table:
                customer_rows = [
                    {"email": "alice@example.com", "tier": "Silver"},
                    {"email": "bob@example.com", "tier": "Gold"},
                    {"email": "charlie@example.com", "tier": "Bronze"},
                ]
                cust_table = TableData(
                    name=customer_table_name,
                    description="A few sample customer records.",
                    object_id=customer.id,
                    data=customer_rows
                )
                session.add(cust_table)
                print(f"Adding sample table: {customer_table_name}")
                needs_table_commit = True
            else:
                print(f"Sample table '{customer_table_name}' already exists.")
        else:
             print(f"Skipping sample customer table creation (Customer object missing or has no ID).")


        # Sample Bookstore Product Table
        if product and product.id: # Check if product object exists and has an ID
            book_table_name = "Bookstore Products"
            statement_book_table = select(TableData).where(TableData.name == book_table_name)
            existing_book_table = session.exec(statement_book_table).first()
            if not existing_book_table:
                book_rows = [
                    {"sku": "BOOK-001", "price": 19.95, "in_stock": True, "title": "The SQL Enigma"},
                    {"sku": "BOOK-002", "price": 24.50, "in_stock": False, "title": "Pythonic Patterns"},
                    {"sku": "BOOK-003", "price": 15.00, "in_stock": True, "title": "API Adventures"},
                ]
                # Note: 'title' might not be in the base 'Sample Product' object schema's attributes.
                # The TableData.data field stores arbitrary JSON, but validation against
                # the linked ObjectSchema might occur elsewhere (e.g., in API endpoints).
                book_table = TableData(
                    name=book_table_name,
                    description="Sample products for a bookstore.",
                    object_id=product.id,
                    data=book_rows
                )
                session.add(book_table)
                print(f"Adding sample table: {book_table_name}")
                needs_table_commit = True
            else:
                print(f"Sample table '{book_table_name}' already exists.")
        else:
             print(f"Skipping sample bookstore table creation (Product object missing or has no ID).")


        # Sample Jewelry Product Table
        if product and product.id: # Check if product object exists and has an ID
            jewelry_table_name = "Jewelry Products"
            statement_jewelry_table = select(TableData).where(TableData.name == jewelry_table_name)
            existing_jewelry_table = session.exec(statement_jewelry_table).first()
            if not existing_jewelry_table:
                jewelry_rows = [
                    {"sku": "JEWEL-N1", "price": 199.99, "in_stock": True, "material": "Silver", "gemstone": "Sapphire"},
                    {"sku": "JEWEL-R1", "price": 499.50, "in_stock": True, "material": "Gold", "gemstone": "Diamond"},
                    {"sku": "JEWEL-E1", "price": 99.00, "in_stock": False, "material": "Platinum", "gemstone": None},
                ]
                 # Note: 'material', 'gemstone' might not be in the base 'Sample Product' object schema's attributes.
                jewelry_table = TableData(
                    name=jewelry_table_name,
                    description="Sample products for a jewelry store.",
                    object_id=product.id,
                    data=jewelry_rows
                )
                session.add(jewelry_table)
                print(f"Adding sample table: {jewelry_table_name}")
                needs_table_commit = True
            else:
                print(f"Sample table '{jewelry_table_name}' already exists.")
        else:
             print(f"Skipping sample jewelry table creation (Product object missing or has no ID).")


        if needs_table_commit:
            session.commit()
            print("Committed sample table data.")
        else:
            print("No new sample table data to commit.")

# Root endpoint to serve the main navigation page
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Endpoint to serve the object creation form
@app.get("/object/create", response_class=HTMLResponse)
async def get_object_create_form(request: Request):
    return templates.TemplateResponse("object_create.html", {"request": request})

# Endpoint to serve the object list page
@app.get("/objects", response_class=HTMLResponse)
async def get_objects_list_page(request: Request):
    return templates.TemplateResponse("objects_list.html", {"request": request})

# Edit an object
@app.get("/object/edit/{object_id}", response_class=HTMLResponse)
async def get_object_edit_page(request: Request, object_id: int, session: Session = Depends(get_session)):
    object_data = session.get(ObjectSchema, object_id)
    # return 404 if not exist
    if not object_data:
        return templates.TemplateResponse("404.html", {"request": request})
    # Handle case where object is not found
    if not object_data:
        raise HTTPException(status_code=404, detail=f"Object with id {object_id} not found")
    return templates.TemplateResponse("object_edit.html", {"request": request, "object": object_data})

# Endpoint to serve the table creation form
@app.get("/table/create", response_class=HTMLResponse)
async def get_table_create_form(request: Request, session: Session = Depends(get_session)):
    # Fetch all objects to populate the dropdown
    statement = select(ObjectSchema)
    object_list = session.exec(statement).all()
    return templates.TemplateResponse("table_create.html", {"request": request, "objects": object_list})

# Endpoint to serve the table list page
@app.get("/tables", response_class=HTMLResponse)
async def get_tables_list_page(request: Request):
    # The actual data fetching is done by JavaScript in the template
    return templates.TemplateResponse("tables_list.html", {"request": request})

# Endpoint to serve the table edit form
@app.get("/table/edit/{table_id}", response_class=HTMLResponse)
async def get_table_edit_page(request: Request, table_id: int, session: Session = Depends(get_session)):
    # Fetch the specific table
    table_data = session.get(TableData, table_id)
    if not table_data:
        raise HTTPException(status_code=404, detail=f"Table with id {table_id} not found")

    # Fetch all objects to populate the dropdown
    statement = select(ObjectSchema)
    object_list = session.exec(statement).all()

    # Convert table_data to dict for JSON serialization
    table_data_dict = table_data.dict()

    # Manually convert datetime objects to ISO strings for JSON
    def default_serializer(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

    # Use json.dumps with the custom serializer, then json.loads to get a clean dict
    # This ensures all nested datetimes are handled.
    serializable_table_data_str = json.dumps(table_data_dict, default=default_serializer)
    serializable_table_data_dict = json.loads(serializable_table_data_str)


    return templates.TemplateResponse("table_edit.html", {
        "request": request,
        "table": table_data, # Pass the original object for direct field access (e.g., table.id)
        "table_json": serializable_table_data_dict, # Pass the fully JSON-serializable dict
        "objects": object_list
    })

# Endpoint to serve the test case creation form
@app.get("/test-case/create", response_class=HTMLResponse)
async def get_test_case_create_form(request: Request, session: Session = Depends(get_session)):
    # Fetch all functions to populate the dropdown
    statement = select(FunctionDef)
    function_list = session.exec(statement).all()
    return templates.TemplateResponse("test_case_create.html", {"request": request, "functions": function_list})