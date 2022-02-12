# postpone and is in UTC
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
    compare_time,
    edit_time,
    SUB_ATTENDANCE,
    SUB_LINKS
)
from telebot import types, TeleBot, custom_filters
import random

global bot
global TOKEN

global EVENT_INDEX
EVENT_INDEX = int(0)

ADMINS = crd.ADMINS

TIBIN_USER_ID = crd.CREATOR_USER_ID
TIBIN_USER_NAME = crd.CREATOR_USER_NAME
GRP_ID = crd.GRP_ID

global SHOW_NOTIF

global temp # variable to add the values taken from different state functions

_SUBJECTS = {val: key for key, val in SUBJECTS.items()} # inverted SUBJECTS dict

global chat_id

db['events'] = []
db['postponed'] = []
db['cancelled'] = []
db['added'] = []
db['SHOW_NOTIF'] = True

TOKEN = crd.BOT_TOKEN

sched = BackgroundScheduler(timezone='UTC')
sched.remove_all_jobs()

bot = TeleBot(TOKEN)
bot_user_name = crd.BOT_USER_NAME

def time_uct_to_ist(time_str:str):
    time_str = time_str.split(':')
    time_str[0] = int(time_str[0])
    time_str[1] = int(time_str[1])
    DT = datetime.combine(date.today(), time(hour=time_str[0], minute=time_str[1], second=int(0))) + timedelta(hours= int(5), minutes=int(30))
    return DT.strftime("%H:%M")

def time_ist_to_uct(time_str:str):
    time_str = time_str.split(':')
    time_str[0] = int(time_str[0])
    time_str[1] = int(time_str[1])
    DT = datetime.combine(date.today(), time(hour=time_str[0], minute=time_str[1], second=int(0))) - timedelta(hours= int(5), minutes=int(30))
    return DT.strftime("%H:%M")

def time_ist_to_ast(time_str:str):
    time_str = time_str.split(':')
    time_str[0] = int(time_str[0])
    time_str[1] = int(time_str[1])
    DT = datetime.combine(date.today(), time(hour=time_str[0], minute=time_str[1], second=int(0))) - timedelta(hours= int(2), minutes=int(30))
    return DT.strftime("%H:%M")

def SendMessage(text, keyboard=None):
    global chat_id
    bot.send_message(chat_id= chat_id, text=str(text),  reply_markup=keyboard)

def isInTime(DT:str):
    '''
    DT should be time in ist HH:MM format and it will check if that time is already over that day.
    If it is over, it sends a message telling so and returns false, else it retruns true.
    '''
    if compare_time(DT, edit_time(datetime.today().strftime("%H:%M"), hour=5, minute=30)) == 'lesser':
        TimeJoke = ["Time Travel hasn't been discovered yet", "My watch only goes forward", "Oops! Is the event already over?"]
        bot.send_message(chat_id=chat_id, text=TimeJoke[random.randint(0, len(TimeJoke)) - 1])
        return False
    else:
        return True

def is_not_CR(message):
    if message.from_user.username not in ADMINS:
        msg = 'Only CRs can access this command'
        bot.send_message(chat_id=message.chat.id, text=msg)
        return False
    
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    global chat_id
    global temp

    data = call.data

    if data == "Turn On":
        db['SHOW_NOTIF'] = True
        bot.send_message(chat_id= chat_id, text="Turned On")
    elif data == "Turn Off":
        db['SHOW_NOTIF'] = False
        bot.send_message(chat_id= chat_id, text="Turned Off")

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
        bot.set_state(chat_id, 2)
        bot.send_message(chat_id = chat_id, text = f"Please enter the time in 24 hrs (eg: 17:30)")

    elif data[0] == 'e':
        sched.remove_job(call.data)
        events = db['events']
        for i in range(len(events)):
          if events[i][0] == data[1]:
            events.pop(i)
        db['events'] = events
        msg = f'\"{data[1]} deleted\"'
        bot.send_message(chat_id = chat_id, text = msg)


