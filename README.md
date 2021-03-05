# bookinfo-threemilebeach
3 Mile Beach Integration with BookInfo

# Tracing and Fault Injection

## Client Request
```
    Request Data Strcture


    HTTPMethod:             int64
        HTTPGet             1
        HTTPPost            2


    ActionResponse:         int64
        PrintResponse:      1
        DeserializeTrace:   2
        CustomizedRspFunc:  3


    ExpectedResponse:       int64
        ContentType:        string
        Action:             ActionResponse



    Request:
        Method:             HTTPMethod
        URL:                string
        UrlValues:          url.Values // HTTP Post

        MessageName:        string
        Trace:              Trace
        Expect              ExpectResponse


    Requests:
        CookieUrl:          string
        Trace:              Trace

        Requests:           []Request

```
```
    Trace Data Structure


    Trace:
        Id:                 int64
        Records:            []*Records
        Rlfis:              []*Rlfis
        Tfis:               []*Tfis
```
```
    Record Data Structure


    MessageType:            int32
        Message_Request:    1
        Message_Response:   2

    RecordType              int32
        RecordSend:         1
        RecordReceive:      2

    Records
        Type:               RecordType
        Timestamp:          int64
        MessageName:        string
        Uuid:               string
        Service:            string
```
```
    Fault Data Structure


    FaultType:              int32
        FaultCrash:         1
        FaultDelay:         2

    TFIMeta:
        Name:               string
        Times:              int64
        Already:            int64

    TFI:
        Type:               FaultType
        Name:               []string
        Delay:              int64
        After:              []*TFIMeta
```
```
    Request Level Fault Injection Data Structure (Deleted)


    RLFI
        Type:               FaultType
        Name:               string
        Delay:              int64
```