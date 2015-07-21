def startup(addEssentialHook) :
    addEssentialHook("USER", main, 0)

def main(sonic, line, uid) :
    info = sonic.genInfo(line)
    userinfo = sonic.infoByUID[uid]
    ident = info["words"][1].replace("!", "").replace("@", "")
    realname = " ".join(info["words"][4:])[1:]
    longname = userinfo["nick"] + "!" + ident + "@" + userinfo["address"]
    sonic.infoByUID[uid]["longname"] = longname
    sonic.infoByUID[uid]["realname"] = realname
    sonic.infoByUID[uid]["ident"] = ident
    sonic.infoByUID[uid]["status"].append("user")
    if "nick" in userinfo["status"] :
        serve(sonic, uid)
def serve(sonic, uid) :
    userinfo = sonic.infoByUID[uid]
    sonic.msg_send(userinfo["connection"], "NOTICE Auth :*** Looking up your hostname...")
    sonic.msg_send(userinfo["connection"], "NOTICE Auth :*** Found your hostname (%s) -- cached" % (userinfo["address"]))
    sonic.msg_send(userinfo["connection"], "NOTICE Auth :Welcome to %s!" % (sonic.network_name))
    sonic.msg_send(userinfo["connection"], "001 %s :Welcome to %s, %s" % (userinfo["nick"], sonic.network_name, userinfo["longname"]))
    sonic.msg_send(userinfo["connection"], "002 %s :Your host is %s, running version sonicIRCd-2.0.0" % (userinfo["nick"], sonic.network_hostname))
    sonic.msg_send(userinfo["connection"], "003 %s :This server was created %s" % (userinfo["nick"], sonic.creationtime))
    sonic.msg_send(userinfo["connection"], "004 %s sonicIRCd-2.0.0  bohv" % (userinfo["nick"]))
    sonic.msg_send(userinfo["connection"], "005 %s CHANTYPES=# PREFIX=(ohv)@%%+ CHANMODES=b,o,h,v, NETWORK=%s CASEMAPPING=rfc1459" % (userinfo["nick"], sonic.network_name))
    sonic.msg_send(userinfo["connection"], "375 %s :%s message of the day" % (userinfo["nick"], sonic.network_hostname))
    for motdline in sonic.motd.split("\n") :
        sonic.msg_send(userinfo["connection"], "372 %s :- %s" % (userinfo["nick"], motdline.replace("\r", "")))
    sonic.msg_send(userinfo["connection"], "376 %s :End of message of the day." % (userinfo["nick"]))
    sonic.schedulePing(uid)
