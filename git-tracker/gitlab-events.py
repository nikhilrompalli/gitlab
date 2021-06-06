from flask import Flask, request
import json,sys,re

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib


app = Flask(__name__)
configFilePath = "config.json"
config = ""


def sendMail(subject, htmldata,toArr):
    try:
        fromAddr = "no-reply@gmail.com"
        mailRelayHost = "localhost"
        COMMASPACE = ', '
        toCc = []
        toCc = []
        toBcc = [] 
        htmlBody = MIMEText(htmldata, "html", "utf-8")
        mainMsg = MIMEMultipart()
        mainMsg['Subject'] = subject
        mainMsg['From'] = fromAddr
        mainMsg['To'] = COMMASPACE.join(toArr)
        mainMsg['Cc'] = COMMASPACE.join(toCc)
        mainMsg['X-Priority'] = '1'
        mainMsg['X-MSMail-Priority'] = 'High'
        mainMsg.attach(htmlBody)
        recipients = toArr 
        recipients.extend(toCc)
        recipients.extend(toBcc)
        s = smtplib.SMTP(mailRelayHost)
        s.sendmail(fromAddr, recipients, mainMsg.as_string())
        s.quit()
    except Exception as err:
        print "Got exception to send mail." + str(err)

def processEvent(event):
    try:
        event_pid = event["project_id"]
        event_branch = event["ref"].split("/")[-1]

        if event["event_name"] != "push":
            print "Ignoring event as it is not push event."
            return
        
        print config["projects"]
        
        if str(event_pid) in config["projects"]:
            print "In config projects"
            print config
            config_branches  = config["projects"][str(event_pid)]["branches"].split(',')
            config_re        = config["projects"][str(event_pid)]["re-match"]
            config_mail_list = config["projects"][str(event_pid)]["mail-list"].split(',')
            config_subject   = config["projects"][str(event_pid)]["subject"].strip()

            if len(config_branches) == 0 or event_branch in config_branches:
                fromReqBranch = True
            else:
                fromReqBranch = False
                print "Ignoring event as we are not interested on this branch changes."
                return
            
            commits = event["commits"]
            commits_data = []

            for commit in commits:
                
                print commit

                data_ = {"id":"","files":[],"commit_url":"","author_name":"","author_email":"","message":""}

                data_["id"] = commit["id"]
                data_["message"] = commit["message"]
                data_["author_name"]  = commit["author"]["name"]
                data_["author_email"] = commit["author"]["email"]
                data_["commit_url"]   = commit["url"]

                for added in commit["added"]:
                    if re.match(config_re,added):
                        data_["files"].append(added)
                for removed in commit["removed"]:
                    if re.match(config_re,removed):
                        data_["files"].append(removed)
                for modified in commit["modified"]:
                    if re.match(config_re,modified):
                        data_["files"].append(modified)

                if len(data_["files"]) == 0:
                    print "Ignoring event as we are not interested with these files."
                    return
                
                commits_data.append(data_)

            html = """Hi Team, Files which need attention got pushed to git. Please find details below.<br>"""
            html += "<table>"
            
            for data in commits_data:

                html += """<tr id="t6" style="height:30px;display:table-row;background:#e9e9e9;">
                        <td style='font-family:"Lucida Grande", "Lucida Sans Unicode", Helvetica, Arial, Tahoma, sans-serif;font-size:10pt;'><b>Commit URL</b></td>
                        <td style='font-family:"Lucida Grande", "Lucida Sans Unicode", Helvetica, Arial, Tahoma, sans-serif;font-size:10pt;'><a href='"""+data["commit_url"]+"""'>Click Here</a></td>
                    </tr>
                    <tr id="t6" style="height:30px;display:table-row;background:#e9e9e9;">
                        <td style='font-family:"Lucida Grande", "Lucida Sans Unicode", Helvetica, Arial, Tahoma, sans-serif;font-size:10pt;'><b>Author Name</b></td>
                        <td style='font-family:"Lucida Grande", "Lucida Sans Unicode", Helvetica, Arial, Tahoma, sans-serif;font-size:10pt;'>"""+data["author_name"]+"""</td>
                    </tr>
                    <tr id="t6" style="height:30px;display:table-row;background:#e9e9e9;">
                        <td style='font-family:"Lucida Grande", "Lucida Sans Unicode", Helvetica, Arial, Tahoma, sans-serif;font-size:10pt;'><b>Author Email</b></td>
                        <td style='font-family:"Lucida Grande", "Lucida Sans Unicode", Helvetica, Arial, Tahoma, sans-serif;font-size:10pt;'>"""+data["author_email"]+"""</td>
                    </tr>
                    <tr id="t6" style="height:30px;display:table-row;background:#e9e9e9;">
                        <td style='font-family:"Lucida Grande", "Lucida Sans Unicode", Helvetica, Arial, Tahoma, sans-serif;font-size:10pt;'><b>Commit Message</b></td>
                        <td style='font-family:"Lucida Grande", "Lucida Sans Unicode", Helvetica, Arial, Tahoma, sans-serif;font-size:10pt;'>"""+data["message"]+"""</td>
                    </tr>
                    <tr id="t6" style="height:30px;display:table-row;background:#e9e9e9;">
                        <td style='font-family:"Lucida Grande", "Lucida Sans Unicode", Helvetica, Arial, Tahoma, sans-serif;font-size:10pt;'><b>Files</b></td>
                        <td style='font-family:"Lucida Grande", "Lucida Sans Unicode", Helvetica, Arial, Tahoma, sans-serif;font-size:10pt;'>"""+",".join(data["files"])+"""</td>
                    </tr>
                    
                    """

            html += "</table>"

            print html

            sendMail(config_subject,html,config_mail_list)
            
        else:
            return
    except Exception as err:
        print "Got exception: " + str(err)



@app.route('/',methods=['POST'])
def foo():
   event = json.loads(request.data)
   processEvent(event)
   return "OK"

if __name__ == '__main__':
    with open(configFilePath) as f:
       config = json.load(f)
    if config == "":
        print "Failed to read config file. Exiting...."
        sys.exit()  
    
    app.run(config["server"])