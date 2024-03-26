FROM iloveonsen/fastapi-llamacpp-conda:latest

COPY . /app
WORKDIR /app

EXPOSE 8003

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003"]