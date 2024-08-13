from database import Database
import json

database = Database()

# faq = database.getFaq()
# for f in range(len(faq)):
#     del faq[f]['_id']

# with open('json/faq.json', 'w') as f:
#     json.dump(faq, f)

with open('json/faq.json', 'r') as f:
    faq = json.load(f)

for f in faq:
    database.updateFaq(f)