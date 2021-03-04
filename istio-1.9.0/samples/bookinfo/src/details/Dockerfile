FROM python:3.8.7-slim

COPY details.py /opt/microservices/
COPY requirements.txt /opt/microservices/

ARG service_version
ENV SERVICE_VERSION ${service_version:-v1}
ARG enable_external_book_service
ENV ENABLE_EXTERNAL_BOOK_SERVICE ${enable_external_book_service:-false}

EXPOSE 9080
WORKDIR /opt/microservices
RUN pip3 install -r requirements.txt

CMD ["python3", "details.py", "9080"]