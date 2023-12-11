FROM python:3.9 as requirements-stage
WORKDIR /tmp
RUN pip install poetry==1.4.2
COPY ./pyproject.toml ./poetry.lock* /tmp/
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes


FROM python:3.9
WORKDIR /backend
RUN pip install poetry==1.4.2
COPY --from=requirements-stage /tmp/requirements.txt ./backend/requirements.txt
RUN pip install --upgrade -r ./backend/requirements.txt
COPY . .
# CMD ["python", "-m", "uvicorn", "--host", "0.0.0.0", "--port", "8000", "main:app", "--reload"]
# CMD ["gunicorn", "main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
CMD ["python", "start.py"]
