from datetime import date, datetime, timedelta
import re

# reminder: everything in the future
LATER = "(in|later|after|next|coming)"
AGO = "(before|earlier than)"

WEEKDAYS1 = ["monday", "tuesday", "wednesday", "thursday", "friday", "satuarday", "sunday"]
WEEKDAYS2 = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

MONS1 = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"]

MONS2 = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]

def preprocess(s):
  s.strip("\n").strip(" ")
  s = " ".join(s.split())
  return s.lower()


def getReferenceDate(s):
  r = date.today()
  y, m, d = r.year, r.month, r.day
  set = [False, False, False]

  ss = s.split()

  # Weekdays
  for x in range(0, len(WEEKDAYS1)):
    if WEEKDAYS1[x] in s or WEEKDAYS2[x] in ss:
      r += timedelta((x-r.weekday())%7)
      return r

  # "MONS (Dayth)"
  for x in range(0, len(MONS1)):
    if MONS1[x] in s or MONS2[x] in ss: 
      m += (x+1-m)%12
      if m > 12: 
        y += m/12
        m %= 12
      if re.search("\d+(nd|st|rd|th)", s):
        d = int(re.search("\d+(nd|st|rd|th)", s).group()[:-2])
      else:
        d = 1  
      return date(y,m, d)
   
  # "2 or 3 NUM separated by . or - or / or ' ' or ,"
  reg1 = re.search("\d+( |-|\.|/|,)\d+( |-|\.|/|,)\d+", s)
  reg2 = re.search("\d+( |-|\.|/|,)\d+", s)
  if reg1 or reg2:
    if reg1: tmp = reg1.group()
    else: tmp = reg2.group()

    for x in [" ", "-", ".", "/"]:
      if x in tmp: tmp = tmp.split(x)
    tmp = list(int(x) for x in tmp)
    if len(tmp) == 3: 
      y, set[0] = max(tmp), True
      tmp.remove(max(tmp))
    if max(tmp)>31: y, m, set[0], set[1] = max(tmp), min(tmp), True, True
    elif max(tmp)>12: m, d, set[1], set[2] = min(tmp), max(tmp), True, True
    else: 
      [m, d] = tmp
      set[1] = set[2] = True
     
  # "4d as year"
  if re.search("\d\d\d\d", s) and not set[0]:
    tmp = int(re.search("\d+", s).group())
    y, set[0] = max(tmp, y), True
    

  # "NUMst,nd,rd,th as day"
  if re.search("\d+(nd|st|rd|th)", s):
    tmp = int(re.compile("\d+(nd|st|rd|th)").group()[:-2])
    if tmp < d and not set[1]:
      m += 1
      if m > 12: 
        m %= 12
        y += 1
    d, set[2] = tmp, True

  if set[0] and not set[1]: m, d = 1, 1
  if set[0] and set[1] and not set[2]: d = 1
  return date(y, m, d)
  
 
def parseDate(s):
  r = getReferenceDate(s)
  #print r

  # "THIS" == BY case
  if re.search("this", s):
    if "week" in s: r += timedelta(days=6-r.weekday())
    elif "month" in s:
      if r.month < 12: r = date(r.year, r.month+1, 1)-timedelta(days=1)
      else: r = date(r.year, 12, 31)
    elif "year" in s: r = date(r.year, 12, 31)
    return r

  # today == FIX DATE
  if "today" in s:
    return r

  # LATER days, change reference
  if "tomorrow" in s:
    r += timedelta(days=1)

  if "yesterday" in s:
    r -= timedelta(days=1)

  # Date by offset
  while True:
    reg1 = re.search("\d+ (days|weeks|months|years)", s)
    reg2 = re.search("the (day|weeks|month|year)", s)
    reg3 = re.search("1 (day|week|month|year)", s)
    if reg1 or reg2 or reg3:
      if reg1:
        tmp = reg1.group().split()
        tmp[0] = int(tmp[0])
      else: 
        reg2 = reg2 if reg2 else reg3
        tmp = [1, reg2.group().split()[1]]

      if re.search(AGO, s): mul = -1 
      elif re.search(LATER, s): mul = 1
      else: mul = 0

      if "day" in tmp[1]: r += timedelta(days=mul*tmp[0])
      if "week" in tmp[1]: r += timedelta(days=mul*tmp[0]*7)
      if "year" in tmp[1]: r = date(r.year+mul*tmp[0], r.month, r.day)
      if "month" in tmp[1]:
        m = r.month + mul*tmp[0]
        y = r.year
        if m > 12:
          y += m/12
          m %= 12
        r = date(y, m, r.day)

      ss = list(x for x in s.split() if x not in tmp)
      s = " ".join(ss)

    else: break

  return r

def parseTime(s):
  r = datetime.now()
  # NUM NUM seperated by : or " "
  if re.search("\d+( |:)\d+",s):
    tmp = re.search("\d+( |:)\d+",s).group()
    for x in [" ", ":"]:
      if x in tmp: tmp = tmp.split(x)
    tmp = list(int(x) for x in tmp)
    if "pm" in s: tmp+=12
    return tmp[0], tmp[1]

  # NUM as hour
  if re.search("\d+", s):
    tmp = int(re.search("\d+",s).group())
    if "pm" in s: tmp+=12
    return (tmp, 0)

  return (r.hour+1, 0)
