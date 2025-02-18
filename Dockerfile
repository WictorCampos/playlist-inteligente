FROM python:3.12

WORKDIR /app

COPY requirements.txt setup.py /app/

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY src /app/src

ENV PYTHONPATH=/app/src

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
