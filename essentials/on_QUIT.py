def startup(addEssentialHook) :
    addEssentialHook("QUIT", main, 0)

def main(sonic, line, uid) :
    userinfo = sonic.infoByUID[uid]
    info = sonic.genInfo(line)
    if len(info["words"]) > 1 :
        message = sonic.coloncheck(" ".join(info["words"][1:]))
    else :
        message = ""
    sonic.distribute(uid, 'QUIT :"%s"' % (message), "all")
    sonic.connectionlost(userinfo["connection"], quithandled=True)
