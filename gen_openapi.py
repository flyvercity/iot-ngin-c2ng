import yaml
from pathlib import Path
from argparse import ArgumentParser

from apispec import APISpec
from apispec.exceptions import APISpecError
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.tornado import TornadoPlugin  # type: ignore

from service.app import handlers


def generate_swagger_file(file: Path):
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
    parser.add_argument('-f', '--file', help='Target file to write specification', required=True)
    args = parser.parse_args()
    generate_swagger_file(Path(args.file))


if __name__ == '__main__':
    main()
