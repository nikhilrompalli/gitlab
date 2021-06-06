import gitlab
import pycurl,StringIO,urllib,commands,json
git_server="gitlab.net"
access_token = ''
protect_branches_url = "https://%s/api/v4/projects/%s/protected_branches/"
get_all_projects_url="https://%s/api/v4/projects/"
gl = gitlab.Gitlab('https://' + git_server + "/" , private_token= access_token)
projectsList = gl.projects.all()

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
        headers.append("Connection: keep-alive")
        headers.append("Keep-Alive: 300")
        strio = StringIO.StringIO()
        c.setopt(c.URL, url)
        # c.setopt(pycurl.POST, 1)
        c.setopt(pycurl.VERBOSE, 0)
        c.setopt(pycurl.SSL_VERIFYPEER, True)
        c.setopt(pycurl.SSL_VERIFYHOST, True)
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

        c.perform()
        content = strio.getvalue()
        code = c.getinfo(pycurl.HTTP_CODE)
        return 0, "Successfully got response", [code, content]
    except Exception, emsg:
        return 1, str(emsg), [None, None]


def GetProjectIdByname(projectName):
    for project in projectsList:
        if project.name_with_namespace == projectName:
            return project.id
def ProjectListA():
    print "Fetching......"
    for project in projectsList:
        projectName=project.name_with_namespace
        projectId=GetProjectIdByname(projectName)
        print(projectName)
        print(projectId)
        # print(project.id)

def ProjectList():
    print "Fetching......"
    headers = ["Content-Type: application/json", "Accept: application/json","PRIVATE-TOKEN: " + access_token]
    url = get_all_projects_url % (git_server)
    retVal, errMsg, response = postData(url, None, headers)
    # if retVal != 0:
    #     raise Exception(errMsg + ", URL - " + url)
    # if response[0] == 407:
    #     raise AuthenticationError("Authentication error. HTTP response code %s, URL - %s" % (str(response[0]), url))
    if response[0] != 200:
        raise Exception("HTTP response code %s, URL - %s" % (str(response[0]), url))
    try:
        json_response = json.loads(str(response[1]))
        if len(json_response) == 0:
            return 0
        return json_response
    except Exception, emsg:
        raise Exception(str(emsg))
        # print(project.id)

def getAllBranchesOfProject(projectId):
    print "Fetching Branches...."
    gl = gitlab.Gitlab('https://gitlab.net/', private_token='')
    project = gl.projects.get(projectId)
    # print project
    for branch in project.branches.list():
        print branch.name

def getparticularBranchByName(projectId,branchName):
    gl = gitlab.Gitlab('https://gitlab.net/', private_token='')
    project = gl.projects.get(projectId)
    # print project
    branch = project.branches.get(branchName)
    print branch

def projectUsers(projectId):
    gl = gitlab.Gitlab('https://gitlab.net/', private_token='')
    project = gl.projects.get(projectId)
    print project.users

def allBranchesList():
    gl = gitlab.Gitlab('https://gitlab.net/', private_token='')
    projectsList = gl.projects.all()
    # print((projectsList))

    for project in projectsList:
        b= project.branches.list()
        print(b)
def protectBranch(projectId,branchName):
    url = protect_branches_url % (git_server, str(projectId))
    cmd="curl --request POST --header \"PRIVATE-TOKEN: %s\" \"%s?name=%s&push_access_level=0&merge_access_level=0\"" %(str(access_token),url,str(branchName))
    result = executeCommand(cmd, [], True)
    print cmd
    # url = protect_branches_url % (git_server, str(projectId))
    # headers = ["PRIVATE-TOKEN" + access_token]
    # data='name=%s&push_access_level=0&merge_access_level=0'
    # data = urllib.urlencode({
    #     "name": branchName,
    #     "push_access_level":0,
    #     "merge_access_level" : 0
    # })
    # retVal, errMsg, response = postData(url, data, headers)
    # if retVal != 0:
    #     raise Exception(errMsg + ", URL - " + url)
    # if response[0] != 200:
    #     raise Exception("HTTP response code %s, URL - %s" % (str(response[0]), url))


    # project = gl.projects.get(projectId)
    # branch = project.branches.get(branchName)
    # branch.protect(masters_can_push=False, masters_can_merge=False)
    if result[0]==0:
        print "specified Branch has been protected"

if __name__ == "__main__":
    print("1.All Projects")
    # ProjectListA()
    ProjectList()
    # print("Select Project")
    # projectName=raw_input()
    # projectId= GetProjectIdByname(projectName)
    # # print projectId
    # getAllBranchesOfProject(projectId)
    # print("Enter branch name to protect:")
    # branchName=raw_input()
    #
    #
    # # allBranchesList()
    # # print("enter branchName")
    # # branchName=raw_input()
    # # getparticularBranchByName(projectId, branchName)
    # # protectBranch(projectId,branchName)
