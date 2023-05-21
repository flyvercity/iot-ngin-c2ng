# UAS Command-and-Control Connectivity Service

___Project: C2NG Trusted Uncrewed Aviation Systems Command and Control for IoT-NGIN Open Call 2.___

[Detailed Documentation](docs/README.md)

[External Service Interface Specification](docs/c2ng.yaml)

## Development Environment

Development dependencies:

* `make`
* `docker`
* `docker-compose`
* `python 3.10` and `pip`. Virtual environment recommended.

## Environment Variables

Copy `.env.template` to `.env` and set your value to the following variables:

* `KEYCLOAK_ADMIN` sets a KeyCloak service admin username
* `KEYCLOAK_ADMIN_PASSWORD` sets a KeyCloak service admin password (keep strictly secret for production deployments)
* `MONGO_INITDB_ROOT_USERNAME` sets a username for MongoDB
* `MONGO_INITDB_ROOT_PASSWORD` sets a password for MongoDB
* `ME_CONFIG_MONGODB_ADMINUSERNAME` sets a username for MongoExpress
* `ME_CONFIG_MONGODB_ADMINPASSWORD` sets a password for MongoExpress
* `C2NG_UAS_CLIENT_SECRET` client secret for UA and ADX users authentication
* `C2NG_UA_DEFAULT_PASSWORD` a default password for UA users 
* `C2NG_ADX_DEFAULT_PASSWORD` a default password for ADX users
* `C2NG_USS_CLIENT_SECRET` client secret for service to service authentication for USS simulator service (`c2ng` to `uss`)

## Launch Sequence

Install Python dependencies:

```sh
pip install -r requirements.txt
pip install -r requirements.dev.txt
```

Build the image:

```sh
make build
```

Generate root keys:

```sh
make keys
```

Start the application:

```sh
docker-compose up -d
```

Configure authentication server:

```sh
python tools/c2ng.py keycloak
```

_Note: the CLI tool `c2ng.py` has other capabilities. For further help, run:_

```sh
python tools/c2ng.py -h
```

## Building Documentation

Install additional dependencies:

* `LaTeX`:
  * for Linux, use TeX Live (<https://tug.org/texlive/>)
  * for Windows, use MikTeX (<https://miktex.org/download>)
* `pandoc` (<https://pandoc.org/installing.html>)

To build `D2.C2NG.pdf` (MVP documentation), execute

```sh
make docs
```
