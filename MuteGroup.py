#! /usr/bin/env python
# -*- coding: utf-8 -*-
import requests

qqurl = 'http://127.0.0.1:7890/muteAll'
qqdata = {
    "sessionKey":"",
    "target":614391357,
}
qqreq = requests.post(qqurl,json=qqdata)
