# ClassAssistant_TeleBot
The bot sends notification of class 5 minutes prior to the class along with the class link and attendance link as buttons.
1. Got to @BotFather in telegram and create a bot.
2. Add details in credential.py. Use @userinfobot toget group id. Creator id and username are optional if you want personalised functions.
3. In general.py, add the class names, their meeting links and attendance links.

Functons
/start - Greeting 
/timetable - Timetable of the day 
/nextclass - Next class that day 
/cancelclass - Cancel a class of the day (CR) 
/showcancel - List of classes cancelled 
/deletecancel - Clear list of cancelled classes (CR) 
/postponeclass - Postpone a class of the day to a specific time (CR) 
/showpostpone - List of class postponed 
/deletepostpone - Clear list of postponed classes (CR) 
/notifswitch - Turn of or on notification (CR)
/cancel - cancel a command thread
