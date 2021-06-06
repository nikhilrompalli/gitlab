from optparse import OptionParser
import sys
from datetime import datetime
import commands

gitlab_url = "https://gitlab.net"
private_token = ""


try:

    parser = OptionParser(description="Gitlab Tagging.")

    parser.add_option("-p", "--Project_name", dest="project_name",help="specify the project name")
    parser.add_option("-b", "--Project_branch", dest="project_branch",help="specify the project branch")
    (options, args) = parser.parse_args()

    project_name = options.project_name
    project_branch = options.project_branch


except Exception, e:
    print "Unexpected Exception [", e.__repr__(), "]"
    sys.exit(3)
    
if len(sys.argv) == 1:
   parser.print_help()
   sys.exit()

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

def construct_tag_api(project_id, project_branch):
    try:
        d = datetime.today().strftime('%Y%m%d')
        tag_name = project_branch + '-' + str(d)
        body = "%s/api/v4/projects/%s/repository/tags?tag_name=%s&ref=%s" % (gitlab_url, project_id, tag_name, project_branch)
        return body
    except Exception as err:
        print "construct_tag_api " + str(err)
        sys.exit(3)

def post_gitlab_tag(tag_body):
    try:
        cmd = 'curl --request POST --header "PRIVATE-TOKEN: %s" "%s"' % (private_token, tag_body)
        res = executeCommand(cmd, [], True)
        print res
    except Exception as err:
        print "post_gitlab_tag " + str(err)
        sys.exit(3)
        
project_id = get_project_id(project_name)
tag_body = construct_tag_api(project_id, project_branch)
post_gitlab_tag(tag_body)


