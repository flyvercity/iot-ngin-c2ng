# General System Description

___Project: C2NG Trusted Uncrewed Aviation Systems Command and Control for IoT-NGIN Open Call 2.___

## Disclaimer

IoT UAS C2 is a sub-project funded via the [IoT-NGIN project](https://iot-ngin.eu) Open Call. IoT-NGIN has received funding from the European Union’s Horizon 2020 research and innovation programme (Grant Agreement No 957246).

## Introducion

The trusted UAS Next-Generation Command-and-Control (C2NG) Service enables reliable and compliant connectivity between uncrewed aircraft (UA) a.k.a. drones and remote pilot stations (RPS). Any UA under consideration is assumed to be equipped with 5G modules and antennae. RPS may also use 5G connectivity, but not necessarily. All data exchanges are assumed to be based on TCP/IP protocol suite. In contrast with generic Internet connectivity, a reliable connection between the vehicle and the RPS is herein referred to as the “aerial connection”.

## Application Architecture

```mermaid
flowchart
    UAS-Client --> Application
    subgraph Application
        direction TB
        C2NG --> NSACF
        C2NG ---> MongoDB
        C2NG ---> InfluxDB
    end
    Application ----> KeyCloak
```

## Repository Structure

__TDB__

## C2NG Service Architecture

```mermaid
flowchart
    subgraph Components
        NSACF
        SecMan
        USS
        Mongo
        Influx
    end
    subgraph API-Handlers
        direction TB
        Base --> Auth
        Auth --> Sessions
        Auth --> Certificates
        Auth --> Signal
    end
    Tornado --> App
    App --> Components
    App --> API-Handlers
```

## Security Credentials

__TDB__


## CLI Tools

```mermaid
flowchart
    c2ng-cli --> crypto-keys
    c2ng-cli --> gen-open-api
    c2ng-cli --> oauth-admin
```


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
