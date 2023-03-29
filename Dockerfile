
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7
ENV PYTHONUNBUFFERED 1

EXPOSE 3000
WORKDIR /app
COPY ./app /app/app
COPY app/requirements.txt .


# Python install
RUN pip install --upgrade pip
RUN pip install -r requirements.txt --no-cache-dir
COPY app /app /app/

# Running API server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3000"]


