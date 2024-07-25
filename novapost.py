import requests, json, os, dotenv
from datetime import datetime, timedelta

dotenv.load_dotenv()

class NovaAPI():
    def __init__(self):
        self.apiKey = os.getenv('NOVA_API_KEY')
        self.endpoints = {
            'ukraine': 'https://api.novaposhta.ua/v.1.0/',
            'europe': 'https://api.novapost.com/v.1.0/'
        }
        self.session = requests.Session()
        self.tokenExpiration = None
        self.updateToken()

    def updateToken(self):
        if self.tokenExpiration and self.tokenExpiration < datetime.now():
            return self.token
        
        r = requests.get('https://api.novaposhta.ua/v.1.0/clients/authorization?apiKey='+self.apiKey)
        self.tokenExpiration = datetime.now()+timedelta(hours=1)

        self.session.headers.update({'Authorization': r.json()['jwt']})

    def getCities(self, countryCode):
        self.updateToken()
        cities = []
        r = self.session.get(self.endpoints['europe']+f'divisions?countryCodes[]={countryCode}&divisionCategories[]=PostBranch&limit=100&page=1')
        cities += [c['settlement']['name'] for c in r.json()['items']]
        while r.json()['total'] > len(cities):
            r = self.session.get(self.endpoints['europe']+f'divisions?countryCodes[]={countryCode}&divisionCategories[]=PostBranch&limit=100&page={len(cities)//100+1}')
            cities += [c['settlement']['name'] for c in r.json()['items']]
        print(len(cities))
        cities = list(set(cities))
        return cities

    def getBranches(self, countryCode, city=None):
        self.updateToken()
        branches = []
        r = self.session.get(self.endpoints['europe']+f'divisions?countryCodes[]={countryCode}&divisionCategories[]=PostBranch&limit=100&page=1' + (f'&textSearch={city}' if city else ''))
        branches += r.json()['items']
        while r.json()['total'] > len(branches):
            r = self.session.get(self.endpoints['europe']+f'divisions?countryCodes[]={countryCode}&divisionCategories[]=PostBranch&limit=100&page={len(branches)//100+1}' + (f'&textSearch={city}' if city else ''))
            branches += r.json()['items']
        return branches
    
    def updateNovaPostData(self):
        data = {}
        # data['countries'] = ['UA']
        data['lastUpdate'] = datetime.now().timestamp()
        data['countryCodes'] = {"ukraine": "UA", "moldova": "MD", "poland": "PL", "lithuania": "LT", "czech": "CZ", "romania": "RO", "germany": "DE", "slovakia": "SK", "estonia": "EE", "latvia": "LV", "hungary": "HU", "italy": "IT", "greatBritain": "GB", "spain": "ES", "france": "FR"}
        data['countries'] = ['UA', 'MD', 'PL', 'LT', 'CZ', 'RO', 'DE', 'SK', 'EE', 'LV', 'HU', 'IT', 'GB', 'ES', 'FR']
        data['cities'] = {}
        for country in data['countries']:
            print(country)
            data['cities'][country] = self.getCities(country)
        with open('novapost.json', 'w') as f:
            json.dump(data, f)

    def loadNovaPostData(self):
        with open('novapost.json', 'r') as f:
            return json.load(f)
        
    def loadCountryCodes(self):
        return self.loadNovaPostData()['countryCodes']
        
    def loadCountries(self):
        return self.loadNovaPostData()['countries']
    
    def loadCities(self, countryCode=None):
        if countryCode == None:
            return self.loadNovaPostData()['cities']
        return self.loadNovaPostData()['cities'][countryCode]
    
    def calculateShippingPrice(self, warehouse, destination):
        divisionNumber = None
        if warehouse == 'Kyiv': divisionNumber = "11/159"
        form = {
            "parcels": [
                {
                    "cargoCategory": "parcel",
                    "insuranceCost": "1",
                    "rowNumber": 1,
                    "width": 100,
                    "length": 200,
                    "height": 100,
                    "actualWeight": 1000,
                    "volumetricWeight": 1000
                }
            ],
            "sender": {
                "countryCode": "UA",
                "divisionNumber": divisionNumber,
            },
            "recipient": {
                "countryCode": destination['countryCode'],
                "divisionNumber": destination['divisionNumber']
            }
        }
        r = self.session.post(self.endpoints['ukraine']+'shipments/calculations', json=form)
        print(r.json())


if __name__ == "__main__":
    nova = NovaAPI()
    # nova.updateNovaPostData()
    # with open('divisionsKyiv', 'w') as f:
        # json.dump(nova.getBranches('PL', 'Wroclaw'), f)
    nova.calculateShippingPrice('Kyiv', {'countryCode': 'PL', 'divisionNumber': '50/1'})