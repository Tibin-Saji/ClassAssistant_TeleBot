from replit import db

for key in db.keys():
  print(key)
  del db[key]


db['events'] = []
db['postponed'] = []
db['cancelled'] = []