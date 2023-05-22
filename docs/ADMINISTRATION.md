# System Administration Tasks

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

* `ME_CONFIG_MONGODB_ADMINUSERNAME` sets a username
* `ME_CONFIG_MONGODB_ADMINPASSWORD` sets a password
* `ME_CONFIG_MONGODB_URL` access URL for MongoDB

#### Core Service Configuration

* `C2NG_UAS_CLIENT_SECRET` client secret for UA and ADX users authentication
* `C2NG_USS_CLIENT_SECRET` client secret for service to service authentication for USS simulator service (`c2ng` to `uss`)
* `C2NG_UA_DEFAULT_PASSWORD` a default password for a simulated user

### Configuration File

#### `service` Section

Parameters:

* `port` is a TCP port for service to listen to incoming HTTP requests

#### `logging` Section

Parameters:

* `verbose` controls whether the logging mechanism shall be more verbose. If `true`, the level is set to `DEBUG`, otherwise to `INFO`

#### `oath` Section

This section controls what OIDC server to user to authenticate users again. This version can only contain a single subsection called `keycloak`, with the following parameters:

* `base` is the base URL of the server
* `realm` is the KeyCloak's realm that contains the enrolled UAV as users

#### `uss` Section

Configures how the service reaches the USS 

## Enrollment

## Makefile

### Regenerating the OpenAPI Specification

To extract OpenAPI 3 service specification from code, run:

```sh
make generate
```

## darglint

darglint

![test](xpng.png)

# mermaid sample

```mermaid
graph TD;
    A-->B;
    A-->C;
    B-->D;
    C-->D;
```
