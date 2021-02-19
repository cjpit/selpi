from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from memory import Protocol
import connection
from muster import Muster
from memory import variable
import settings

protocol = Protocol(connection.create())
muster = Muster(protocol)
scales = {}

def add_parser(subparsers):
    parser = subparsers.add_parser('http', help='start http server')
    parser.set_defaults(func=run)

def run(args):
    protocol.login()
    scale_vars = [
        variable.create('CommonScaleForAcVolts'),
        variable.create('CommonScaleForAcCurrent'),
        variable.create('CommonScaleForDcVolts'),
        variable.create('CommonScaleForDcCurrent'),
        variable.create('CommonScaleForTemperature'),
        variable.create('CommonScaleForInternalVoltages'),
    ]
    muster.update(scale_vars)
    for var in scale_vars:
        scales[var.get_name()] = var.get_value([])

    print(scales)
    server_address = ('', 8000)
    print("Starting server")
    httpd = ThreadingHTTPServer(server_address, HTTPRequestHandler)
    httpd.serve_forever()

class HTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        stats = []
        variables = [
            #variable.create('CombinedKacoAcPowerHiRes'),
            #variable.create('Shunt1Name'),
            variable.create('Shunt1Power'),
            #variable.create('Shunt2Name'),
            variable.create('Shunt2Power'),
            variable.create('BatteryVolts'),
            variable.create('BatteryTemperature'),
            variable.create('LoadAcPower'),
            variable.create('DCBatteryPower'),
            #variable.create('ACLoadkWhTotalAcc'),
            #variable.create('BattOutkWhPreviousAcc'),
            variable.create('BattSocPercent'),
        ]
        muster.update(variables)
        for var in variables:
            stats.append({
                "description": variable.MAP[var.get_name()][variable.DESCRIPTION],
                "name": var.get_name(),
                "value": "%s%s" % (var.get_value(scales), variable.MAP[var.get_name()][variable.UNITS]),
            })
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        data = json.dumps(obj=stats, indent=2)
        self.wfile.write(bytes(data, "utf-8"))