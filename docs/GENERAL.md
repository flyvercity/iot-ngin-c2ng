# I. General System Description

___Project: C2NG Trusted Uncrewed Aviation Systems  
Command and Control for IoT-NGIN Open Call 2.___

## Disclaimer

IoT UAS C2 is a sub-project funded via the [IoT-NGIN project](https://iot-ngin.eu) Open Call. IoT-NGIN has received funding from the European Union’s Horizon 2020 research and innovation programme (Grant Agreement No 957246).

## Introducion

The trusted UAS Next-Generation Command-and-Control (C2NG) Service enables reliable and compliant connectivity between uncrewed aircraft (UA) a.k.a. drones and remote pilot stations (RPS). Any UA under consideration is assumed to be equipped with 5G modules and antennae. RPS may also use 5G connectivity, but not necessarily. All data exchanges are assumed to be based on TCP/IP protocol suite. In contrast with generic Internet connectivity, a reliable connection between the vehicle and the RPS is herein referred to as the “aerial connection”.

This service has three primary functions:

* manage reliability of connection by interacting with 5G network functions.
* support security by managing security credentials and implementing Aerial Connection Authorization with Uncrewed Traffic Management Systems.
* monitor performance and compliance by signal data acquisition and analysis.

There are two types of users of the service:

* Aerial Connection Users are flying objects equipped with 5G UE

## Application Architecture

The Application is based on containerized services and comprises three open source basic components (KeyCloak, MongoDB, and InfluxDB) and the core software service (C2NG). Besides the core software, a CLI tool was developed to control all administrative task, simulation and demostration.

KeyCloak is an open source implementation OIDC protocol and

```mermaid
flowchart
    UAS-Client --> Application
    subgraph Application
        direction TB
        C2NG --> NSACF
        C2NG --> MongoDB
        C2NG --> InfluxDB
    end
    Application --> KeyCloak
```

__TDB__

## Repository Structure

__TDB__

# API Definition

__TBD__

## C2NG Service Architecture

```mermaid
flowchart
    Tornado --> App
    App --> Sessions
    App --> Certificates
    App --> Signal
    Sessions --> USS
    Sessions --> NSACF
    Sessions --> SecMan
    Certificates --> SecMan
    Signal --> Influx
```

__TDB__

## Security Credentials

```mermaid
flowchart BT
    Session-Ua-Cert --> Session-Ua-Private-Key
    Session-Ua-Cert --> Root-Cert
    Session-Adx-Cert --> Session-Adx-Private-Key
    Root-Cert --> Root-Private-Key
    Session-Adx-Cert --> Root-Cert
```

### Security Credentials Exchange Procedure

User = UA | ADX

```mermaid
sequenceDiagram
    User ->> KeyCloak: Get Token
    KeyCloak -->> User: Access Token
    User ->> +C2NG: Request Session
    C2NG ->> NSACF: Request Admission
    NSACF -->> C2NG: IP/Gateway
    C2NG ->> SecMan: Request Session credentials
    SecMan -->> C2NG: Session Public/Private Keys
    C2NG -->> -User: IP/Gateway, Certificate
```

__TDB__

### Expected User Interaction

```mermaid
sequenceDiagram
    UA ->> C2NG: Request Session
    ADX ->> C2NG: Request Session
    UA ->> C2NG: Request Peer Certificate
    ADX ->> С2NG: Request Peer Certificate
    ADX ->> C2NS: Request UA Address
    ADX ->> UA: Connect
    ADX -->> UA: Send Encrypted/Signed C2 Payload
    UA -->> ADX: Reply for Encrypted/Signed C2 Payload
    ADX ->> UA: Disconnect
```

### Expected Encryption Description Procedure

```mermaid
flowchart
    Message --> CP
    subgraph CP [Construct Packet]
        direction TB
        Encrypt(Encrypt with peer's public key) --> Sign
        Sign(Sign with out private key) --> Marshal
    end
    CP --> Transmit
    Transmit --> DP
    subgraph DP [Deconstruct Packet]
        direction TB
        Unmarshal --> Verify
        Verify(Verify a signature with peer's public key) --> Decrypt
        Decrypt(Decrypt with our private key)
    end
    DP --> RM(Message)
```

### Handlers Structure

```mermaid
classDiagram
    BaseHandler <|-- AuthHandler
    AuthHandler <|-- SessionRequest
    SessionRequest <|-- UaSessionRequest
    SessionRequest <|-- AdxSessionRquest
    AuthHandler <|-- Certificates
    AuthHandler <|-- Signal
```

__TDB__

## CLI Tools

```mermaid
flowchart
    c2ng-cli --> crypto-keys
    c2ng-cli --> gen-open-api
    c2ng-cli --> oauth-admin
```

__TDB__


## Logging

__TDB__

# MongoDB Logical Schema

__TDB__

Databse name: `c2ng`

## Session Collection

Name: `c2session`  
Key: `UasID`  

Document schema:  
```json
{
    "UasID": "string",
    "UaID": "string",

    "UaIP": "string: IPv4 or IPv6 address",
    "UaGatewayIP": "string: IPv4 or IPv6 address",
    "UaCertificate": "string: PEM",

    "AdxIP": "string: IPv4 or IPv6 address",
    "AdxGatewayIP": "string: IPv4 or IPv6 address",
    "AdxCertificate": "string: PEM"
}
```
