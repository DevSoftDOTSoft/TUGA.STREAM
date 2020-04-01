#!/usr/bin/python
# coding=utf-8

import sys,urlparse,urllib,re,urllib2,base64,os
import requests
# Local Packages
scripts_import = [os.getcwd() + '\\octopus']
for script in scripts_import:
    if not script in sys.path:
        sys.path.insert(0, script)




from octopus import Octopus
def octopus_create_GET_request(urls):
    data = []
    otto = Octopus(
           concurrency=4, auto_start=True, cache=True, expiration_in_seconds=10,request_timeout_in_seconds=8
    )
    def handle_url_response(url, response):
        if "Not found" == response.text:
            print ("URL Not Found: %s" % url)
        else:
            data.append(response.text)
    for url in urls:
        otto.enqueue(url, handle_url_response)
    otto.wait(25)
    return data



def urllib_GET(url,timeout):
    try:
        req = urllib2.Request(url)
        response = urllib2.urlopen(req,timeout=timeout)
        response.close()
        return response
    except:
        print("HTTP-ERROR")

def requests_GET(uri,timeout):
    try:
        return requests.get(url = uri, timeout=timeout, allow_redirects=True)
    except:
        print("HTTP-ERROR")