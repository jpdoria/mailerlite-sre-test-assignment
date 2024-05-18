FROM python:3.11.9-slim
WORKDIR /src
COPY email_operator.py /src/
RUN pip install kopf kubernetes mailersend
CMD ["kopf", "run", "-A", "/src/email_operator.py"]
