# postpone and notif_off is in UTC
# If program re-run, no job but present in db
# postpone the next day's class
# postponing on sat and sun shouldnt be allowed 
# add cancel button to postpone, cancel and events


from replit import db
import credentials as crd
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta, date, time
import keep_alive
from general import (
    SLOTS,
    SUBJECTS,
    TIMETABLE,
    timeDict,
    compare_time,
    edit_time,
    SUB_ATTENDANCE,
    SUB_LINKS
)
from telebot import types, TeleBot, custom_filters
import random

global bot
global TOKEN

global DOC_INDEX
DOC_INDEX = int(0)
global EVENT_INDEX
EVENT_INDEX = int(0)

ADMINS = crd.ADMINS

TIBIN_USER_ID = crd.CREATOR_USER_ID
TIBIN_USER_NAME = crd.CREATOR_USER_NAME
GRP_ID = crd.GRP_ID

global SHOW_NOTIF
SHOW_NOTIF = True

global temp # variable to add the values taken from different state functions

_SUBJECTS = {val: key for key, val in SUBJECTS.items()} # inverted SUBJECTS dict

#####
global chat_id
#chat_id = crd.CREATOR_USER_ID
#####

db['events'] = []
db['postponed'] = []
db['cancelled'] = []
db['added'] = []

TOKEN = crd.BOT_TOKEN

sched = BackgroundScheduler(timezone='UTC')
sched.remove_all_jobs()

bot = TeleBot(TOKEN)
bot_user_name = crd.BOT_USER_NAME

def SendMessage(text, keyboard=None):
    global chat_id
    bot.send_message(chat_id= chat_id, text=str(text),  reply_markup=keyboard)

def is_not_CR(message):
    if message.from_user.username not in ADMINS:
        msg = 'Only CRs can access this command'
        bot.send_message(chat_id=message.chat.id, text=msg)
        return False

def deleteevent(id):
    id1 = str(id)+ '_1'
    id2 = str(id) + '_2'

    event_desc = ''
    events_list = db['events']
    for i in range(len(events_list)):
        event = events_list[i].split('|')
        if event[0] == id:
            events_list.pop(i)
            event_desc = event[1]
    db['events'] = events_list

    try:
        sched.remove_job(id1)
        sched.remove_job(id2)
    except:
        return ''

    return event_desc

def showUpcomingEvents_first(event_desc, offset_time):
    msg = f'{event_desc} in {offset_time[0]} hours and {offset_time[1]} minutes.'
    SendMessage(msg)

def showUpcomingEvents_second(id, event_desc):
    msg = f'{event_desc} in 5 minutes.'

    events_list = db['events']
    for i in range(len(events_list)):
        event = events_list[i].split('|')
        if event[0] == id:
            events_list.pop(i)
            event_desc = event[1]
    db['events'] = events_list

    SendMessage(msg)

#############################################################################
@bot.message_handler(state = 1)
def Postpone_Time(message):
    global temp
    post_class = db['postponed']
    class_time = f"{message.text}:00"
    class_date = f'{datetime.today().strftime("%Y-%m-%d")} {class_time}'

    sched.add_job(ClassMessage, trigger='date', run_date=class_date, id=f'p_{temp[0]}', args= [temp[0]])
    post_class.append(f"{_SUBJECTS[temp[0]]}|{class_time}")
    bot.delete_state(message.chat.id)
    bot.send_message(chat_id = message.chat.id, text = f'{temp[0]} postponed')
#############################################################################

@bot.message_handler(state = 5)
def AddClass_Time(message):
    global temp     # Full name of the subject. Is a list but has only one element
    add_class = db['added']     # Short name of subject with time seperated by '|'
    class_time = f"{message.text}:00"
    class_date = f'{datetime.today().strftime("%Y-%m-%d")} {class_time}'       # 2021-10-28 19:00:00

    sched.add_job(ClassMessage, trigger='date', run_date=class_date, id=f'a_{temp[0]}', args=[temp[0]])
    add_class.append(f"{_SUBJECTS[temp[0]]}|{class_time}")

    bot.delete_state(message.chat.id)
    bot.send_message(chat_id = message.chat.id, text = f'{temp[0]} added')

