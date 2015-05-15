from datetime import date
from time import gmtime, strftime
import reminder
import sys


def realtime():
  print "REAL TIME MODE\n--------------"
  greet = strftime("%a, %d %b %Y %H:%M:%S", gmtime())
  print greet+"\n\n:) Hello! I'm ready to set up reminder for you!\n"
  while True:
    event = raw_input(":) What's up?\n")
    print "\nYou are going to: \n"+event+"\n"

    date = raw_input(":) On which day?\n")
    if "exit" in date: break
    d = reminder.parseDate(reminder.preprocess(date))
    w = reminder.WEEKDAYS2[d.weekday()].upper()
    print "\nOn Date: "+w+" %s\n"%d

    time = raw_input(":) At what time?\n")
    if "exit" in time: break
    t = reminder.parseTime(reminder.preprocess(time))
    print "\n@ %02d:%02d\n"%t


def timetest():
  print "TEST MODE\n---------"
  while True:
    date = raw_input("<==")
    if "exit" in date: break
    d = reminder.parseDate(reminder.preprocess(date))
    w = reminder.WEEKDAYS2[d.weekday()].upper()
    print "==>"+w+" %s"%d


jet_prop1 = """
# JET properties file for time tagging
Jet.dataPath      = data
JetTest.fileName1 = """

jet_prop2 = """
Timex.rule        = time_rules.yaml
Timex.refTime     = """

jet_prop3 = """
processSentence  = tokenize, tagTimex, shrink(TIMEX2)
WriteSGML.type       = TIMEX2
"""

def timetest_file():
  print "TEST MODE\n---------"

  f = sys.argv[2]
  fin = open(f, "r")
  fout = open(f+".out", "w")
  fjet = open(f+".txt", "w")
  fjet.write("<DOC>\n<TEXT>\n")

  for line in fin.readlines():
    fjet.write(line)
    d = line.strip("\n").strip(".")
    d = reminder.parseDate(reminder.preprocess(d))
    fout.write("%s\n"%d)
  print "WROTE TO "+f+".out"
  fin.close()
  fout.close()

  fjet.write("</TEXT>\n</DOC>")
  fjet.close()
  print "MADE JET TEST: "+f+".txt"

  prop = jet_prop1+f+".txt"+jet_prop2+"%s\n"%date.today()+jet_prop3
  jet_p = open("reminder_time_test.jet", "w")
  jet_p.write(prop)
  jet_p.close()
  print "MADE JET PROPERTY FILE: "+"reminder_time_test.jet"  

  
handler = [realtime, timetest, timetest_file]
handler[int(sys.argv[1])]()
