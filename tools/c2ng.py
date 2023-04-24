import requests
import json
from argparse import ArgumentParser


def request(args, path, method='GET'):
    url = args.url + path
    r = requests.request(method=method, url=url)
    r.raise_for_status()
    reply = r.json()

    if 'Success' not in reply:
        raise UserWarning(f'Malformed reply: {r.text}')

    if not reply['Success']:
        if ('ErrorID' not in reply) or ('ErrorString' not in reply):
            raise UserWarning(f'Malformed failure reply: {r.text}')

        eid = reply['ErrorID']
        text = reply['ErrorString']
        raise UserWarning(f'Service replied with an error ({eid}): {text}')

    return reply


def dump(data):
    print(json.dumps(data, indent=4))


def test(args):
    r = request(args, '/')
    dump(r)


def connect(args):
    pass


COMMANDS = {
    'test': test,
    'connect': connect
}


def main():
    parser = ArgumentParser()
    parser.add_argument('-u', '--url', help='C2NG service URL', default='http://localhost:9090')
    sp = parser.add_subparsers(dest='command', required=True, metavar='CMD')
    sp.add_parser('test', help='Test a connection with the service')
    args = parser.parse_args()


    try:
        handler = COMMANDS[args.command]
        handler(args)

    except UserWarning as exc:
        print(f'Command failed: {exc}')


if __name__ == '__main__':
    main()
