import json, requests
from flask import redirect, url_for
from shapely.geometry import shape, Point
from werkzeug.datastructures import MultiDict
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
    db = Database()

    utmSource = request.args.get('utmSource')
    if utmSource:
        utmSources = db.getStats('utmSources')
        if not utmSource in utmSources['data']:
            utmSources['data'][utmSource] = 0
        utmSources['data'][utmSource] += 1
        db.updateStats('utmSources', utmSources)

        args = MultiDict(request.args)
        args.pop('utmSource')
        return redirect(url_for(request.endpoint, **args))

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
        countryData = requests.get(f'https://restcountries.com/v3.1/alpha/{ipData["country"]}').json()
        region = countryData[0]['name']['common'].lower()

    dailyRequests = db.getStats('dailyRequests')
    if not day in dailyRequests['data']:
        dailyRequests['data'][day] = 0
    dailyRequests['data'][day] += 1
    db.updateStats('dailyRequests', dailyRequests)

    hourlyRequests = db.getStats('hourlyRequests')
    if not hour in hourlyRequests['data']:
        hourlyRequests['data'][hour] = 0
    hourlyRequests['data'][hour] += 1
    db.updateStats('hourlyRequests', hourlyRequests)

    pageDistribution = db.getStats('pageDistribution')
    if not page in pageDistribution['data']:
        pageDistribution['data'][page] = 0
    pageDistribution['data'][page] += 1
    db.updateStats('pageDistribution', pageDistribution)

    regionDistribution = db.getStats('regionDistribution')
    if not region in regionDistribution['data']:
        regionDistribution['data'][region] = 0
    regionDistribution['data'][region] += 1
    db.updateStats('regionDistribution', regionDistribution)

    cityDistribution = db.getStats('cityDistribution')
    if not city in cityDistribution['data']:
        cityDistribution['data'][city] = 0
    cityDistribution['data'][city] += 1
    db.updateStats('cityDistribution', cityDistribution)

if __name__ == '__main__':
    print(getRegion((37.2768, 49.2070)))