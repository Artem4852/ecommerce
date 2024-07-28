import json, requests
from shapely.geometry import shape, Point
from datetime import datetime
from database import Database

with open('regions.json') as f:
    regions = json.load(f)
regions = {region['properties']['name']: shape(region['geometry']) for region in regions['features']}

def getRegion(coords):
    point = Point(coords)
    for region, polygon in regions.items():
        if polygon.contains(point):
            return region
    return None

def log(page, request=None, ip=None):
    if ip: userIp = ip
    elif request.headers.get('X-Forwarded-For'): userIp = request.headers.get('X-Forwarded-For').split(',')[0]
    else: userIp = request.remote_addr
    ipData = requests.get(f'http://ipinfo.io/{userIp}/json').json()
    if "bogon" in ipData: return

    now = datetime.now()
    day = now.strftime("%d.%m.%Y")
    hour = now.strftime("%H:00")

    city = ipData['city'].lower()
    if ipData['country'] == 'UA':
        region = getRegion(tuple(map(float, ipData['loc'].split(',')))[::-1])
    else:
        codesCountry = requests.get(f'https://restcountries.com/v3.1/alpha/{ipData["country"]}').json()
        region = codesCountry['name']['common'].lower()

    db = Database()
    dailyRequests = db.getStats('dailyRequests')
    if not day in dailyRequests:
        dailyRequests['data'][day] = 0
    dailyRequests['data'][day] += 1
    db.updateStats('dailyRequests', dailyRequests)

    hourlyRequests = db.getStats('hourlyRequests')
    if not hour in hourlyRequests['data']:
        hourlyRequests['data'][hour] = 0
    hourlyRequests['data'][hour] += 1
    db.updateStats('hourlyRequests', hourlyRequests)

    regionDistribution = db.getStats('regionDistribution')
    if not region in regionDistribution:
        regionDistribution['data'][region] = 0
    regionDistribution['data'][region] += 1

    cityDistribution = db.getStats('cityDistribution')
    if not city in cityDistribution:
        cityDistribution['data'][city] = 0
    cityDistribution['data'][city] += 1

    print(page, day, hour, city, region)

if __name__ == '__main__':
    print(getRegion((37.2768, 49.2070)))