def class_markup(change_type:str):
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 1
    if change_type == 'a':
        cls_list = [list(SUBJECTS.values())[i] for i in range(1, len(list(SUBJECTS.values())))]
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
        if SUB_LINKS[subject] != "":
            keyboard.add(types.InlineKeyboardButton(text="Class Link", url=SUB_LINKS[subject]))
            

        if SUB_ATTENDANCE[subject] != "":
            keyboard.add(types.InlineKeyboardButton(text="Attendance", url=SUB_ATTENDANCE[subject]))

        msg = f"You have {subject} in 5 min."

        bot.send_message(GRP_ID, msg, reply_markup=keyboard)

@bot.message_handler(commands=['start'])
def StartFunc(message):
  bot_welcome = "Hi, I am Mr.Bot. I will be helping you with your class timings. \nUse '/' to see the commands."
  bot.send_message(chat_id=message.chat.id, text=bot_welcome)

@bot.message_handler(commands = ["nextclass"])
def NextClassFunc(message):
  currentTime = edit_time(datetime.now().strftime("%H:%M"), hour = int(5), minute= int(30))
  weekday = datetime.today().weekday()
  msg = "No more class today"

  offset_time = [0,0]

  if message.from_user.username == TIBIN_USER_NAME:
      offset_time = [-2,-30]

  for slot in SLOTS:
      if  compare_time(slot, currentTime) == 'greater':
          if weekday in [5, 6]:
              msg = "No class today."
              break
          subject = TIMETABLE[slot][weekday]
          if subject != SUBJECTS['NIL']:
              msg = f"You have {TIMETABLE[slot][weekday]} at {edit_time(slot, hour = offset_time[0], minute= offset_time[1])}"
              break
  bot.send_message(chat_id=message.chat.id, text=msg)

@bot.message_handler(commands = ["addevent"])
def EventDescFunc(message):
  if is_not_CR(message):
      return 'ok'
  
  msg = 'Please enter the event description'
  bot.set_state(message.chat.id, 3)
  bot.send_message(chat_id=message.chat.id, text=msg)

@bot.message_handler(state = 3)
def EventTime1Func(message):
  global temp
  temp = []
  temp.append(message.text)
  msg = 'Enter the deadline for the event in YYYY-MM-DD HH:MM (24-hr) format'
  bot.set_state(message.chat.id, 4)
  bot.send_message(chat_id=message.chat.id, text=msg)

@bot.message_handler(state = 4)
def EventTime2Func(message):
  global temp
  temp.append(message.text)
  msg = 'Enter the reminder time for the event in HH:MM 24-hr format'
  bot.set_state(message.chat.id, 5)
  bot.send_message(chat_id=message.chat.id, text=msg)

@bot.message_handler(state = 5)
def EventSetFunc(message):
  global temp
  temp.append(message.text)
  msg = 'Event Added'
  bot.delete_state(message.chat.id)
  event_date = temp[1].split()[0] + ' ' + temp[2] + ':00'
  sched.add_job(EventJob1Call, trigger='date', run_date=event_date, id=f"e_{temp[0]}", args= [temp[0], temp[1]])
  db['events'].append(temp)
  bot.send_message(chat_id=message.chat.id, text=msg)

def EventJob1Call(Desc:str, deadline:str):
  msg = f'You have \"{Desc}\" at {deadline}'
  sched.add_job(EventJob2Call, trigger='date', run_date=deadline, id=f'e_{temp[0]}', args= [temp[0]])
  bot.send_message(chat_id=GRP_ID, text=msg)

def EventJob2Call(Desc:str):
  events = db['events']
  for i in range(len(events)):
      if events[i][0] == Desc:
          events.pop(i)
  db['events'] = events
  msg = f'You have \"{Desc}\" now'
  bot.send_message(chat_id=GRP_ID, text=msg)
  
@bot.message_handler(commands = ["showevents"])
def ShowEventFunc(message):
    msg = ''
    for event in db['events']:
      msg += f'{event[0]}  {event[1]}  {event[2]}\n'
    if msg == '':
      msg = 'No events found'
    bot.send_message(chat_id=message.chat.id, text=msg)

