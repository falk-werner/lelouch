# Development Workflow

- https://packaging.python.org/en/latest/tutorials/packaging-projects/


## Build Docker Image

```bash
docker build -t lelouch .
```

## Run Tests

Once before test, install `pytest`:

```bash
python3 -m pip install pytest
```

Run tests:

```bash
pytest --rootdir tests
```
