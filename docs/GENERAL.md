# General System Description

___Project: C2NG Trusted Uncrewed Aviation Systems Command and Control for IoT-NGIN Open Call 2.___

## Disclaimer

IoT UAS C2 is a sub-project funded via the [IoT-NGIN project](https://iot-ngin.eu) Open Call. IoT-NGIN has received funding from the European Union’s Horizon 2020 research and innovation programme (Grant Agreement No 957246).

## Application Architecture

## Service Architecture

## Security Credentials

## Logging

# MongoDB Logical Schema

## C2NG Database

Name: `c2ng`

### Session Collection

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
