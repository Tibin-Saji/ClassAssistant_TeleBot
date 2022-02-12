from datetime import datetime, timedelta, time, date

slot1 = "08:00"    # 7:55       5:25
slot2 = "09:00"    # 8:55       6:25
slot3 = "10:15"    # 10:10      7:40
slot4 = "11:15"    # 11:10      8:40
slot5 = "13:00"    # 12:55      10:25
slot6 = "14:00"    # 13:55      11:25
slot7 = "17:00"    # 16:55      14:25

SLOTS = [slot1, slot2, slot3, slot4, slot5, slot6, slot7]

SUBJECTS = {
    'NIL' : "No Class",
    'EC1' : "Electronics Circuits I",
    'EMFTA'  : "Electro-magnetic Field Theory A",
    'EMFTB'  : "Electro-magnetic Field Theory B",
    'CTS1A' : "Communnication Theory & Systems I A",
    'CTS1B' : "Communnication Theory & Systems I B",
    'MPMC': "Microprocessors & MicroconMicrocontrollers",
    'MA4' : "Mathematics IV",
    'MATUT' : "Mathematics Tutorial",
    'LAB1': "EC Lab for R and MPMC Lab for S",
    'LAB2': "EC Lab for S and MPMC Lab for R",

}

TIMETABLE = {
    SLOTS[0]:
        [SUBJECTS['EC1'], SUBJECTS['CTS1B'], SUBJECTS['NIL'], SUBJECTS['MA4'], SUBJECTS['MPMC']],
    SLOTS[1]:
        [SUBJECTS['NIL'], SUBJECTS['EMFTB'], SUBJECTS['EC1'], SUBJECTS['CTS1B'], SUBJECTS['NIL']],
    SLOTS[2]:
        [SUBJECTS['MA4'], SUBJECTS['MPMC'], SUBJECTS['EMFTA'], SUBJECTS['EMFTB'], SUBJECTS['EC1']],
    SLOTS[3]:
        [SUBJECTS['CTS1A'], SUBJECTS['NIL'], SUBJECTS['MA4'], SUBJECTS['MPMC'], SUBJECTS['EMFTA']],
    SLOTS[4]:
        [SUBJECTS['NIL'], SUBJECTS['EC1'], SUBJECTS['NIL'], SUBJECTS['NIL'], SUBJECTS['NIL']],
    SLOTS[5]:
        [SUBJECTS['MATUT'], SUBJECTS['NIL'], SUBJECTS['LAB1'], SUBJECTS['LAB2'], SUBJECTS['CTS1A']],
    SLOTS[6]:
        [SUBJECTS['NIL'], SUBJECTS['NIL'], SUBJECTS['NIL'], SUBJECTS['NIL'], SUBJECTS['NIL']]
}

SUB_LINKS = {
    SUBJECTS['EC1'] : "https://eduserver.nitc.ac.in/course/view.php?id=2361#section-1",
    SUBJECTS['EMFTA'] : "https://nitcalicut.webex.com/nitcalicut/j.php?MTID=m6a7175f6b973bf4c22a9bd361423459d",
    SUBJECTS['EMFTB'] : "https://nitcalicut.webex.com/nitcalicut/o.php?AT=ST&SP=MC&BU=https%3A%2F%2Feduserver.nitc.ac.in%2Fmod%2Fwebexactivity%2Fview.php%3Fid%3D90519%26action%3Djoinmeeting",
    SUBJECTS['CTS1A'] : "https://eduserver.nitc.ac.in/mod/webexactivity/view.php?id=90509",
    SUBJECTS['CTS1B'] : "https://nitcalicut.webex.com/webappng/sites/nitcalicut/meeting/info/be740faf5b1140379d31346cc54b6514?siteurl=nitcalicut&MTID=me681e670b69c7cefb6103ef1b45ec249",
    SUBJECTS['MPMC'] : "https://nitcalicut.webex.com/nitcalicut/j.php?MTID=m38558e55e47941e6943dfbcd380fe9d0",
    SUBJECTS['MA4'] : "https://nitcalicut.webex.com/nitcalicut/j.php?MTID=m4f855125f95f1b5e54ebd21afc89e7e9",
    SUBJECTS['MATUT'] : "",
    SUBJECTS['LAB1'] : "",
    SUBJECTS['LAB2'] : ""
}

SUB_ATTENDANCE = {
    SUBJECTS['EC1'] : "https://eduserver.nitc.ac.in/course/view.php?id=2361#section-1",
    SUBJECTS['EMFTA'] : "https://eduserver.nitc.ac.in/mod/attendance/view.php?id=89332&view=1",
    SUBJECTS['EMFTB'] : "https://eduserver.nitc.ac.in/mod/attendance/view.php?id=90520&view=1",
    SUBJECTS['CTS1A'] : "https://eduserver.nitc.ac.in/mod/attendance/view.php?id=90511&view=1",
    SUBJECTS['CTS1B'] : "",
    SUBJECTS['MPMC'] : "https://eduserver.nitc.ac.in/mod/attendance/view.php?id=90700&view=1",
    SUBJECTS['MA4'] : "",
    SUBJECTS['MATUT'] : "",
    SUBJECTS['LAB1'] : "",
    SUBJECTS['LAB2'] : ""
}

def str_to_tuple(time_str:str):
    time_str = time_str.split(':')
    return (int(time_str[0]), int(time_str[1]))

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

def edit_time(DT:str, day:int=0, hour:int=0, minute:int=0, second:int=0, change_day = True):
    DT = str_to_tuple(DT)
    DT_now = datetime.combine(date.today(), time(hour=DT[0], minute=DT[1], second=0))
    DateTime = DT_now + timedelta(days=day,hours= hour, minutes= minute, seconds= second)
    if not change_day:
        DT_diff = DateTime - datetime.combine(date.today(), time(0, 0, 0))
        if DT_diff.total_seconds() < 0:
            return '-1:-1'
    return DateTime.strftime('%H:%M')