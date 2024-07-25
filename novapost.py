import requests, json, os, dotenv
from datetime import datetime, timedelta

dotenv.load_dotenv()

class NovaAPI():
    def __init__(self):
        self.apiKey = os.getenv('NOVA_API_KEY')
        self.endpoints = {
            'ukraine': 'https://api.novaposhta.ua/v.1.0/',
            'europe': 'https://api.novapost.com/v.1.0/',
            'new': 'https://api.novaposhta.ua/v2.0/json/'
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
    
    def calculateShippingPrice(self, warehouse, destination, products):
        print(warehouse, destination, products)
        divisionNumber = None
        if warehouse == 'Kyiv': divisionNumber = "11/99"
        elif warehouse == 'Poltava': divisionNumber = "91/3"
        elif warehouse == 'Ternopil': divisionNumber = "602/15"
        elif warehouse == 'Odesa': divisionNumber = "55/60"
        elif warehouse == 'Ivano-Frankivsk': divisionNumber = "77/3"

        totalDeliveryCost = 0
        form = {
            "parcels": [
                {
                    "cargoCategory": "parcel",
                    "insuranceCost": 0,
                    "rowNumber": 1,
                    "width": 230,
                    "length": 160,
                    "height": 100,
                    "actualWeight": 0,
                    "volumetricWeight": 0,
                }
            ],
            "sender": {
                "countryCode": "UA",
                "divisionNumber": divisionNumber,
            },
            "recipient": {
                "countryCode": destination['countryCode'],
                "divisionNumber": destination['branch']
            }
        }
        groups = [products[i:i+2] for i in range(0, len(products), 2)]
        for group in groups:
            form['parcels'][0]['insuranceCost'] = sum([product['info']['price'] for product in group])
            form['parcels'][0]['actualWeight'] = 1000 * len(group)
            form['parcels'][0]['volumetricWeight'] = 1000 * len(group)
            form['parcels'][0]['width'] = 230 if form['parcels'][0]['volumetricWeight'] == 1000 else 330
            form['parcels'][0]['length'] = 160 if form['parcels'][0]['volumetricWeight'] == 1000 else 230

            r = self.session.post(self.endpoints['ukraine']+'shipments/calculations', json=form)

            print(r.json())
            totalDeliveryCost += r.json()['services'][0]['cost']
        return totalDeliveryCost


if __name__ == "__main__":
    nova = NovaAPI()
    # print(nova.getBranches('PL', 'Wrockl'))
    # city = 'Poltava'
    # with open(f'divisions{city}.json', 'w') as f:
    #     json.dump(nova.getBranches('UA', city), f)
    price = nova.calculateShippingPrice('Kyiv', {'countryCode': 'UA', 'branch': '12/8'}, 
                                        [
                                            {'info': {'category': 'Sandals', 'price': 2199}}, 
                                            {'info': {'category': 'Boots', 'price': 1999}}
                                        ])
    print(price)