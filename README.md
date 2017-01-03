# deviceScanner
Scan your local network for devices and store device info in a mongoDB

## Requirements

* Python 2.7+
* nmap
* Script must run with *sudo* rights
* python-nmap (install using *pip install python-nmap*)
* requests (install using *pip install requests*)
* pymongo (install using *pip install pymongo*)
* MongoDB

## How to use it

Just run the script periodically (using cronjobs for example) and use whatever you like to display or analyze the data.
