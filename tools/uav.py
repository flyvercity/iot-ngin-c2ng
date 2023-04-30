from datetime import datetime

DEFAULT_SAFETY_MARGIN = 300


def fake_point():
    return {
        'Latitude': 30.0,
        'Longitude': 30.0,
        'Altitude': 100.0
    }


def request(ctx):
    query = {
        'ReferenceTime': datetime.now().timestamp(),
        'UavID': ctx.args.uavid,
        'Waypoints': [
            fake_point()
        ],
        'OperationalMargin': DEFAULT_SAFETY_MARGIN
    }

    response = ctx.request('/uav/session', method='POST', body=query)
    ctx.dump(response)
