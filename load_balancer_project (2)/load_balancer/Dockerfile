FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install flask
RUN apt update && apt install -y curl docker.io
EXPOSE 5000
CMD ["python", "balancer.py"]
