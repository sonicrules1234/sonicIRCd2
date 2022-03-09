def startup(addEssentialHook) :
    addEssentialHook("PONG", main, 0)

def main(sonic, line, uid) :
    userinfo = sonic.infoByUID[uid]
    info = sonic.genInfo(line)
    if userinfo["pongwaiting"] :
        sonic.infoByUID[uid]["pongwaiting"] = False
        del sonic.timedevents[userinfo["pongtimestr"]]["WAITPONG" + uid]
        if sonic.timedevents[userinfo["pongtimestr"]] == {} :
            del sonic.timedevents[userinfo["pongtimestr"]]
        nexttime = sonic.count + 120
        nexttimestr = str(nexttime)
        if not sonic.timedevents.has_key(nexttimestr) :
            sonic.timedevents[nexttimestr] = {}
        sonic.timedevents[nexttimestr]["PINGAGAIN" + uid] = {"function":sonic.schedulePing, "args":(uid,)}
