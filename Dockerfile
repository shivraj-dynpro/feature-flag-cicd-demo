# Feature Flag Service — minimal image for the demo.
FROM python:3.12-slim

# Don't write .pyc files; flush stdout/stderr immediately (nice for `docker logs`).
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Copy project metadata + source, then install (deps + the app package).
COPY pyproject.toml ./
COPY app ./app
RUN pip install --no-cache-dir .

EXPOSE 8000

# Run a non-root user.
RUN useradd --create-home appuser
USER appuser

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
