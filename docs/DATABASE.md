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
    "UavID": "string",

    "UavIP": "string: IPv4 or IPv6 address",
    "UavGatewayIP": "string: IPv4 or IPv6 address",
    "UavPublicKey": "string: hex",
    "UavPrivateKey": "string: hex",

    "RpsIP": "string: IPv4 or IPv6 address",
    "RpsGatewayIP": "string: IPv4 or IPv6 address",
    "RpsPublicKey": "string: hex",
    "RpsPrivateKey": "string: hex"
}
```
