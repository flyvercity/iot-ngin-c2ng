# V. Verification

This section describes a basic scenario for software testing and demostation. These step shall follow the steps describes in the ["Getting Started"](./START.md#launch-sequence) section.

### Prerequisites

To simplify this procedure, we need to install the following:

* `jq` - commandline JSON processor.

For Debian-based Linux, execute:

```sh
sudo apt-get install jq
```

## Validate Container State

Query application status with:

```sh
./scripts/ctrl-core.sh ps --format json | jq
```

### Output Received During Verification

```json
[
  {
    "ID": "ef034c18891bcbb0f5e44495db6d0d01e470a72f656b6460123ff56b0b4e8b45",
    "Name": "core-c2ng-1",
    "Image": "c2ng",
    "Command": "python3 c2ng/service/app.py",
    "Project": "core",
    "Service": "c2ng",
    "Created": 1693159736,
    "State": "running",
    "Status": "Up 2 minutes",
    "Health": "",
    "ExitCode": 0,
    "Publishers": [
      {
        "URL": "0.0.0.0",
        "TargetPort": 9090,
        "PublishedPort": 9090,
        "Protocol": "tcp"
      },
      {
        "URL": "::",
        "TargetPort": 9090,
        "PublishedPort": 9090,
        "Protocol": "tcp"
      }
    ]
  },
  {
    "ID": "bda4fa3d73d42872ae209c6c144f31b7e1c7a9561f27111665475b3de19f123d",
    "Name": "core-influxdb-1",
    "Image": "influxdb",
    "Command": "/entrypoint.sh influxd",
    "Project": "core",
    "Service": "influxdb",
    "Created": 1693027076,
    "State": "running",
    "Status": "Up 2 minutes",
    "Health": "",
    "ExitCode": 0,
    "Publishers": [
      {
        "URL": "0.0.0.0",
        "TargetPort": 8086,
        "PublishedPort": 8086,
        "Protocol": "tcp"
      },
      {
        "URL": "::",
        "TargetPort": 8086,
        "PublishedPort": 8086,
        "Protocol": "tcp"
      }
    ]
  },
  {
    "ID": "64fa9c336e384a3a75e8bc94eff191d73602fd7413775055b79b2119ad5ac00a",
    "Name": "core-mongo-1",
    "Image": "mongo",
    "Command": "docker-entrypoint.sh mongod",
    "Project": "core",
    "Service": "mongo",
    "Created": 1693027076,
    "State": "running",
    "Status": "Up 2 minutes",
    "Health": "",
    "ExitCode": 0,
    "Publishers": [
      {
        "URL": "0.0.0.0",
        "TargetPort": 27017,
        "PublishedPort": 27017,
        "Protocol": "tcp"
      },
      {
        "URL": "::",
        "TargetPort": 27017,
        "PublishedPort": 27017,
        "Protocol": "tcp"
      }
    ]
  },
  {
    "ID": "31b4554edb213b4fc1e0d16fa54120a83e38531360a475b160351e33c4ed0d9f",
    "Name": "core-mongo-express-1",
    "Image": "mongo-express",
    "Command": "tini -- /docker-entrypoint.sh mongo-express",
    "Project": "core",
    "Service": "mongo-express",
    "Created": 1693027076,
    "State": "running",
    "Status": "Up 2 minutes",
    "Health": "",
    "ExitCode": 0,
    "Publishers": [
      {
        "URL": "0.0.0.0",
        "TargetPort": 8081,
        "PublishedPort": 8081,
        "Protocol": "tcp"
      },
      {
        "URL": "::",
        "TargetPort": 8081,
        "PublishedPort": 8081,
        "Protocol": "tcp"
      }
    ]
  },
  {
    "ID": "867a416647e3a3c56109f34c749774ccd602c751485d885d00eae00605eab18b",
    "Name": "core-oauth-1",
    "Image": "quay.io/keycloak/keycloak",
    "Command": "/opt/keycloak/bin/kc.sh start-dev",
    "Project": "core",
    "Service": "oauth",
    "Created": 1693027076,
    "State": "running",
    "Status": "Up 2 minutes",
    "Health": "",
    "ExitCode": 0,
    "Publishers": [
      {
        "URL": "0.0.0.0",
        "TargetPort": 8080,
        "PublishedPort": 8080,
        "Protocol": "tcp"
      },
      {
        "URL": "::",
        "TargetPort": 8080,
        "PublishedPort": 8080,
        "Protocol": "tcp"
      },
      {
        "URL": "",
        "TargetPort": 8443,
        "PublishedPort": 0,
        "Protocol": "tcp"
      }
    ]
  },
  {
    "ID": "f5047b992d757a85941683fad3d8b665db561c5bcb32582c15c056caaa456d70",
    "Name": "core-uss-1",
    "Image": "c2ng-uss-sim",
    "Command": "python3 c2ng/uss_sim/uss_sim.py",
    "Project": "core",
    "Service": "uss",
    "Created": 1693159736,
    "State": "running",
    "Status": "Up 2 minutes",
    "Health": "",
    "ExitCode": 0,
    "Publishers": [
      {
        "URL": "0.0.0.0",
        "TargetPort": 9091,
        "PublishedPort": 9091,
        "Protocol": "tcp"
      },
      {
        "URL": "::",
        "TargetPort": 9091,
        "PublishedPort": 9091,
        "Protocol": "tcp"
      }
    ]
  }
]

```

## Check Service Startup

Execute:

```sh
./scripts/core-follow.sh
```

The service should restart and then show that it's private and public key are successfully loaded, KeyCloak and Mongo DB are connected, and the service is listening for requests:

```sh
core-c2ng-1  | INFO:root:---------- Starting up ----------
core-c2ng-1  | INFO:root:Fetching KeyCloak public keys started
core-c2ng-1  | INFO:root:Fetching KeyCloak public keys: http://oauth:8080/realms/c2ng/protocol/openid-connect/certs
core-c2ng-1  | INFO:root:Connecting to MongoDB on mongodb://root:example@mongo:27017/
core-c2ng-1  | INFO:root:Certificate loaded: 389898463292075240605008754504802033596342104328
core-c2ng-1  | INFO:root:Private key loaded
core-c2ng-1  | INFO:root:---------- Restarted ----------
core-c2ng-1  | INFO:root:Listening for requests on 9090
```

## USSP Simulation

Run the USSP Flight Authrization Endpoint Simulator with

```sh
./scripts/uss-follow.sh
```

### Captured Output

```sh
core-uss-1  | INFO:root:USS SIM :: Listening for requests on 9091
```

## ADX User Simulation

Run the Remote Pilot Station Simulator with:

```sh
./scripts/adx-follow.sh
```

The simulator shall receive a session from the service and start polling for the peer's (UA) certificate.

### Captured Output

ADX Simulator output:

```sh
uas_sim-c2ng-adx-1  | 2023-08-27 18:19:44,034  ------ Starting ------
uas_sim-c2ng-adx-1  | 2023-08-27 18:19:44,034  Selected ADX subsystem
uas_sim-c2ng-adx-1  | 2023-08-27 18:19:44,034  Reset
uas_sim-c2ng-adx-1  | 2023-08-27 18:19:44,035  Subscribing to notifications
uas_sim-c2ng-adx-1  | 2023-08-27 18:19:44,354  Waiting for notification
uas_sim-c2ng-adx-1  | 2023-08-27 18:19:44,355  Reading notifications
uas_sim-c2ng-adx-1  | 2023-08-27 18:19:44,355  Notification received
uas_sim-c2ng-adx-1  | 2023-08-27 18:19:44,355  Reading notifications
uas_sim-c2ng-adx-1  | 2023-08-27 18:19:45,356  Waiting for notification
uas_sim-c2ng-adx-1  | 2023-08-27 18:19:45,356  Requesting session
uas_sim-c2ng-adx-1  | 2023-08-27 18:19:45,555  Requesting peer address
uas_sim-c2ng-adx-1  | 2023-08-27 18:19:45,615  Requesting peer certificate
uas_sim-c2ng-adx-1  | 2023-08-27 18:19:45,672  Requesting Verified Credential JWT
uas_sim-c2ng-adx-1  | 2023-08-27 18:19:45,748  Waiting for a packet
```

Service output:

```sh
core-c2ng-1  | INFO:root:---------- Restarted ----------
core-c2ng-1  | INFO:root:Listening for requests on 9090
core-c2ng-1  | INFO:tornado.access:200 POST /notifications/auth/sim-drone-id/adx (192.168.48.9) 1.70ms
core-c2ng-1  | INFO:tornado.access:101 GET /notifications/websocket (192.168.48.9) 0.56ms
core-c2ng-1  | INFO:root:SessMan :: Subscribing sim-drone-id::adx
core-c2ng-1  | INFO:root:The session exist for sim-drone-id
core-c2ng-1  | INFO:root:Generating credentials for sim-drone-id - ADX
core-c2ng-1  | INFO:root:SessMan :: No subscriber for sim-drone-id::ua
core-c2ng-1  | INFO:root:SessMan :: No subscriber for sim-drone-id::ua
core-c2ng-1  | INFO:tornado.access:200 POST /session (192.168.48.9) 75.18ms
core-c2ng-1  | INFO:tornado.access:200 GET /address/sim-drone-id/ua (192.168.48.9) 2.69ms
core-c2ng-1  | INFO:tornado.access:200 GET /certificate/sim-drone-id/ua (192.168.48.9) 2.45ms
core-c2ng-1  | INFO:tornado.access:200 GET /did/jwt/sim-drone-id (192.168.48.9) 1.46ms
```

## UA User Simulation

Run the UA (drone) Simulator with:

```sh
./scripts/ua-follow.sh
```

### Captured Output

Side-by-side data exchange between the simulators:

![Data Exchange Screenshot](./images/DataExchange.png)

The session data is stored in the data base as shown on the following MongoExpress tool screenshot:

![Mongo Screenshot](./images/MongoSnapshot.png)

Simultaneously, the UA simulator send the emulated signal data to the service, as reflected in the service logs:

![Signal Stats Screenshot](./images/SignalStats.png)

USS Simulator Output:

```sh
core-uss-1  | INFO:root:USS SIM :: Listening for requests on 9091
core-uss-1  | INFO:root:Service authorized: 192.168.48.7
core-uss-1  | INFO:root:Service authorized: 192.168.48.7
core-uss-1  | INFO:root:Approving connection for sim-drone-id
core-uss-1  | INFO:tornado.access:200 GET /approve?UasID=sim-drone-id (192.168.48.7) 20.58ms
core-uss-1  | INFO:root:Service authorized: 192.168.48.7
core-uss-1  | INFO:root:Service authorized: 192.168.48.7
core-uss-1  | INFO:root:Approving connection for sim-drone-id
core-uss-1  | INFO:tornado.access:200 GET /approve?UasID=sim-drone-id (192.168.48.7) 14.82ms
core-uss-1  | INFO:root:Service authorized: 192.168.48.7
core-uss-1  | INFO:root:Service authorized: 192.168.48.7
core-uss-1  | INFO:root:Approving connection for sim-drone-id
core-uss-1  | INFO:tornado.access:200 GET /approve?UasID=sim-drone-id (192.168.48.7) 13.73ms
```
