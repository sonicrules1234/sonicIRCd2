def startup(addEssentialHook) :
    addEssentialHook("NICK", main, 0)
def main(sonic, line, uid) :
    info = sonic.genInfo(line)
    userinfo = sonic.infoByUID[uid]
    if info["words"][1].startswith(":") :
        desirednick = info["words"][1][1:]
    else :
        desirednick = info["words"][1]
    result = sonic.validnick(desirednick)
    if result == "INVALID" :
        sonic.msg_send(userinfo["connection"], "432 %s :Erroneous nickname" % (desirednick))
    elif result == "TAKEN" :
        sonic.msg_send(userinfo["connection"], "433 %s :Nick already in use" % (desirednick))
    else :
        if userinfo.has_key("nick") and "user" in userinfo["status"] :
            #changing nick
            sonic.uppernicks.remove(sonic.caseUpper(userinfo["nick"]))
            oldlongname = userinfo["nick"] + "!" + userinfo["ident"] + "@" + userinfo["address"]
            sonic.infoByUID[uid]["longname"] = desirednick + "!" + userinfo["ident"] + "@" + userinfo["address"]
            sonic.infoByUID[uid]["nick"] = desirednick
            sonic.uppernicks.append(sonic.caseUpper(desirednick))
            sonic.distribute(uid, "NICK :" + desirednick, "all", True, oldlongname)
        else :
            sonic.infoByUID[uid]["status"].append("nick")
            sonic.infoByUID[uid]["nick"] = desirednick
            sonic.uppernicks.append(sonic.caseUpper(desirednick))
            sonic.nick2UID[desirednick] = uid
    
