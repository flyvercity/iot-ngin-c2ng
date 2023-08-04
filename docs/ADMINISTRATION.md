# II. System Administration Tasks

## Configuration

### Environment Variables

These environment variable are used to configure third-party containers and set secret values. All other configuration parameters for the service are set up via the [YAML configuration file](#configuration-file).

#### KeyCloak OAuth Service Configuration

* `KEYCLOAK_ADMIN` sets an admin username on container creation
* `KEYCLOAK_ADMIN_PASSWORD` sets an admin password (keep strictly secret for production deployments)

#### MongoDB Service Configuration

* `MONGO_INITDB_ROOT_USERNAME` sets a username for MongoDB
* `MONGO_INITDB_ROOT_PASSWORD` sets a password for MongoDB

#### MongoExpress Configuration

yME_CONFIG_MONGODB_ADMINUSERNAME` sets a username
* `ME_CONFIG_MONGODB_ADMINPASSWORD` sets a password
* `ME_CONFIG_MONGODB_URL` access URL for MongoDB


#### InfluxDB Configuration

These enviroment variable are used for containerized Influx only, as a default config.

* `DOCKER_INFLUXDB_INIT_MODE`
* `DOCKER_INFLUXDB_INIT_USERNAME`
* `DOCKER_INFLUXDB_INIT_PASSWORD`
* `DOCKER_INFLUXDB_INIT_ORG`
* `DOCKER_INFLUXDB_INIT_BUCKET`
* `OCKER_INFLUXDB_INIT_ADMIN_TOKEN`

#### Core Service Configuration

* `C2NG_UAS_CLIENT_SECRET` client secret for UA and ADX users authentication
* `C2NG_USS_CLIENT_SECRET` client secret for service to service authentication for USS simulator service (`c2ng` to `uss`)
* `C2NG_UA_DEFAULT_PASSWORD` a default password for a simulated user

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

* `base` is the base URL of the server.
* `realm` is the KeyCloak's realm that contains the enrolled UAV as users.

#### `uss` Section

This section configures how the service reaches the USSP flight authorization endpoint or a simulator:

* `endpoint` set a URL of the authorization server.
* `oauth` subsection contain authentication and authorization information. This version suport KeyCloak authentication server, under `keycloak` subsection.

KeyCloak authentication parameters:

* `base` is the base URL server. Note that it does not have to be identical to the [own](#oath-section) server.
* `realm` is the Keycloak realm to authenticate against.
* `auth-client-id` is a the value used as a client identifier in the Client Credentials Grant flow.

#### `mongo` Section

This section controls  inteface with MongoDB server:

Parameters:

* `uri` is a base URI of the server.

#### `sliceman` Section

This section controls interface with SliceMan in the Network Core.

Parameters:

* `simulated` is set to `true` for simulations with an internal SliceMan simulator.
* `uri` is a base URL of the Function.

#### `security` Section

This section controls link security and encryption mechanism.

Parameters:

* `certificate` set the path to a file with the root X.509 certificate of the service in the PEM format.
* `private` set the path to a file with the root private key in the PEM format.
* `defaul-ttl` set the Time-to-Live parameter of the core certificate.

## Makefile

### Image Generation

To build the C2NG web service image, run:

```sh
make build
```

### Cryptograhic Keys Generation

To generate root cryptographic keys, run:

```sh
make keys
```

This command generates two files:

* `config/c2ng/private.pem` - a service root private key, and
* `config/c2ng/service.pem` - a service root certificate with a public key.

### Keycloak Automatic Configuration

The KeyCloak service must be configured to match configuration procedures the service uses:

* user authentication using the Direct Access Grant;
* C2NP service to USSP simulator (or an operational USSP) authentication.

This can be done through KeyCloak's user interface, but there is also a automatic procedure as a part of CLI tools. Use the following command to run:

```sh
python tools/c2ng.py keycloak
```

### OpenAPI Specification Regenerating

To extract OpenAPI 3 service specification from code, run:

```sh
make generate
```
