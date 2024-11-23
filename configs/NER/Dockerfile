FROM python:3.12

WORKDIR /app

RUN pwd && ls -al

COPY . .


RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

CMD ["uvicorn", "api.ner:app", "--host", "0.0.0.0", "--port", "8000"]
