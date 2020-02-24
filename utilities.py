import datetime
def changeTimeFormat(time_string):
    dt = datetime.datetime.strptime(time_string,'%H:%M')
    timeAsSeconds = ((dt.hour)*60*60)+(dt.minute*60)
    return timeAsSeconds