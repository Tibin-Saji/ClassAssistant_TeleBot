from datetime import datetime, timedelta, time, date

slot1 = "08:00"    # 7:55       5:25
slot2 = "09:00"    # 8:55       6:25
slot3 = "10:15"    # 10:10      7:40
slot4 = "11:15"    # 11:10      8:40
slot5 = "13:00"    # 12:55      10:25
slot6 = "14:00"    # 13:55      11:25
slot7 = "17:00"    # 16:55      14:25         11 30

SLOTS = [slot1, slot2, slot3, slot4, slot5, slot6, slot7]

SUBJECTS = {
    'NIL' : "No Class",
    'SSD' : "Solid State Devices",
    'SS'  : "Signals and Systems",
    'DCS' : "Digital Circuits and Systems",
    'ECNT': "Electrical Circuits and Network Theory",
    'MA3' : "Mathematics III",
    'VE'  : "Value Education",
    'LAB': "DCS and DN Labs",

}

TIMETABLE = {
    SLOTS[0]:
        [SUBJECTS['SSD'], SUBJECTS['NIL'], SUBJECTS['NIL'], SUBJECTS['DCS'], SUBJECTS['ECNT']],
    SLOTS[1]:
        [SUBJECTS['SS'], SUBJECTS['MA3'], SUBJECTS['SSD'], SUBJECTS['NIL'], SUBJECTS['NIL']],
    SLOTS[2]:
        [SUBJECTS['DCS'], SUBJECTS['ECNT'], SUBJECTS['SS'], SUBJECTS['MA3'], SUBJECTS['SSD']],
    SLOTS[3]:
        [SUBJECTS['NIL'], SUBJECTS['NIL'], SUBJECTS['DCS'], SUBJECTS['ECNT'], SUBJECTS['SS']],
    SLOTS[4]:
        [SUBJECTS['MA3'], SUBJECTS['SSD'], SUBJECTS['NIL'], SUBJECTS['NIL'], SUBJECTS['NIL']],
    SLOTS[5]:
        [SUBJECTS['NIL'], SUBJECTS['DCS'], SUBJECTS['MA3'], SUBJECTS['LAB'], SUBJECTS['LAB']],
    SLOTS[6]:
        [SUBJECTS['NIL'], SUBJECTS['NIL'], SUBJECTS['ECNT'], SUBJECTS['SS'], SUBJECTS['NIL']]
    # SLOTS[7].strftime("%H %M"):
    #     [SUBJECTS['NIL'], SUBJECTS['SSD'], SUBJECTS['ECNT'], SUBJECTS['MA3'], SUBJECTS['SS']]
    # slotTest1.strftime("%H %M"):
    #     ["TestClass1", "TestClass2","TestClass3", "TestClass4","TestClass5"]
}

SUB_LINKS = {
    SUBJECTS['SS'] : 'https://nitcalicut.webex.com/nitcalicut/j.php?MTID=mefb99f19ac24ea19aa15d24c6062d3b1',
    SUBJECTS['DCS'] : 'https://nitcalicut.webex.com/nitcalicut/j.php?MTID=m8832367923e264671c7ca251b752ff21',
    SUBJECTS['VE'] : "https://nitcalicut.webex.com/wbxmjs/joinservice/sites/nitcalicut/meeting/download/a44ee30a3147f25b9aaed3abfe578945?protocolUID=4740f7fad7e3791ad27366ef6924e4fd&MTID=m0e98d05b5dc051e41a310946d20fc481#noRefresh",
    SUBJECTS['ECNT'] : "https://eduserver.nitc.ac.in/course/view.php?id=1856#section-2",
    SUBJECTS['MA3'] : "https://eduserver.nitc.ac.in/course/view.php?id=2128",
    SUBJECTS['SSD'] : "https://nitcalicut.webex.com/nitcalicut/j.php?MTID=m69c5a46661eb7fb44e703e32e4712f30",
    SUBJECTS['LAB'] : ""
}

SUB_ATTENDANCE = {
    SUBJECTS['SSD'] : "https://eduserver.nitc.ac.in/mod/attendance/view.php?id=63280&view=1",
    SUBJECTS['DCS'] : "https://eduserver.nitc.ac.in/mod/attendance/view.php?id=63352&view=1",
    SUBJECTS['LAB'] : "https://eduserver.nitc.ac.in/mod/attendance/view.php?id=65810&view=1",
    SUBJECTS['SS']  : "",
    SUBJECTS['VE']  : "", 
    SUBJECTS['MA3'] : "",
    SUBJECTS['ECNT'] : ""
}

def tuple_to_str(tpl:tuple):
    return f"{tpl[0]}:{tpl[1]}"

def str_to_tuple(time_str:str):
    time_str = time_str.split(':')
    return tuple(int(time_str[0]), int(time_str[1]))

def compare_time(DT_1: str, DT_2: str):
    DT_1 = str_to_tuple(DT_1)
    DT_2 = str_to_tuple(DT_2)

    if DT_1[0] > DT_2[0]:
        return 'greater'
    elif DT_1[0] < DT_2[0]:
        return 'lesser'
    else:
        if DT_1[1] >= DT_2[1]:
            return 'greater'
        elif DT_1[1] < DT_2[1]:
            return 'lesser'

def edit_time(DT:str, day:int=0, hour:int=0, minute:int=0, second:int=0):
    DT = str_to_tuple(DT)
    DateTime = datetime.combine(date.today(), time(hour=DT[0], minute=DT[1], second=0)) + timedelta(days=day,hours= hour, minutes= minute, seconds= second)
    return DateTime.strftime('%H:%M')