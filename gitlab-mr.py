from optparse import OptionParser
import sys
from datetime import datetime
import commands
import resource

import requests
import pycurl
import os, sys, time, base64, commands, json
import urllib
import smtplib, mimetypes
import base64
from StringIO import StringIO
from operator import index
import time,datetime
from datetime import date, timedelta
from __builtin__ import raw_input

from email import encoders
from email.message import Message
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

gitlab_url = "https://gitlab.net"
private_token = ""

try:

    parser = OptionParser(description="Gitlab Tagging.")

    parser.add_option("-p", "--Project_name", dest="project_name",help="specify the project name")
    parser.add_option("-m", "--Mr_iid", dest="mr_iid",help="Merge Request Iid")
    parser.add_option("-a", "--action", dest="action",help="Action need to perform")
    parser.add_option("-j", "--jenkins_url", dest="jenkins_url",help="Specify Jenkins URL")
    (options, args) = parser.parse_args()

    project_name = options.project_name
    mr_iid = options.mr_iid
    action = options.action
    jenkins_url = options.jenkins_url


except Exception, e:
    print "Unexpected Exception [", e.__repr__(), "]"
    sys.exit(3)
    
if len(sys.argv) == 1:
   parser.print_help()
   sys.exit()

def httpRequest(url, header=[], data={}, delete=False):
    
    """ This httpRequest method is used to call both HTTPPOST and HTTPGET methods. 
    It will gets Access Token info by posting Client_secret, client_id, grant_type info to OpsRamp cloud. 
    """
    
    try:
        headers = ['Accept: application/json']
        headers.extend(header)
        strio = StringIO()
        try:
            c = pycurl.Curl()
            c.setopt(pycurl.URL, url)
            c.setopt(pycurl.HTTPHEADER, headers)
            c.setopt(pycurl.VERBOSE, 0)
            c.setopt(pycurl.NOSIGNAL, 1)
            c.setopt(pycurl.TIMEOUT, 500)
            c.setopt(pycurl.CONNECTTIMEOUT, 500)
            c.setopt(pycurl.SSL_VERIFYPEER, False)
            c.setopt(pycurl.SSL_VERIFYHOST, False)
            c.setopt(pycurl.FOLLOWLOCATION, 1)
            c.setopt(pycurl.MAXREDIRS, 5)
            c.setopt(pycurl.WRITEFUNCTION, strio.write)
            if delete:
                c.setopt(pycurl.VERBOSE, 0)
                c.setopt(pycurl.POSTFIELDS, data)
                c.setopt(pycurl.CUSTOMREQUEST, "DELETE")
            elif data:
                c.setopt(pycurl.POST, 1)
                c.setopt(pycurl.POSTFIELDS, data)
            else:
                c.setopt(pycurl.HTTPGET, 1)
            
            c.perform()
            
        except Exception, ex:
            raise Exception(str(ex))
        
        content = strio.getvalue()
        response = int(c.getinfo(pycurl.HTTP_CODE))
        if response != 200:
            if response != 404:
                raise Exception('\t\tpostData - Response code ' + str(response) + ' ' + content)
            else:
                raise Exception('\t\tpostData: HTTP_404 - ' + content)
        strio.flush()
        strio.close()
        c.close()
        return content
    except Exception, msg:
        raise Exception("\t\tException in httpRequest - " + str(msg))

def sendMail(subject, htmldata,toArr,toCc):
    try:
        hostname = "no-reply@gmail.com"
        fromAddr = hostname
        mailRelayHost = "localhost"
        fromAddr = hostname
        COMMASPACE = ', '
        toBcc = []
        htmlBody = MIMEText(htmldata, "html", "utf-8")
        mainMsg = MIMEMultipart()
        mainMsg['Subject'] = subject
        mainMsg['From'] = fromAddr
        mainMsg['To'] = toArr
        mainMsg['Cc'] = toCc
        mainMsg['X-Priority'] = '1'
        mainMsg['X-MSMail-Priority'] = 'High'
        mainMsg.attach(htmlBody)
        recipients = toArr 
        s = smtplib.SMTP(mailRelayHost)
        s.sendmail(fromAddr, recipients, mainMsg.as_string())
        print "mail send successfully"
        s.quit()
    except Exception as err:
        print "sendMail : " + str(err)
        
