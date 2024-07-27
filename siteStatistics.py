import json
from shapely.geometry import shape, Point
from database import Database

with open('regions.json') as f:
    regions = json.load(f)

regions = {region['properties']['name']: shape(region['geometry']) for region in regions['features']}
print(regions['central'])