# III. System Administration Tasks

## Configuration

### Environment Variables

These environment variable are used to configure third-party containers and set secret values. All other configuration parameters for the service are set up via the [YAML configuration file](#configuration-file).

#### KeyCloak OAuth Service Configuration

* `KEYCLOAK_ADMIN` sets an admin username on container creation;
* `KEYCLOAK_ADMIN_PASSWORD` sets an admin password (keep strictly secret for production deployments).

#### MongoDB Service Configuration

* `MONGO_INITDB_ROOT_USERNAME` sets a username for MongoDB;
* `MONGO_INITDB_ROOT_PASSWORD` sets a password for MongoDB.

#### MongoExpress Configuration

* `ME_CONFIG_MONGODB_ADMINUSERNAME` sets a username;
* `ME_CONFIG_MONGODB_ADMINPASSWORD` sets a password;
* `ME_CONFIG_MONGODB_URL` access URL for MongoDB.


#### InfluxDB Configuration

These enviroment variable are used for containerized Influx only, as a default config.

* `DOCKER_INFLUXDB_INIT_MODE`
* `DOCKER_INFLUXDB_INIT_USERNAME`
* `DOCKER_INFLUXDB_INIT_PASSWORD`
* `DOCKER_INFLUXDB_INIT_ORG`
* `DOCKER_INFLUXDB_INIT_BUCKET`
* `DOCKER_INFLUXDB_INIT_ADMIN_TOKEN`

#### C2NG Service Public Parameters

* `C2NG_CONFIG_FILE` is a configuration file path;
* `C2NG_WS_AUTH_SECRET` a secret for Websocket Authentication Mechanism;
* `C2NG_UAS_CLIENT_SECRET` client secret for UA and ADX users authentication.

#### C2NG UA/ADX Simulation Tools Public Parameters

* `C2NG_SIM_DRONE_ID` a simulated drone ID;
* `C2NG_DEFAULT_UA_UDP_PORT` a default receiving UDP port for UA simulator;
* `C2NG_DEFAULT_ADX_UDP_PORT` a default receiving UDP port for ADX simulator;
* `C2NG_SIM_VERBOSE` a verbose loggin mode for UA and ADX simulators;
* `C2NG_SIM_OAUTH_URL` is used to overrive the default OAuth server URL;
* `C2NG_SIM_CORE_URL` is used to overrive the C2NP core URL for simulators (main API);
* `C2NG_SIM_CORE_WS_URL` is used to overrive the C2NP core URL for simulators (asynchronious notifications API);
* `C2NG_SIM_UA_MODEM` set UA modem type (supported values: `none` and `simulated`);
* `C2NG_SIM_USE_DID` - set to `true` to use DID for authenticate ADX simulator on UA simulator using a verifiable credential.

#### C2NG UA/ADX Simulation Tools Secret Parameters

* `C2NG_UA_DEFAULT_PASSWORD` a default password for a simulated user.

#### C2NG USS Simulation Tools Public Parameters

* `C2NG_DEFAULT_USS_PORT` used to override the default USSP port.

#### C2NG USS Simulation Tools Secret Parameters

* `C2NG_USS_CLIENT_SECRET` client secret for service to service authentication for USS simulator service (`c2ng` to `uss`).

### Configuration File

#### `service` Section

This section configures access to the services itself.

Parameters:

* `port` is a TCP port for service to listen to incoming HTTP requests.

#### `logging` Section

This section configure the logging facility.

Parameters:

* `verbose` controls whether the logging mechanism shall be more verbose. If `true`, the level is set to `DEBUG`, otherwise to `INFO`.

#### `oath` Section

This section controls what OIDC server to user to authenticate users again. This version can only contain a single subsection called `keycloak`, with the following parameters:

* `base` is the base URL of the server;
* `realm` is the KeyCloak's realm that contains the enrolled UAV as users;
* `retry-timeout` is a timeout in seconds to retry server initialization if the server is not available.

#### `mongo` Section

This section controls  inteface with MongoDB server:

Parameters:

* `uri` is a base URI of the server.

#### `influx` Section

* `uri` is a base URI of the server;
* `org` is an organization name;
* `bucket` is a bucket name.

#### `uss` Section

This section configures how the service reaches the USSP flight authorization endpoint or a simulator:

* `endpoint` sets a URL of the authorization server;
* `oauth` subsection contain authentication and authorization information. This version suport KeyCloak authentication server, under `keycloak` subsection.

KeyCloak authentication parameters:

* `base` is the base URL server. Note that it does not have to be identical to the [own](#oath-section) server.
* `realm` is the Keycloak realm to authenticate against.
* `auth-client-id` is a the value used as a client identifier in the Client Credentials Grant flow.

#### `sliceman` Section

This section controls interface with SliceMan in the Network Core.

Parameters:

* `provider` sets the provider type. Supported values are `simulated` and `cumucore`. This section also contains provider-specific eponymous subsections.

##### `simulated` Provider Configuration

* `ue` sets the initial IP for aerial clients within a simulated network;
* `adx` sets the initial IP for ground clients within a simulated network;
* `gateway` is a gateway IP address for a simulated network.

##### `cumucore` Provider Configuration

* `uri` sets the base URI of the CumuCore Network Configuration Service.

#### `security` Section

This section controls link security and encryption mechanism.

Parameters:

* `certificate` set the path to a file with the root X.509 certificate of the service in the PEM format.
* `private` set the path to a file with the root private key in the PEM format.
* `defaul-ttl` set the Time-to-Live parameter of the core certificate.

#### `did` Section

This is an optional section that configures the Verifiable Credential mechanism and decentralized identifiers.

* `issuer-did` sets a path to a file with the DID of the issuer, which is by default the service itself;
* `resources` is a dict of resources that are allowed to be used in the Verifiable Credentials.

Each resource is a dict with the following parameters (dict's name is a name of the resource):
  * `jwt` is a path to a file with a JWT token that contains an encrypted Verifiable Credential.

## Makefile

### Image Generation

To build all docker images, run:

```sh
make build
```

### Cryptograhic Keys Generation

To generate root cryptographic keys, run:

```sh
make prerun
```

This command generates two files:

* `config/c2ng/private.pem` - a service root private key, and
* `config/c2ng/service.pem` - a service root certificate with a public key.

### DID Components Generation

To generate DID components, run:

```sh
make did
```

To support Verifiable Credentials, we need to generate some more cryptographic objects:

* an issuer private key `config/c2ng/did/issuer.pem`;
* an issuer decentralized identifer `config/c2ng/did/issuer.did`;
* a simulated remote pilot station private key `config/c2ng/did/sim-drone-id.pem`;
* a pilot station decentralized identifer `config/c2ng/did/sim-drone-id.did`;
* a json web token derived from the template verifiable credential `config/c2ng/did/sim-drone-id.jwt`. A template of the credential is located in `config/c2ng/did/sim-drone-id.vc-credential.json`.

### Starting the Service

To start the service, run:

```sh
make up
```

### Keycloak Automatic Configuration

The KeyCloak service must be configured to match configuration procedures the service uses:

* user authentication using the Direct Access Grant;
* C2NP service to USSP simulator (or an operational USSP) authentication.

This can be done through KeyCloak's user interface, but there is also a automatic procedure as a part of CLI tools. Use the following command to run:

```sh
python ./cli.sh keycloak
```

of just run:

```sh
make start
```

to go through all the steps automatically.

### OpenAPI Specification Regenerating

To extract OpenAPI 3 service specification from code, run:

```sh
make generate
```