def executeCommand(cmd, args=[], ignoreOnError=False):
    for arg in args:
        cmd = cmd + ' ' + str(arg)
    try:
        result = commands.getstatusoutput(cmd)
    except Exception as errmsg:
        return 1, 'Exception caught - ' + str(errmsg)
    
    if result[0] != 0 and ignoreOnError == False:
        raise Exception("Failed to execute command: " + cmd)
    return result[0] >> 8 , result[1]

def get_project_id(project_name):
    try:
        if project_name == 'user': return 1
        elif project_name == 'core': return 2
        elif project_name == 'feeds': return 3
        elif project_name == 'reviews': return 4
        elif project_name == 'analysts ': return 5
        elif project_name == 'remort-dp': return 6
        elif project_name == 'portfolio': return 7
        elif project_name == 'collabration': return 8
    except Exception as err:
        print "get_project_id " + str(err)
        sys.exit(3)

def get_gitlab_api(resource_api):
    try:
        headers = ["Content-Type: application/json", "Accept: application/json", "PRIVATE-TOKEN: " + private_token]
        response  = httpRequest(resource_api, headers)
        return response
    except Exception as err:
        print "get_gitlab_api " + str(err)

def mr_get_api(project_id, mr_iid):
    try:
        mr_api = "%s/api/v4/projects/%s/merge_requests/%s" % (gitlab_url, project_id, mr_iid)
        response = get_gitlab_api(mr_api)
        res = json.loads(response)
        author_id = res["author"]["id"]
        assignee_id = res["assignee"]["id"]
        title = res["title"]
        web_url = res["web_url"]
        return author_id, assignee_id, title, web_url
    except Exception as err:
        print "mr_get_api " + str(err)
      
def user_details_api(user_id):
    try:
        user_api = "%s/api/v4/users/%s" % (gitlab_url, user_id)
        response = get_gitlab_api(user_api)
        res = json.loads(response)
        user_name = res["username"]
        user_email = res["email"]
        return user_name, user_email
    except Exception as err:
        print "user_details_api " + str(err)
        sys.exit(3)

def notify_users(author_email, assignee_email, title, web_url, project_name, jenkins_url):
    try:
        subject = project_name +  " - Merge Request"
        htmldata = """
                    <p><center><h3>New Merge Request</h3></center></p>
                    <p><b>Repo</b> : """ + project_name + """</p>
                    <p><b>Title</b> : """ + title + """</p>
                    <p><b>URL<b> : """ + web_url + """</p>
                    <div><label>&nbsp;&nbsp;&nbsp;</label></div>
                    <div><label>&nbsp;&nbsp;&nbsp;</label></div>
                    <div><label>&nbsp;&nbsp;&nbsp;</label></div>
                    <p>Jenkins Merge Pipeline is been triggered</p>
                    <p>Jenkins URL : """ + jenkins_url + """</p>
                    """
        sendMail(subject , htmldata, author_email, assignee_email)
    except Exception as err:
        print "notify_users " + str(err)
        sys.exit(3)

def notify_users_build_status(author_email, assignee_email, title, web_url, project_name, status):
    try:
        subject = project_name +  " - Merge Request"
        htmldata = """
                    <p><center><h3>Merge Request</h3></center></p>
                    <p><b>Repo</b> : """ + project_name + """</p>
                    <p><b>Title</b> : """ + title + """</p>
                    <p><b>URL<b> : """ + web_url + """</p>
                    <div><label>&nbsp;&nbsp;&nbsp;</label></div>
                    <div><label>&nbsp;&nbsp;&nbsp;</label></div>
                    <div><label>&nbsp;&nbsp;&nbsp;</label></div>
                    <p><b>Jenkins Build Status : """ + status + """<b></p>
                    """
        sendMail(subject , htmldata, author_email, assignee_email)
    except Exception as err:
        print "notify_users_build_status " + str(err)
        sys.exit(3)


project_id = get_project_id(project_name)
author_id, assignee_id, title, web_url = mr_get_api(project_id, mr_iid)
print author_id, assignee_id, title, web_url
author_name, author_email = user_details_api(author_id)
print author_name, author_email
assignee_name, assignee_email = user_details_api(assignee_id)
print assignee_name, assignee_email
if action == 'started':
    notify_users(author_email, assignee_email, title, web_url, project_name, jenkins_url)
else:
    notify_users_build_status(author_email, assignee_email, title, web_url, project_name, action)





