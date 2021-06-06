import requests

git_url = "https://gitlab.net/"
private_token = ""

def get_users_data(iterate_value, type):
    for iter in range(iterate_value):
        active_user_url = git_url + "api/v4/users?"+ type +"=true&per_page=100&page="+ str(iter + 1) +"&private_token=" + private_token
        
        r = requests.get(active_user_url)
        active_user_data  = r.json()
        
        for user in active_user_data:
            print user['name'] + ' - ' + user['username'] + ' - ' + user['email'] +  ' - ' + str(user['two_factor_enabled'])
        

total = 300
iterate_value = total/100
if total%100 != 0:
    iterate_value += 1

print "Active Users: "
get_users_data(iterate_value, 'active')
print "\n\nBlocked Users: "
get_users_data(iterate_value, 'blocked')