@bot.message_handler(commands = ["deleteevent"])
def DeleteEventFunc(message):
    if is_not_CR(message):
      return 'ok'

    global chat_id
    chat_id = message.chat.id

    msg = 'Select the event to be deleted'

    markup = types.InlineKeyboardMarkup()
    markup.row_width = 1

    if len(db['events']) > 0:
        for event in db['events']:
            markup.add(types.InlineKeyboardButton(event[0], callback_data=f"e_{event[0]}"))    
    else:
        markup = None

    bot.send_message(chat_id=message.chat.id, text=msg, reply_markup = markup)

@bot.message_handler(commands = ["postponeclass"])
def PostponeClassFunc(message):
    global chat_id
    chat_id = message.chat.id
    
    if is_not_CR(message):
      return 'ok'

    if (datetime.today().weekday() not in [5,6]):
        msg = "Please select the class to be postponed. /cancel to cancel"
        bot.send_message(chat_id= message.chat.id, text=msg, reply_markup=class_markup('p'))
    else:
        msg = "No classes to postpone today"
        bot.send_message(chat_id= message.chat.id, text=msg)

#############################################################################
@bot.message_handler(state = 1)
def Postpone_Time(message):
    global temp
    post_class = db['postponed']
    if not isInTime(time_ist_to_uct(message.text)):
        bot.set_state(message.chat.id, 1)
        return 'ok'
    class_time = f"{edit_time(time_ist_to_uct(message.text), minutes = -5)}:00"
    class_date = f'{datetime.today().strftime("%Y-%m-%d")} {class_time}'

    sched.add_job(ClassMessage, trigger='date', run_date=class_date, id=f'p_{temp[0]}', args= [temp[0]])
    post_class.append(f"{_SUBJECTS[temp[0]]}|{message.text}")
    bot.delete_state(message.chat.id)
    bot.send_message(chat_id = message.chat.id, text = f'{temp[0]} postponed')
#############################################################################

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

    if (datetime.today().weekday() not in [5,6]):
        msg = "Please select the class to be cancelled"
        bot.send_message(chat_id= message.chat.id, text=msg, reply_markup=class_markup('c'))
    else:
        msg = "No classes to cancel today"
        bot.send_message(chat_id= message.chat.id, text=msg)

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

@bot.message_handler(commands=["addclass"])
def AddClassFunc(message):
    global chat_id
    chat_id = message.chat.id
    
    if is_not_CR(message):
      return 'ok'
    bot.set_state(message.chat.id, 4)
    bot.send_message(chat_id=message.chat.id, text="Please select the class to be added today.", reply_markup=class_markup('a'))

@bot.message_handler(state = 2)
def AddClass_Time(message):
    global temp     # Full name of the subject. Is a list but has only one element
    add_class = db['added']     # Short name of subjects with time seperated by '|'
    if not isInTime(message.text):
        bot.set_state(message.chat.id, 5)
        return 'ok'
    class_time = edit_time(time_ist_to_uct(message.text), minutes = -5) + ":00"
    run_date = f'{datetime.today().strftime("%Y-%m-%d")} {class_time}'       # 2021-10-28 19:00:00

    sched.add_job(ClassMessage, trigger='date', run_date=run_date, id=f'a_{temp[0]}', args=[temp[0]])
    add_class.append(f"{_SUBJECTS[temp[0]]}|{message.text}")

    bot.delete_state(message.chat.id)
    bot.send_message(chat_id = message.chat.id, text = f'{temp[0]} added')

@bot.message_handler(commands = ["showadd"])
def ShowAddFunc(message):
    msg = ''
    for i in db['added']:
        msg += f"{i}\n"
    if msg == '':
        msg = 'No class added'
    bot.send_message(chat_id=message.chat.id, text=msg)

@bot.message_handler(commands = ["deleteadd"])
def DeleteAddFunc(message):
    if is_not_CR(message):
      return 'ok'
      
    del db['added']
    db['added'] = []

    bot.send_message(chat_id=message.chat.id, text="Removed")

