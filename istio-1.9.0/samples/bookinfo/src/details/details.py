"""
    Implementation of the Istio Details Microservice
"""
from __future__ import print_function
from flask_bootstrap import Bootstrap
from flask import Flask, request, jsonify, make_response
from urllib.parse import urlparse
import simplejson as json
import requests
import sys
import logging
import os
import asyncio
import uuid
import time

serviceUUID = "detailsservice-{}".format(uuid.uuid4().hex)

try:
    import http.client as http_client
except ImportError:
    import httplib as http_client

app = Flask(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.DEBUG)


app.secret_key = b'_5#y2L"F3Q9z\n\xec]/'

Bootstrap(app)


def generate_record(**kwargs):
    """
        Function used to generate a record if we are
        Attempting to trace
    """
    return {
        "message_name": kwargs["message_name"],
        "service": kwargs["service"],
        "timestamp": round(time.time() * 1000),
        "type": kwargs["type"],
        "uuid": kwargs["uuid"]
    }

@app.route("/health")
def health():
    return "Details is healthy"

@app.route("/details/<id>")
def details(id):
    FI_TRACE = True
    data = {}
    message_name = ""
    req_id = ""

    if request.headers.get("fi-trace"):
        FI_TRACE = True
        data = json.loads(request.headers.get("fi-trace"))
        message_name = data["records"][-1]["message_name"]
        req_id = data["records"][-1]["uuid"]

    if FI_TRACE:
        data["records"].append(generate_record(uuid=req_id, type=2, message_name=message_name, service=serviceUUID))

        id = int(id)
        headers = getForwardHeaders(request)
        details = get_book_details(id, headers)

        data["records"].append(generate_record(uuid=req_id, type=1, message_name="Product Details Response", service=serviceUUID))
    else:
        id = int(id)
        headers = getForwardHeaders(request)
        details = get_book_details(id, headers)


    if FI_TRACE:
        response = make_response(jsonify(details))
        response.headers["fi-trace"] = json.dumps(data)
        return response
    else:
        return jsonify(details), 200

# TODO: provide details on different books.
def get_book_details(ID, headers):
    if os.environ.get("ENABLE_EXTERNAL_BOOK_SERVICE") != None:
        # the ISBN of one of Comedy of Errors on the Amazon
        # that has Shakespeare as the single author
        isbn = "0486424618"
        return fetch_details_from_external_service(isbn, ID, headers)

    return {
        "id": ID,
        'author': 'William Shakespeare',
        'year': 1595,
        'type': 'paperback',
        'pages': 200,
        'publisher': 'PublisherA',
        'language': 'English',
        'ISBN-10': '1234567890',
        'ISBN-13': '123-1234567890'
    }

def fetch_details_from_external_service(isbn, ID, headers):
    uri = urlparse('https://www.googleapis.com/books/v1/volumes?q=isbn:' + isbn)
    use_ssl = True
    port = 443

    if os.environ.get("DO_NOT_ENCRYPT"):
        use_ssl = False

    if not use_ssl:
        port = 80

    if not use_ssl:
        conn = http_client.HTTPConnection(uri.hostname, port=port, timeout=5)
    else:
        conn = http_client.HTTPSConnection(uri.hostname, port=port, timeout=5)


    url = uri.geturl()
    conn.request("GET", url)
    r1 = conn.getresponse()
    data = json.loads(r1.read())

    book = data["items"][0]["volumeInfo"]
    language = ""
    type = ""

    if book["language"] == "en":
        language = "English"
    else:
        language = "unknown"

    if book["printType"] == "BOOK":
        type = "paperback"
    else:
        type = "unknown"

    isbn10 = get_isbn(book, 'ISBN_10')
    isbn13 = get_isbn(book, 'ISBN_13')

    return {
        "id": ID,
        "author": book["authors"][0],
        "year": book['publishedDate'],
        "type": type,
        "pages": book['pageCount'],
        "publisher": book['publisher'],
        "language": language,
        "ISBN-10": isbn10,
        "ISBN-13": isbn13
    }

def get_isbn(book, isbn_type):
    isbn_identifiers = book["industryIdentifiers"]

    for obj in isbn_identifiers:
        if obj["type"] == isbn_type:
            return obj["identifier"]

    return isbn_identifiers[0]["identifier"]

def getForwardHeaders(request):
    headers = {}

    incoming_headers = [
      # All applications should propagate x-request-id. This header is
      # included in access log statements and is used for consistent trace
      # sampling and log sampling decisions in Istio.
      'x-request-id',

      # Lightstep tracing header. Propagate this if you use lightstep tracing
      # in Istio (see
      # https://istio.io/latest/docs/tasks/observability/distributed-tracing/lightstep/)
      # Note: this should probably be changed to use B3 or W3C TRACE_CONTEXT.
      # Lightstep recommends using B3 or TRACE_CONTEXT and most application
      # libraries from lightstep do not support x-ot-span-context.
      'x-ot-span-context',

      # Datadog tracing header. Propagate these headers if you use Datadog
      # tracing.
      'x-datadog-trace-id',
      'x-datadog-parent-id',
      'x-datadog-sampling-priority',

      # W3C Trace Context. Compatible with OpenCensusAgent and Stackdriver Istio
      # configurations.
      'traceparent',
      'tracestate',

      # Cloud trace context. Compatible with OpenCensusAgent and Stackdriver Istio
      # configurations.
      'x-cloud-trace-context',

      # Grpc binary trace context. Compatible with OpenCensusAgent nad
      # Stackdriver Istio configurations.
      'grpc-trace-bin',

      # b3 trace headers. Compatible with Zipkin, OpenCensusAgent, and
      # Stackdriver Istio configurations.
      'x-b3-traceid',
      'x-b3-spanid',
      'x-b3-parentspanid',
      'x-b3-sampled',
      'x-b3-flags',

      # Application-specific headers to forward.
      'end-user',
      'user-agent',
      'fi-trace'
    ]

    for ihdr in incoming_headers:
        val = request.headers.get(ihdr)
        if val is not None:
            headers[ihdr] = val

    return headers

if __name__ == "__main__":
    if len(sys.argv) < 2:
        logging.error("usage: %s port" % (sys.argv[0]))
        sys.exit(-1)

    p = int(sys.argv[1])
    logging.info("start at port %s" % (p))
    app.run(host="0.0.0.0", port=p, debug=True, threaded=True)
