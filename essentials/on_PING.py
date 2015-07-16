def startup(addEssentialHook) :
    addEssentialHook("PING", main, 0)
def main(sonic, line, uid) :
    info = sonic.genInfo(line)
    userinfo = sonic.infoByUID[uid]
    if line.startswith("PING LAG") :
        sonic.msg_send(userinfo["connection"], "PONG %s :%s" % (sonic.network_hostname, info["words"][1]))
    else :
        sonic.msg_send(userinfo["connection"], "PONG " + info["words"][1])