@bot.message_handler(regexp = "^/timetable")
def TimeTableFunc(message):
    key_list = list(SUBJECTS.keys())
    val_list = list(SUBJECTS.values())

    offset_time = [0,0]

    text = message.text
    if(message.from_user.username == TIBIN_USER_NAME):
        offset_time = [-2,-30]

    try:
        text = text.split('|')
        week = {'mon' : int(0), 'tue' : int(1), 'wed' : int(2), 'thur' : int(3), 'fri' : int(4), 'sat' : int(5), 'sun' : int(6)}
        week_full = {int(0) : 'Monday', int(1) : 'Tueday', int(2) : 'Wednesday', int(3) : 'Thursday', int(4) : 'Friday', int(5) : 'Saturday', int(6) : 'Sunday'}
        if text[0] == '/timetable' and len(text) == 2:
            #is_today = False
            n_week = week[text[1].lower()]

        else:
            #is_today = True
            if (datetime.today().hour < int(16)):
                n_week = datetime.today().weekday()
            elif (datetime.today().weekday() > 4):
                n_week = 0;
            else:
                n_week = datetime.today().weekday() + 1

        msg = f"*{week_full[n_week]}*:\n\n"

        if n_week > int(4):
            msg += "No class today\n"

        else:
            for slot in SLOTS:
                class_name = TIMETABLE[slot][n_week]

                subject_short = key_list[val_list.index(class_name)]

                if subject_short in db['cancelled']:
                    class_name = f"Cancelled {subject_short}"

                msg += f'{edit_time(slot, hour = offset_time[0], minute= offset_time[1])}    {class_name}\n'

        
        if len(db['added']) != 0:
            msg += "\n*Added Classes*\n\n"
            for cls in db['added']:
                cls = cls.split('|')
                msg += f"{edit_time(cls[1], hour = offset_time[0], minute= offset_time[1])}    {SUBJECTS[cls[0]]}\n"

        if len(db['postponed']) != 0:
            msg += "\n*Postponed Classes*\n\n"
            for cls in db['postponed']:
                cls = cls.split('|')
                msg += f"{edit_time(cls[1], hour = offset_time[0], minute= offset_time[1])}    {SUBJECTS[cls[0]]}\n"
        
        if len(db['cancelled']) != 0:
            msg += "\n*Cancelled Classes*\n\n"
            for cls in db['cancelled']:
                msg += f"{cls}"

        bot.send_message(chat_id=message.chat.id, text=msg, parse_mode='MARKDOWN')
    
    except Exception as e:
        print(e)

    return 'ok'

@bot.message_handler(commands = ["notifswitch"])
def NotifSwitchFunc(message):
    global chat_id 
    chat_id = message.chat.id
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Turn On", callback_data="Turn On"),types.InlineKeyboardButton("Turn Off", callback_data="Turn Off"))    
    bot.send_message(chat_id=message.chat.id, text="Turn on or turn off notification.", reply_markup= markup)

@bot.message_handler(state = "*", commands=['cancel'])
def CancelFunc(message):
    bot.delete_state(message.chat.id)
    bot.send_message(message.chat.id, "The command has been cancelled")

def UpcomingClass(slot):
    if db['SHOW_NOTIF'] == False:
        return
    subject = TIMETABLE[slot][datetime.today().weekday()]
    ClassMessage(subject)

for slot in SLOTS:
    _time=edit_time(time_ist_to_uct(slot), minute= -5).split(':')
    sched.add_job(UpcomingClass, 'cron', day_of_week= 'mon-fri', hour = _time[0], minute= _time[1], second= int(0), args = [slot], id= f'{slot}', replace_existing=True)

def reset_daily():
    db['postponed'] = []
    db['cancelled'] = []
    db['added'] = []

sched.add_job(reset_daily, trigger='cron', hour='22', minute='30')

bot.add_custom_filter(custom_filters.StateFilter(bot))
bot.add_custom_filter(custom_filters.IsDigitFilter())

keep_alive.keep_alive()

sched.start()
bot.infinity_polling()