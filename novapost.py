import requests, json, os, dotenv
from datetime import datetime, timedelta

dotenv.load_dotenv()

class NovaAPI():
    def __init__(self):
        self.api_key = os.getenv('NOVA_API_KEY')
        self.endpoints = {
            'ukraine': 'https://api.novaposhta.ua/v.1.0/',
            'europe': 'https://api.novapost.com/v.1.0/'
        }
        self.session = requests.Session()
        self.token_expiration = None
        self.updateToken()

    def updateToken(self):
        if self.token_expiration and self.token_expiration < datetime.now():
            return self.token
        
        r = requests.get('https://api.novaposhta.ua/v.1.0/clients/authorization?apiKey='+self.api_key)
        self.token_expiration = datetime.now()+timedelta(hours=1)

        self.session.headers.update({'Authorization': r.json()['jwt']})

    def getCities(self, country_code):
        self.updateToken()
        cities = []
        r = self.session.get(self.endpoints['europe']+f'divisions?countryCodes[]={country_code}&divisionCategories[]=PostBranch&limit=100&page=1')
        cities += [c['settlement']['name'] for c in r.json()['items']]
        while r.json()['total'] > len(cities):
            r = self.session.get(self.endpoints['europe']+f'divisions?countryCodes[]={country_code}&divisionCategories[]=PostBranch&limit=100&page={len(cities)//100+1}')
            cities += [c['settlement']['name'] for c in r.json()['items']]
        cities = list(set(cities))
        return cities

    def getBranches(self, country_code, city=None):
        self.updateToken()
        branches = []
        r = self.session.get(self.endpoints['europe']+f'divisions?countryCodes[]={country_code}&divisionCategories[]=PostBranch&limit=100&page=1' + (f'&textSearch={city}' if city else ''))
        branches += r.json()['items']
        while r.json()['total'] > len(branches):
            r = self.session.get(self.endpoints['europe']+f'divisions?countryCodes[]={country_code}&divisionCategories[]=PostBranch&limit=100&page={len(branches)//100+1}' + (f'&textSearch={city}' if city else ''))
            branches += r.json()['items']
        return branches
    
    def updateNovaPostData(self):
        data = {}
        data['countries'] = ['UA']
        # data['countries'] = ['MD', 'PL', 'LT', 'CZ', 'RO', 'DE', 'SK', 'EE', 'LV', 'HU', 'IT', 'GB', 'ES', 'FR']
        data['cities'] = {}
        data['branches'] = {}
        for country in data['countries']:
            print(country)
            data['cities'][country] = self.getCities(country)
            for city in data['cities'][country]:
                print(city)
                data['branches'][city] = self.getBranches(country, city)
        with open('novapostDomestic.json', 'w') as f:
            json.dump(data, f)

    def loadNovaPostData(self):
        with open('novapost.json', 'r') as f:
            return json.load(f)

if __name__ == '__main__':
    nova = NovaAPI()
    # with open("1.json", "w") as f: 
        # json.dump(nova.getBranches('LT'), f)
    nova.updateNovaPostData()