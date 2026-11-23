to run backend you have to from ./backend:
-docker compose up
-python -m uvicorn app.main:app --reload

## Tests

Product, user, and recipe API tests use the real routers and services with a
dedicated PostgreSQL database. The API runs in-process through FastAPI's
`TestClient`, so a separate Uvicorn process is not required. Image recognition
uses a deterministic fake classifier; image loading and validation use the
real image service.

From `backend`, run the complete test suite:

```powershell
python -m pytest tests -q
```

The pytest fixture reads the test-only database settings from `.env.test`,
starts a dedicated non-persistent PostgreSQL container, creates a clean schema,
wraps each test in a transaction, and removes the container afterward. Docker
Desktop must be running. No separate API server needs to be started.

Run the image-service unit tests without PostgreSQL using:

```powershell
python -m pytest tests/image_test.py -q
```
