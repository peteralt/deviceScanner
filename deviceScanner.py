import nmap, requests, json, logging
from pymongo import MongoClient
from datetime import datetime

class deviceScanner:

    backendUrl = 'http://localhost:2000/api/devices'
    network = '192.168.0.0/24'
    portScanner = nmap.PortScanner()

    dbClient = None
    logging.basicConfig(filename="/var/tmp/deviceScanner.log", level=logging.INFO)

    def __init___(self, network = None):
        if network is not None:
            self.network = network

    def initDatabase(self):
        if self.dbClient == None:
            self.dbClient = MongoClient()
            self.database = self.dbClient.deviceScanner

    def logInfo(self, message):
        logging.info(message)

    def logError(self, message):
        logging.error(message)

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

if __name__ == '__main__':
    scanner = deviceScanner()
    print "Scanning network: ", scanner.network
    results = scanner.scan()
    if len(results) > 0:
        print "Found",len(results),"devices:"
        scanner.logInfo(str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + ': ' + str(len(results)) + ' devices found')
        for device in results:
            print "\tDevice:", device['mac'], "@", device['ip'], "(", device['vendor'],")"
            result = scanner.saveDevice(device)
    else:
        print "No devices found. Are you sure you running with sudo priviledges?"
        scanner.logError('No devices found')
