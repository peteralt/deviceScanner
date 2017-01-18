import nmap, requests, json, logging, os
from pymongo import MongoClient
from datetime import datetime
from pprint import pprint
import slackweb

class deviceScanner:

    backendUrl = 'http://localhost:2000/api/devices'
    network = '192.168.0.0/24'
    portScanner = nmap.PortScanner()
    knownDevices = None

    dbClient = None

    def __init__(self, knownDevices, network, backendURL, loggingFile, logLevel = logging.INFO):
        if network is not None:
            self.network = network
        if backendURL is not None:
            self.backendUrl = backendURL
        if loggingFile is not None:
            logging.basicConfig(filename=loggingFile, level=logLevel)
        if knownDevices is not None:
            self.knownDevices = knownDevices

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
                device['knownDevice'] = False
                if device['mac'] in self.knownDevices:
                    device['name'] = self.knownDevices[device['mac']]
                    device['knownDevice'] = True
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

    network = None
    backendURL = None
    loggingFile = None

    with open(os.path.dirname(os.path.abspath(__file__))+'/settings.json') as data_file:
        print("Loading settings...")
        data = json.load(data_file)
        network = data['local_network']
        backendURL = data['backend_url']
        loggingFile = data['logging_file']
        known_devices = data['devices']

    slack = slackweb.Slack(url=data['slack_url'])

    scanner = deviceScanner(known_devices, network, backendURL, loggingFile, logging.INFO)
    print("Scanning network: ", scanner.network)
    results = scanner.scan()

    knownDeviceFound = False
    if len(results) > 0:
        print("Found",len(results),"devices:")
        scanner.logInfo(str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + ': ' + str(len(results)) + ' devices found')
        for device in results:
            name = ''
            if device['knownDevice']:
                name = "=> " + device['name']
                knownDeviceFound = True
            print ("\tDevice:", device['mac'], "@", device['ip'], "(", device['vendor'],")", name)
            result = scanner.saveDevice(device)
        if knownDeviceFound:
            print("Known devices: found")
            slack.notify(text="Known device found. Someone is home!", channel="#home", username="nest-bot", icon_emoji=":snowflake:")
        else:
            print("Known devices: not found")
            slack.notify(text="No known devices found. Seems everyone is out.", channel="#home", username="nest-bot", icon_emoji=":snowflake:")
    else:
        print ("No devices found. Are you sure you running with sudo priviledges?")
        scanner.logError('No devices found')
