#!/usr/bin/python2.4
#coding: utf-8

# 
# author: Marian Babik
"""
This script generates diff report comparing content of two POEM APIs.

"""
import simplejson
import urllib2
import sys
import datetime
import StringIO
import urlparse
import smtplib

from optparse import OptionParser
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

VERSION="0.1"

METRIC_MAP = ( ('emi.cream.CREAMCE-DirectJobSubmit', 'org.sam.CREAMCE-DirectJobSubmit'),
               ('emi.cream.CREAMCE-JobSubmit','org.sam.CREAMCE-JobSubmit'),
               ('emi.wn.WN-Bi','org.sam.WN-Bi'),
               ('emi.wn.WN-Csh','org.sam.WN-Csh'),
               ('emi.wn.WN-SoftVer','org.sam.WN-SoftVer'),
               ('emi.wms.WMS-JobSubmit','org.sam.WMS-JobSubmit'),
               ('emi.cream.glexec.CREAMCE-JobSubmit', 'org.sam.glexec.CE-JobSubmit'),
               ('emi.cream.glexec.WN-gLExec','org.sam.glexec.WN-gLExec'),
               ('emi.ce.CREAMCE-JobSubmit','org.sam.CE-JobSubmit'),
               ('org.nordugrid.ARC-CE-ARIS','org.arc.ARC-STATUS'),
               ('org.nordugrid.ARC-CE-IGTF','org.arc.CA-VERSION'),
               ('org.nordugrid.ARC-CE-sw-csh','org.arc.csh'),
               ('org.nordugrid.ARC-CE-sw-gcc','org.arc.gcc'),
               ('org.nordugrid.ARC-CE-sw-perl','org.arc.perl'),
               ('org.nordugrid.ARC-CE-sw-python','org.arc.python'),
               ('org.nordugrid.ARC-CE-result','org.arc.Jobsubmit'),
               ('org.nordugrid.ARC-CE-lfc','org.arc.LFC'),
               ('org.nordugrid.ARC-CE-srm','org.arc.SRM') )

METRIC_MAP_DICT = dict([ (i[1], i[0]) for i in METRIC_MAP]) #inverse map
IS_DIFF_REPORTED = False

def get_json(uri):
    req = urllib2.urlopen(uri)
    return req.read()

def get_mis(profile):
    mis = [(i['metric']['name'], i['atp_vo']['voname'], i['atp_service_type_flavour']['flavourname']) 
                    for i in profile['metricinstances'] ]
    # apply filter (old to new)
    def metric_filter(mis_entry):
        if mis_entry[0] in METRIC_MAP_DICT.keys():
            return (METRIC_MAP_DICT[mis_entry[0]], mis_entry[1], mis_entry[2])
        return mis_entry                                          
    return [ metric_filter(i) for i in mis ]

def get_matching_profile(profile, profiles):
    profile_index = [ i['name'] for i in profiles ]
    if profile['name'] in profile_index:
        return profiles[profile_index.index(profile['name'])]
    else:
        return None

def generate_report(uri1, pr, uri2, pre):
    global IS_DIFF_REPORTED
    
    uri1_host = urlparse.urlparse(uri1)[1]
    uri2_host = urlparse.urlparse(uri2)[1]
        
    report = StringIO.StringIO()
    report.write("======== POEM diff report for %s =======\n\n" % datetime.datetime.now() )
    report.write("Comparing the following feeds: \n")
    report.write("- %s (%d profiles) \n" % (uri1, len(pr)) )
    report.write("- %s (%d profiles) \n\n" % (uri2, len(pre)) )
    
    for profile in pr:
        profile2 = get_matching_profile(profile, pre)
        if not profile2:
            report.write("Profile %s only exists on " % (profile['name'], uri1_host) )
            continue
        report.write("Profile: %s \n" % (profile['name']) )

        diff12 = set(get_mis(profile)) - set(get_mis(profile2))
        diff21 = set(get_mis(profile2)) - set(get_mis(profile))
        if diff21 or diff12:
            IS_DIFF_REPORTED = True

        report.write("%d metric instances missing in %s:\n" % (len(diff21), uri1_host) )
        for mi in sorted(diff21):
                report.write("- %s %s %s \n" % (mi[2], mi[0], mi[1]) )
                
        report.write("%d metric instances missing in %s:\n" % (len(diff12), uri2_host) )
        for mi in sorted(diff12):
                report.write("- %s %s %s \n" % (mi[2], mi[0], mi[1]) )
        report.write("\n")
    return report
    
def sent_report(report, email):
    now = datetime.datetime.now()        
    from_addr = 'POEM diff script <sam-support@cern.ch>'
    to_addr = email
    subject = 'Diff results for %s' % (now.strftime("%Y-%m-%d %H:%M"))
    
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = from_addr
    msg['To'] = to_addr
    
    part = MIMEText(report.getvalue())
    msg.attach(part)
    
    server = smtplib.SMTP('localhost')
    return server.sendmail(from_addr, to_addr, msg.as_string())


if __name__ == "__main__":
    parser = OptionParser(version="poem diff version "+VERSION,
                              usage="usage: %prog [options]")
    parser.add_option("--uri1", dest="uri1", type="string", 
                  help="URI referring to POEM profiles API")
    parser.add_option("--uri2", dest="uri2", type="string",
                  help="URI referring to POEM profiles API")
    parser.add_option("--email", dest="email", type="string",
                  help="Sent report to an email (otherwise print to stdout)")
    options, args = parser.parse_args(sys.argv)
    
    if not (options.uri1 or options.uri2):
        parser.error("Both URIs are need to compare.")
            
    try:
       pr = simplejson.loads(get_json(options.uri1))
       pre = simplejson.loads(get_json(options.uri2))
    except Exception, e:
       print e
       sys.exit(-1)
    
    report = generate_report(options.uri1, pr, options.uri2, pre)
       
    # only send reports if there are differences 
    if options.email and IS_DIFF_REPORTED:
        sent_report(report, options.email) 
    else:
        print report.getvalue()
        
    report.close()