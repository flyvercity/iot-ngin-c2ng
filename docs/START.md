# III. Getting Started with Next Generation UAS C2 Connectivity Service

[External Service Interface Specification](./c2ng.yaml)

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

### Mermaid Filter

Install `nodejs` and `npm` is not present (assuming Debian-based distros):

```sh
sudo apt-get install nodejs npm
```

Then install the filter with:

```sh
npm install --global mermaid-filter
```

If the filter fails, try installing some dependencies:

```sh
sudo apt-get install libnss3-dev
```

If it still fails, add more dependencies:

```sh
sudo apt-get install -y gconf-service libasound2 libatk1.0-0 libc6 libcairo2 libcups2 libdbus-1-3 libexpat1 libfontconfig1 libgcc1 libgconf-2-4 libgdk-pixbuf2.0-0 libglib2.0-0 libgtk-3-0 libnspr4 libpango-1.0-0 libpangocairo-1.0-0 libstdc++6 libx11-6 libx11-xcb1 libxcb1 libxcomposite1 libxcursor1 libxdamage1 libxext6 libxfixes3 libxi6 libxrandr2 libxrender1 libxss1 libxtst6 ca-certificates fonts-liberation libappindicator1 libnss3 lsb-release xdg-utils wget libgbm-dev
```

### Building the Deliverable

To build `D2.C2NG.pdf` (MVP documentation), execute

```sh
make docs
```
