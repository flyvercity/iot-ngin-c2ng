import requests
import json
from argparse import ArgumentParser
import logging as lg

import uav
import uss_sim


DEFAULT_USS_PORT = 9091


class Handler:
    def __init__(self, args):
        self.args = args

    def dump(data):
        print(json.dumps(data, indent=4))

    def handle(self):
        try:
            func = getattr(self, self.args.command)
            func()

        except UserWarning as exc:
            print(f'Command failed: {exc}')

    def request(self, path: str, method='GET', body={}) -> dict:
        url = self.args.url + path
        r = requests.request(method=method, url=url, json=body)
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

    def test(self):
        r = self.request('/test')
        self.dump(r)

    def uav(self):
        uav.request(self)

    def uss(self):
        uss_sim.run(self.args)


def main():
    parser = ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose logging')
    parser.add_argument('-u', '--url', help='C2NG service URL', default='http://localhost:9090')
    sp = parser.add_subparsers(dest='command', required=True, metavar='CMD')
    sp.add_parser('test', help='Test a connection with the service')
    uav = sp.add_parser('uav', help='Command on behalf of UAV')
    uav.add_argument('-i', '--uavid', help='UAV CAA ID', default='droneid')
    uss = sp.add_parser('uss', help='USSP Simulator')
    uss.add_argument('-p', '--port', type=int, default=DEFAULT_USS_PORT)
    args = parser.parse_args()
    lg.basicConfig(level=lg.DEBUG if args.verbose else lg.INFO)
    Handler(args).handle()


if __name__ == '__main__':
    main()
