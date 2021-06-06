# import xlrd
from optparse import OptionParser
import urllib, StringIO, json, pycurl, sys,requests,curl



access_token = ''
c = None
debug = True


class AuthenticationError(Exception):
    pass


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


def getBranches():
    headers = ["Content-Type: application/json", "Accept: application/json",
               "Authorization: " + "Bearer " + access_token]
    url = "https://gitlab.net/"
    retVal, errMsg, response =  requests.get(url,headers)
    print response[0]
    print response

if __name__ == "__main__":
    getBranches()
