import gitlab
def get_member():
    gl = gitlab.Gitlab('https://gitlab.net/', private_token='')
    projectsList = gl.projects.all()
    for project in projectsList:
        print project.id,project.name_with_namespace
    print "THESE ARE AVALABLE REPOS"
    print "ENTER REPO ID"
    repo_id=input()
    for project in projectsList:
        if project.id==repo_id:
            member=project.members.list()
            for mem in member:
                if mem.access_level==10:
                    print mem.name,'Guest'
                if mem.access_level == 20:
                    print mem.name, 'Reporter'
                if mem.access_level == 30:
                    print mem.name, 'Developer'
                if mem.access_level == 40:
                    print mem.name, 'Master'
                if mem.access_level == 50:
                    print mem.name, 'Owner'
if __name__ == "__main__":
    get_member()