def AddUpcomingEvents(id, Desc, event_time, offset_time):
    id1 = str(id) + '_1'
    id2 = str(id) + '_2'

    try:
        event_time = event_time.split()
        if len(event_time) != 5:
            return
        event_time = datetime(int(event_time[0]), int(event_time[1]), int(event_time[2]), int(event_time[3]), int(event_time[4]), int(0))
        event_time = event_time - timedelta(hours = 5, minutes = 30)

        if offset_time != '0 0':
            offset_time = offset_time.split()
            if len(offset_time) != 2:
                return
            _time_1 = event_time - timedelta(hours = int(offset_time[0]), minutes = int(offset_time[1]))
            sched.add_job(showUpcomingEvents_first, 'date', id = id1, run_date = _time_1, args = [Desc, offset_time])

        _time_2 = event_time - timedelta(minutes = int(5))
        sched.add_job(showUpcomingEvents_second, 'date', id = id2, run_date = _time_2, args = [id, Desc])
    except:
        return
    
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    global chat_id
    global temp
    data = call.data.split("_")
    if data[0] == 'c':
        cancel_class = db['cancelled']
        if _SUBJECTS[data[1]] in cancel_class:
            bot.send_message(chat_id= chat_id, text="Already added")
            return 'ok'
        cancel_class.append(_SUBJECTS[data[1]])
        db['cancelled'] = cancel_class
        bot.send_message(chat_id = chat_id, text = f"{data[1]} cancelled")

    elif data[0] == 'p':
        temp = [data[1]]
        bot.set_state(chat_id, 1)
        bot.send_message(chat_id = chat_id, text = f"Please enter the time in 24 hrs (eg: 17:30)")

    elif data[0] == 'a':
        temp = [data[1]]
        bot.set_state(chat_id, 5)
        bot.send_message(chat_id = chat_id, text = f"Please enter the time in 24 hrs (eg: 17:30)")

def class_markup(change_type:str):
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 1
    if change_type == 'a':
        cls_list = [list(SUBJECTS.values[i] for i in range(1, len(SUBJECTS.values())))]
    else:
        cls_list = [list(TIMETABLE.values())[i][datetime.today().weekday()] for i in range(len(TIMETABLE.values()))]
    for cls in cls_list:
        if cls == SUBJECTS['NIL']:
            continue
        markup.add(types.InlineKeyboardButton(cls, callback_data=f"{change_type}_{cls}"))    
    return markup

def ClassMessage(subject):
    keyboard = types.InlineKeyboardMarkup()

    subject_short =_SUBJECTS[subject]


    for post_class in db['postponed']:
        post_class = post_class.split("|")
        class_name = post_class[0]
        if subject_short == class_name:
            msg = f"{subject} postponed to {post_class[1]}"
            bot.send_message(crd.GRP_ID, msg)
            return 'ok'

    for cancel_class in db['cancelled']:
        if subject_short == cancel_class:
            msg = f"{subject} cancelled"
            bot.send_message(crd.GRP_ID, msg)
            return 'ok'

    if  subject != SUBJECTS['NIL']:
        if subject_short != 'LAB':
            keyboard.add(types.InlineKeyboardButton(text="Class Link", url=SUB_LINKS[subject]))
            

            if SUB_ATTENDANCE[subject] != "":
                keyboard.add(types.InlineKeyboardButton(text="Attendance", url=SUB_ATTENDANCE[subject]))

        msg = f"You have {subject} in 5 min."

        bot.send_message(crd.GRP_ID, msg, reply_markup=keyboard)

@bot.message_handler(commands=['start'])
def StartFunc(message):
  bot_welcome = "Hi, I am Mr.Bot. I will be helping you with your class timings. \nUse '/' to see the commands."
  bot.send_message(chat_id=message.chat.id, text=bot_welcome)

@bot.message_handler(commands = ["nextclass"])
def NextClassFunc(message):
  currentTime =timeDict(datetime.now())
  weekday = datetime.today().weekday()
  msg = "No more class today"
  for slot in SLOTS:
      if  compare_time(slot, currentTime) == 'greater':
          _Time = edit_time(slot, just_time= True, hour=5, minute=30)
          if weekday in [5, 6]:
              msg = "No class today."
              break
          subject = TIMETABLE[slot][weekday]
          if subject != SUBJECTS['NIL']:
              Time = f'{_Time[0]:02}:{_Time[1]:02}'
              msg = "You have " + TIMETABLE[slot][weekday] + " at " + Time
              break
  bot.send_message(chat_id=message.chat.id, text=msg)

