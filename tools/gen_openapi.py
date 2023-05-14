#   SPDX-License-Identifier: MIT
#   Copyright 2023 Flyvercity

import yaml
from pathlib import Path
from argparse import ArgumentParser

from apispec import APISpec
from apispec.exceptions import APISpecError
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.tornado import TornadoPlugin  # type: ignore

from service.app import handlers


def generate_openapi_file(file: Path):
    ''' Generate OpenAPI Specification from Code '''

    spec = APISpec(
        title='C2NG API Definition',
        version='1.0.0',
        openapi_version='3.0.2',
        info=dict(description='Documentation for the Command-and-Control NextGen API'),
        plugins=[TornadoPlugin(), MarshmallowPlugin()]
    )

    for handler in handlers():
        try:
            spec.path(urlspec=handler)
        except APISpecError:
            pass

    spec_dict = spec.to_dict()
    yaml_version = yaml.dump({'openapi': spec_dict.pop('openapi')})
    yaml_imfo = yaml.dump({'info': spec_dict.pop('info')})
    yaml_rest = yaml.dump(spec_dict)
    file.write_text(yaml_version + yaml_imfo + yaml_rest)


def main():
    parser = ArgumentParser()

    parser.add_argument(
        '-f', '--file',
        help='Target file to write specification', default='docs/c2ng.yaml'
    )

    args = parser.parse_args()
    generate_openapi_file(Path(args.file))


if __name__ == '__main__':
    main()
