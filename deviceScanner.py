import nmap, requests, json
from pymongo import MongoClient
from datetime import datetime

class deviceScanner:

    backendUrl = 'http://localhost:2000/api/devices'
    network = '192.168.0.0/24'
    portScanner = nmap.PortScanner()

    dbClient = None

    def __init___(self, network = None):
        if network is not None:
            self.network = network
        print "Scanning for network: ", self.network,"..."

    def initDatabase(self):
        if self.dbClient == None:
            self.dbClient = MongoClient()
            self.database = self.dbClient.deviceScanner

    def scan(self):
        """Returns a dictionary with all devices found on the network (mac, IP and vendor info)"""
        self.portScanner.scan(hosts=self.network, arguments='-sn')
        # print nm.command_line() # print nm.scaninfo()
        devices = self.convertPortScannerResultsToDict()
        return devices

    def convertPortScannerResultsToDict(self):
        """Converts nmap results into dict (only using values we care about)"""
        devices = []

        for h in self.portScanner.all_hosts():
            if 'mac' in self.portScanner[h]['addresses']:
                device = {}
                device['mac'] = self.portScanner[h]['addresses']['mac']
                device['ip'] = self.portScanner[h]['addresses']['ipv4']
                device['vendor'] = self.portScanner[h]['vendor'].get(device['mac'])

                devices.append(device)

        return devices

    def saveDevice(self, device):
        self.initDatabase()
        result = self.database.devices.insert_one(
            {
                "device": {
                    "mac": device['mac'],
                    "vendor": device['vendor'],
                    "ip": device['ip'],
                    "seen_at": datetime.now()
                }
            }
        )
        return result


    def postDevice(self, device):
        payload = {'name': str(device['vendor']), 'mac': str(device['mac']), 'ip': str(device['ip'])}
        # print "Payload:", payload
        # print "dump: ", json.dumps(payload)
        try:
            r = requests.post(url, data=json.dumps(payload))
            # print r.text # print r.status_code
            return r.status_code
        except:
            return None
