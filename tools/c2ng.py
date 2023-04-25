import requests
import json
from argparse import ArgumentParser
from datetime import datetime


DEFAULT_SAFETY_MARGIN = 300
                

def fake_point():
    return {
        'Latitude': 30.0,
        'Longitude': 30.0,
        'Altitude': 100.0
    }


def dump(data):
    print(json.dumps(data, indent=4))


class Handler:
    def __init__(self, args):
        self.args = args

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
        dump(r)

    def uav(self):
        query = {
            'ReferenceTime': datetime.now().timestamp(),
            'UavID': self.args.uavid,
            'Waypoints': [
                fake_point()
            ],
            'OperationalMargin': DEFAULT_SAFETY_MARGIN
        }

        r = self.request('/uav/session', method='POST', body=query)
        dump(r)

    def handle(self):
        try:
            func = getattr(self, self.args.command)
            func()

        except UserWarning as exc:
            print(f'Command failed: {exc}')


def main():
    parser = ArgumentParser()
    parser.add_argument('-u', '--url', help='C2NG service URL', default='http://localhost:9090')
    sp = parser.add_subparsers(dest='command', required=True, metavar='CMD')
    sp.add_parser('test', help='Test a connection with the service')
    uav = sp.add_parser('uav', help='Command on behalf of UAV')
    uav.add_argument('-i', '--uavid', help='UAV CAA ID', default='droneid')
    args = parser.parse_args()
    Handler(args).handle()


if __name__ == '__main__':
    main()
