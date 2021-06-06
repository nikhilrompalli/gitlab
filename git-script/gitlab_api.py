import pycurl,StringIO,urllib,commands,json

git_server="gitlab.net"
access_token = ''
protect_branches_url = "https://%s/api/v4/projects/%s/protected_branches/"
get_all_projects_url="https://%s/api/v4/projects?private_token=%s"
branches_project_url="https://%s/api/v4/projects/%s/repository/branches?private_token=%s"

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

def postData(url, data=None, headers=None):
    if not url:
        return 1, "URL has not been given", [None, None]
    try:
        c = None
        c = pycurl.Curl()
        strio = StringIO.StringIO()
        c.setopt(c.URL, url)
        # c.setopt(pycurl.POST, 1)
        c.setopt(pycurl.VERBOSE, 0)
        c.setopt(pycurl.SSL_VERIFYPEER, False)
        c.setopt(pycurl.SSL_VERIFYHOST, False)
        c.setopt(c.WRITEFUNCTION, strio.write)
        c.setopt(pycurl.FOLLOWLOCATION, 1)
        c.setopt(pycurl.MAXREDIRS, 5)
        c.setopt(pycurl.TIMEOUT, 90)
        c.setopt(pycurl.CONNECTTIMEOUT, 60)

        if headers:
            c.setopt(pycurl.HTTPHEADER, headers)
        if data:
            c.setopt(pycurl.POSTFIELDS, str(data))
            c.setopt(pycurl.POST, 1)
        else:
            c.setopt(pycurl.HTTPGET, 1)
        c.perform()
        content = strio.getvalue()
        code = c.getinfo(pycurl.HTTP_CODE)
        return 0, "Successfully got response", [code, content]
    except Exception, emsg:
        return 1, str(emsg), [None, None]



def ProjectList():
    print "Fetching......"
    url = get_all_projects_url % (git_server,access_token)
    headers = ["Content-Type: application/json", "Accept: application/json","private_token" + access_token]
    retVal, errMsg, response = postData(url, None, headers)
    projects = json.loads(str(response[1]))
    for project in projects:
        print str(project["id"])+"-"+str(project["name"])

def get_all_branches(project_id):
    print "Fetching......"
    url = branches_project_url % (git_server,project_id, access_token)
    headers = ["Content-Type: application/json", "Accept: application/json", "private_token" + access_token]
    retVal, errMsg, response = postData(url, None, headers)
    branches = json.loads(str(response[1]))
    for branch in branches:
        print branch['name']



if __name__ == "__main__":
    print("All Projects")
    ProjectList()
    print "Enter Project Id :"
    project_id=int(input())
    get_all_branches(project_id)
