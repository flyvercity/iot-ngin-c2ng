import json
from pathlib import Path
from argparse import ArgumentParser

from apispec import APISpec
from apispec.exceptions import APISpecError
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.tornado import TornadoPlugin  # type: ignore

from app.c2ng_service import handlers


def generate_swagger_file(file: Path):
    spec = APISpec(
        title='C2NG API Definition',
        version='1.0.0',
        openapi_version='3.0.2',
        info=dict(description='Documentation for the Command-and-Control NextGen APi'),
        plugins=[TornadoPlugin(), MarshmallowPlugin()]
    )

    for handler in handlers():
        try:
            spec.path(urlspec=handler)
        except APISpecError:
            pass

    spec_str = json.dumps(spec.to_dict(), ensure_ascii=False, indent=4)
    file.write_text(spec_str)


def main():
    parser = ArgumentParser()
    parser.add_argument('-f', '--file', help='Target file to write specification', required=True)
    args = parser.parse_args()
    generate_swagger_file(Path(args.file))


if __name__ == '__main__':
    main()
