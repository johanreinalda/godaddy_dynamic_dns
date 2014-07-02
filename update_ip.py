#!/usr/bin/python
import sys, argparse, logging, pif, smtplib
from pygodaddy import GoDaddyClient
# Import the email modules we'll need
from email.mime.text import MIMEText

#this contain the config file
import godaddy

#email function
def email_update(body):
	global smtplib
	msg = MIMEText(body)
	msg['From'] = sender
	msg['To'] = to
	msg['Subject'] = 'IP address updater'
	s = smtplib.SMTP(smtpserver)
	s.sendmail(sender, to, msg.as_string())
	s.quit()

#command line arguments parsing
parser = argparse.ArgumentParser('A Python script to do updates to a GoDaddy DNS host A record')
parser.add_argument('-v', '--verbose', action='store_true', help="send emails on 'no ip update required'")
args = parser.parse_args()

#start log file
logging.basicConfig(filename=godaddy.logfile, format='%(asctime)s %(message)s', level=logging.INFO)

#what is my public ip?
public_ip = pif.get_public_ip()
logging.info("My ip: {0}".format(public_ip))

# login to GoDaddy DNS management
# docs at https://pygodaddy.readthedocs.org/en/latest/
client = GoDaddyClient()

if client.login(godaddy.gduser, godaddy.gdpass):
	# find out current dns record value. This can also be done with a quick nslookupA
	# with something like socket.gethostbyname()
	# however, this can include caching somewhere in the dns layers
	# We could also use dnspython libraray, but that adds a lot of complexity

	# use the GoDaddy object to find our current IP registered
	domaininfo = client.find_dns_records(godaddy.domain)
	for record in domaininfo:
		if record.hostname == godaddy.host:
			if record.value != public_ip:
				logging.info("Update required: old {0}, new {1}".format(record.value, public_ip))
				updateinfo = "old " + record.value + ", new " + public_ip
				# This will fail if you try to set the same IP as already registered!
				if client.update_dns_record(godaddy.host+"."+godaddy.domain, ip):
					logging.info('Update OK')
					email_update("Update OK!\n"+updateinfo)
				else:
					logging.info('Update DNS FAILED!')
					email_update("Update failed!\n"+updateinfo)

			else:
				logging.info('No update required.')
				if args.verbose:
					email_update('No update required.')

else:
	logging.error('CANNOT login to GoDaddy')
	email_update('ERROR: Cannot login to GoDaddy!')

