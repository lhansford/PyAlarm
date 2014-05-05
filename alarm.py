#!/bin/usr/python

"""Usage:
	alarm set (<time> | --sunrise [--city=<city>] ) [--playlist=<playlist>]
	alarm (-h | --help | --version)
"""
from docopt import docopt

from datetime import datetime, timedelta
from time import sleep

from astral import Astral
from apscheduler.scheduler import Scheduler
from mpd import MPDClient

#City name for sunrise calculations
CITY = 'Brisbane'

#Add IP address & port for MPD
IP_ADDRESS = "192.168.1.10"
PORT = 6600

#MPD Playlist to be played
PLAYLIST = "alarm"

has_alarm = False

def get_next_sunrise(cityname=None):
	if not cityname:
		cityname = CITY
	astral = Astral()
	city = astral[cityname]
	sun = city.sun(local=True)
	sunrise = sun['sunrise']
	return sunrise.replace(tzinfo=None) + timedelta(days=1)

def alarm(playlist):
	mpd_client.clear()
	mpd_client.load(playlist)
	mpd_client.shuffle()
	mpd_client.play()
	set_volume(0)

def set_volume(level):
	mpd_client.setvol(level)
	if level < 100:
		sched.add_date_job(
			set_volume, datetime.now() + timedelta(seconds = 2), [level+1])
	else:
		has_alarm = False

def is_valid_time(time):
	"""Checks a string to see if it can be converted to HH:MM"""
	#TODO
	if len(time) < 3 or len(time) > 4 or not time.isdigit():
		return False
	return True

def convert_time(time):
	""" Converts string of format HHMM to datetime object. """
	t = datetime.now()
	minute = int(time[-2:])
	hour = int(time[:-2])
	if t.hour == hour and t.minute < minute:
		t = t.replace(minute=minute)
	elif t.hour < hour:
		t = t.replace(hour=hour)
	else:
		day = t.day+1
		t = t.replace(day=day, hour=hour, minute=minute)
	return t

def set_alarm(time, playlist=None):
	if not playlist:
		playlist = PLAYLIST
	print("Setting alarm for " + str(time))
	sched.add_date_job(alarm, time, [playlist])
	has_alarm = True
	sched.start()
	while has_alarm:
	    sleep(100)
	sched.shutdown()

if __name__ == '__main__':
	args = docopt(__doc__, version='Alarm 0.1')
	if args['set']:
		sched = Scheduler()
		mpd_client = MPDClient(use_unicode=True)
		mpd_client.timeout = 10
		mpd_client.connect(IP_ADDRESS, PORT)
		if args['<time>']:
			if not is_valid_time(args['<time>']):
				print "Not a valid time. Use the format HHMM"
			else:
				time = convert_time(args['<time>'])
				set_alarm(time, playlist=args['--playlist'])
    	elif args['--sunrise']:
    		time = get_next_sunrise(city=args['--city'])
    		set_alarm(time, playlist=args['--playlist'])