@bot.message_handler(regexp = "^/addevent")
def AddEventFunc(message):
  text = message.text
  if is_not_CR(message):
      return 'ok'

  # /addevent|Desc|Final Time(yyyy month day hour minute)|Offset Time(hour minute)
  text = text.split('|')
  if text[0] == '/addevent' and len(text) == 4:
      event_time = text[2].split()
      event_time = datetime(int(event_time[0]), int(event_time[1]), int(event_time[2]), int(event_time[3]), int(event_time[4]), int(0))

      if (datetime.today() + timedelta(hours = int(5), minutes = int(30))) >= event_time:
          TimeJoke = ["Time Travel hasn't been discovered yet", "My watch only goes forward", "Oops! Is the event already over?"]
          msg = TimeJoke[random.randint(0,2)]

      else:
          global EVENT_INDEX
          EVENT_INDEX += 1
          if EVENT_INDEX == 100:
              EVENT_INDEX = 1
          data = f'{EVENT_INDEX}|{text[1]}|{text[2]}|{text[3]}\n'
          db['events'].append(data)
          AddUpcomingEvents(EVENT_INDEX, text[1], text[2], text[3])
          msg = f'"{text[1]}" added'

  else:
      msg = 'Please follow format'
  bot.send_message(chat_id=message.chat.id, text=msg)

@bot.message_handler(commands = ["showevents"])
def ShowEventFunc(message):
    msg = ''
    for event in db['events']:
        event = event.split('|')
        if(len(event) == int(4)):
            msg += f'{event[0]} | {event[1]} | {event[2]} | {event[3]}\n'
    if msg == '':
        msg = 'No events found'
    bot.send_message(chat_id=message.chat.id, text=msg)

@bot.message_handler(regexp = "^/deleteevent")
def DeleteEventFunc(message):
    if is_not_CR(message):
      return 'ok'

    text = message.text

    text = text.split('|')
    if len(text) == 2:
        event_desc = deleteevent(text[1])
        if event_desc == '':
            msg = 'Something went wrong.'
        else:
            msg = f'"{event_desc}" deleted'
    else:
        msg = 'Please follow format'
    bot.send_message(chat_id=message.chat.id, text=msg)

@bot.message_handler(commands = ["postponeclass"])
def PostponeClassFunc(message):
    global chat_id
    chat_id = message.chat.id
    
    if is_not_CR(message):
      return 'ok'

    msg = "Please select the class to be postponed. /cancel to cancel"
    bot.send_message(chat_id= message.chat.id, text=msg, reply_markup=class_markup('p'))

@bot.message_handler(commands = ["showpostpone"])
def ShowPostponeFunc(message):
    msg = ''
    for i in db['postponed']:
        msg += f"{i}\n"
    if msg == '':
        msg = 'No class postponed'
    bot.send_message(chat_id=message.chat.id, text=msg)

@bot.message_handler(commands = ["deletepostpone"])
def DeletePostponeFunc(message):
    if is_not_CR(message):
      return 'ok'

    for post_class in db['postponed']:
        post_class = post_class.split('|')[0]
        id = f"p_{SUBJECTS[post_class]}"
        sched.remove_job(id)

    del db['postponed']
    db['postponed'] = []

    bot.send_message(chat_id=message.chat.id, text="Removed")

@bot.message_handler(commands = ["cancelclass"])
def CancelClassFunc(message):
    global chat_id
    chat_id = message.chat.id
    if is_not_CR(message):
      return 'ok'

    msg = "Please select the class to be cancelled"
    bot.send_message(chat_id= message.chat.id, text=msg, reply_markup=class_markup('c'))

@bot.message_handler(commands = ["showcancel"])
def ShowCancelFunc(message):
    msg = ''
    for i in db['cancelled']:
        msg += f"{i}\n"
    if msg == '':
        msg = 'No class cancelled'
    bot.send_message(chat_id=message.chat.id, text=msg)

@bot.message_handler(commands = ["deletecancel"])
def DeleteCancelFunc(message):
    if is_not_CR(message):
      return 'ok'
      
    del db['cancelled']
    db['cancelled'] = []

    bot.send_message(chat_id=message.chat.id, text="Removed")

