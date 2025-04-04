from setuptools import setup, find_packages

setup(
    name="objects-tables-functions-tests",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "sqlmodel",
        "python-multipart",
        "jinja2",
        "python-dotenv",
    ],
    extras_require={
        "test": [
            "pytest",
            "pytest-asyncio",
            "pytest-cov",
            "httpx",
        ],
    },
)
