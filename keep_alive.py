from apscheduler.schedulers.background import BackgroundScheduler 
from flask import Flask
import requests
from threading import Thread

app = Flask('')
sched = BackgroundScheduler()

@app.route('/')
def main():
  return "Your bot is alive!"

def run():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    server = Thread(target=run)
    server.start()

def PingSite():
    requests.get('https://ClassAssistantTeleBot-1.tibinsaji.repl.co')
    

sched.add_job(PingSite, 'interval', minutes=int(15))

sched.start()