@bot.message_handler(commands = ["showadded"])
def ShowAddedFunc(message):
    msg = ''
    for i in db['added']:
        msg += f"{i}\n"
    if msg == '':
        msg = 'No class added'
    bot.send_message(chat_id=message.chat.id, text=msg)

@bot.message_handler(regexp = "^/timetable")
def TimeTableFunc(message):
    key_list = list(SUBJECTS.keys())
    val_list = list(SUBJECTS.values())

    text = message.text
    isTibin = True
    if message.from_user.username != TIBIN_USER_NAME:
        isTibin = False

    is_today = False

    try:
        text = text.split('|')
        week = {'mon' : int(0), 'tue' : int(1), 'wed' : int(2), 'thur' : int(3), 'fri' : int(4)}
        week_full = {int(0) : 'Monday', int(1) : 'Tueday', int(2) : 'Wednesday', int(3) : 'Thursday', int(4) : 'Friday'}
        if text[0] == '/timetable' and len(text) == 2:
            is_today = False
            n_week = week[text[1].lower()]

        else:
            is_today = True
            if (datetime.today().hour < int(16)):
                n_week = datetime.today().weekday()
            else:
                n_week = datetime.today().weekday() + 1
                if n_week > int(4):
                    n_week = int(0)
            
        if isTibin: 
            offset_time = (int(3), int(0))
        else:
            offset_time = (int(5), int(30))

        msg = week_full[n_week] + ' :\n\n'
        for slot in SLOTS:
            class_name = TIMETABLE[slot][n_week]

            if is_today:
                subject_short = key_list[val_list.index(class_name)]

            if subject_short in db['cancelled']:
                class_name = f"Cancelled {subject_short}"

            slot_time = edit_time(slot, hour = offset_time[0], minute = offset_time[1])
            msg += f'{slot_time[0]:02} : {slot_time[1]:02}    {class_name}\n'

        bot.send_message(chat_id=message.chat.id, text=msg)
    
    except Exception as e:
        print(e)

    return 'ok'

def turn_on_notif ():
    global SHOW_NOTIF
    SHOW_NOTIF = True
    sched.delete_job('turn_on_notif')

@bot.message_handler(state=3)
def OffDaysFunc_Days(message):
    bot.delete_state(message.chat.id)
    global SHOW_NOTIF
    SHOW_NOTIF = False
    sched.add_job(turn_on_notif, trigger='date', run_date=message.text+':00', id='trun_on_notif', replace_existing=True)
    bot.send_message(chat_id=message.chat.id, text=f"Notification turned off for {message.text} days")

@bot.message_handler(commands = ["offdays"])
def OffDaysFunc(message):
    bot.set_state(message.chat.id, 3)
    bot.send_message(chat_id=message.chat.id, text="Till which date should the notification be switched off?\nWrite the date as year-month-day hour(24hrs):minute (eg: 2021-10-29 17:30)")

@bot.message_handler(commands=["addclass"])
def AddClass(message):
    bot.set_state(message.chat.id, 4)
    bot.send_message(chat_id=message.chat.id, text="Please select the class to be added today.", reply_markup=class_markup('a'))

def UpcomingClass(slot):
    subject = TIMETABLE[slot][datetime.today().weekday()]
    ClassMessage(subject)

for slot in SLOTS:
    _time=edit_time(slot,just_time= True, minute= -5)
    sched.add_job(UpcomingClass, 'cron', day_of_week= 'mon-fri', hour = _time[0], minute= _time[1], second= int(0), args = [slot], id= f'{slot[0]} {slot[1]}', replace_existing=True)

def reset_daily():
    # for key in db.keys():
    #     print(key)
    #     del db[key]

    db['events'] = []
    db['postponed'] = []
    db['cancelled'] = []
    db['added'] = []

sched.add_job(reset_daily, trigger='cron', hour='22', minute='30')

bot.add_custom_filter(custom_filters.StateFilter(bot))
bot.add_custom_filter(custom_filters.IsDigitFilter())

keep_alive.keep_alive()

# def PingSite():
#     requests.get('https://api.github.com')
# sched.add_job(PingSite, 'interval', minutes=int(28))

sched.start()
bot.infinity_polling()