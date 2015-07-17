import yaml, logging, imp, socket, ssl, thread, traceback, select, time, fnmatch, shelve, hashlib, random, os, sys, json, glob, os.path
global waitingfordata
waitingfordata = False
global sonicinst
configfileobj = open("config.yaml", "r")
configdict = yaml.load(configfileobj)
configfileobj.close()
motdfileobj = open("motd.txt", "r")
motddata = motdfileobj.read()
motdfileobj.close()
configdict["motd"] = motddata
certfile = configdict["certfile"][:]
keyfile = configdict["keyfile"][:]
del configdict["certfile"]
del configdict["keyfile"]
#sonicinst = sonicIRCd2()
configdict["debug"] = True
class sonicIRCd2() :
    def __init__(self, network_name, network_hostname, network_website, opers, motd, debug) :
        self.connectionlist = []
        self.creationtime = time.strftime("%x %X")
        self.infoByUID = {}
        self.nick2UID = {}
        self.uppernicks = []
        self.channelinfo = {}
        self.connection2UID = {}
        self.availableUIDs = []
        self.highestuid = "0"
        self.essentials = {}
        self.plugins = {}
        self.timedevents = {} 
        self.network_name = network_name
        self.network_hostname = network_hostname
        self.network_website = network_website
        self.opers = opers
        self.debug = debug
        self.motd = motd
        self.count = 0
        self.hookstartup()
        thread.start_new_thread(counter, (self,))
    def nextUID(self, uidType="number") :
        if uidType == "number" :
            if len(self.availableUIDs) > 0 :
                return self.availableUIDs.pop()
            else :
                self.highestuid = str(int(self.highestuid) + 1) 
                return self.highestuid
    def infoByNick(self, nick) :
        return self.infoByUID[self.nick2UID[nick]]
    def infoByConnection(self, connection) :
        return self.infoByUID[self.connection2UID[connection]]
    def onConnect(self, connection, address, encryption) :
        uid = self.nextUID()
        self.connectionlist.append(connection)
        self.infoByUID[uid] = {"oper":False, "operlevel":0, "uid":uid, "channels":{}, "status":["connected"], "connection":connection, "address":socket.gethostbyaddr(address[0])[0], "conaddress":address, "ip":address[0], "ssl":encryption, "buffer":"", "level":0}
        self.connection2UID[connection] = uid
    def connectionlost(self, connection) :
        userinfo = self.infoByConnection(connection)
        uid = userinfo["uid"][:]
        if "user" in userinfo["status"] :
            for channel in userinfo["channels"].keys() :
                #handling of quit messages should already be done
                self.channelinfo[channel]["users"].remove(uid)
            del self.nick2UID[userinfo["nick"]]
        del self.connection2UID[connection]
        del self.infoByUID[uid]
        self.connectionlist.remove(connection)
        if uid != self.highestuid :
            self.avaiableuids.append(uid)
        else :
            self.highestuid = str(int(self.highestuid) - 1)
        connection.close()
    def validnick(self, nick) :
        lowerchars = "abcdefghijklmnopqrstuvwxyz1234567890[]'`|-_"
        for letter in nick :
            if letter not in lowerchars + self.caseUpper(lowerchars) :
                return "INVALID"
        if self.caseUpper(nick) in self.uppernicks :
            return "TAKEN"
        return "VALID"
    def msg_send(self, connection, message) :
        self.consend(connection, ":%s %s\r\n" % (self.network_hostname, message))

    def msg2_send(self, connection, message, longname) :
        self.consend(connection, ":%s %s\r\n" % (longname, message))

    def consend(self, connection, message) :
        connection.send(message)
        if self.debug :
            print "[OUT %s] %s" % (self.infoByConnection(connection)["ip"], message)
    def parseData(self, connection, data) :
        userinfo = self.infoByConnection(connection)
        userbuffer = userinfo["buffer"]
        lines = data.replace("\r", "").split("\n")
        lines[0] = userbuffer + lines[0]
        self.infoByUID[userinfo["uid"]]["buffer"] = lines[-1]
        if lines[0].lower().startswith("post") :
            self.connectionlost(connection)
        for line in lines[:-1] :
            if line == "" :
                return
            if self.debug :
                print "[IN %s] %s" % (userinfo["ip"], line)
            info = self.genInfo(line)
            if self.essentials.has_key(info["words"][0].upper()) :
                for essential in self.essentials[info["words"][0].upper()] :
                    essential["function"](self, line, userinfo["uid"])
                
    def caseLower(self, strvar) :
        return strvar.lower().replace("{", "[").replace("}", "]").replace("|", "\\").replace("~", "^")

    def caseUpper(self, strvar) :
        return strvar.upper().replace("[", "{").replace("]", "}").replace("\\", "|").replace("^", "~")

    def genInfo(self, line) :
        info = {}
        info["raw"] = line
        info["words"] = line.split(" ")
        return info
    def distribute(self, uid, message, channel, selftoo=False, oldlongname=None) :
        sentto = []
        if channel == "all" :
            if oldlongname :
                longname = oldlongname
            else :
                longname = self.infoByUID[uid]["longname"]
            for chan in self.infoByUID[uid]["channels"].keys() :
                for useruid in self.channels[chan]["users"] :
                    if userid != uid and userid not in sentto :
                        self.msg2_send(self.infoByUID[userid]["connection"], message, longname)
                        sentto.append(userid)
            if selftoo :
                self.msg2_send(self.infoByUID[uid]["connection"], message, longname)
        else :
            for useruid in self.channels[chan]["users"] :
                if userid != uid and userid not in sentto :
                    self.msg2_send(self.infoByUID[userid]["connection"], message, self.infoByUID[uid]["longname"])
                    sentto.append(userid)
            if selftoo :
                self.msg2_send(self.infoByUID[uid]["connection"], message, self.infoByUID[uid]["longname"])
    def hookstartup(self) :
        del self.essentials
        del self.plugins
        self.essentials = {}
        self.plugins = {}
        for filepath in glob.glob("essentials" + os.sep + "*.pyc") :
            os.remove(filepath)
        for filepath in glob.glob("essentials" + os.sep + "*.py") :
            essential = imp.load_source(filepath.split(os.sep)[-1].replace(".py", ""), filepath)
            essential.startup(self.addEssentialsHook)
        for filepath in glob.glob("plugins" + os.sep + "*.py") :
            plugin = imp.load_source(filepath.split(os.sep)[-1].replace(".py", ""), filepath)
            plugin.startup(self.addPluginHook)
    def addEssentialsHook(self, name, function, minlevel) :
        if not self.essentials.has_key(name.upper) :
            self.essentials[name.upper()] = []
        self.essentials[name.upper()].append({"minlevel":minlevel, "function":function})
    def addPluginHook(self, name, function, minlevel) :
        docs = function.__doc__
        docs = docs.replace("\r", "")
        lines = docs.split("\n")
        helpstring = lines[0]
        detailedhelp = "\n".join(lines[1:])
        if not self.plugins.has_key(name.upper) :
            self.plugins[name.upper()] = []
        self.plugins[name.upper()].append({"minlevel":minlevel, "function":function, "syntax":helpstring, "detailedhelp":detailedhelp})
def waitfordata(sonicinstance) :
    while True :
        if len(sonicinstance.connectionlist) != 0 :
            noerror = False
            tempconlist = sonicinstance.connectionlist[:]
            try :
                connections = select.select(tempconlist, [], [], 5)
                noerror = True
            except :
                for userconnection in tempconlist :
                    try :
                        connections = select.select([userconnection], [], [], 0)
                    except :
                        try :
                            sonicinstance.connectionlost(connection)
                        except :
                            traceback.print_exc()
            if noerror :
                for connection in connections[0] :
                    try :
                        data = connection.recv(4096)
                    except :
                        data = ""
                    if data != "" :
                        try :
                            sonicinstance.parseData(connection, data)
                        except :
                            traceback.print_exc()
                    else :
                        print "No data, closing the connection"
                        try :
                            sonicinstance.connectionlost(connection)
                        except :
                            traceback.print_exc()
                    del tempconlist
        else :
            try :
                time.sleep(3)
            except KeyboardInterrupt as i:
                logging.exception("wat")
                raise i
def regserv() :
    global waitingfordata
    global sonicinst
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('', 6667))
    s.listen(1)



    while True :
        try :        
            conn, addr = s.accept()
            if addr[0] not in [] :
                sonicinst.onConnect(conn, addr, False)
                if not waitingfordata :
                    waitingfordata = True
                    thread.start_new_thread(waitfordata, (sonicinst,))
            else : conn.close()
        except :
            traceback.print_exc()
            break
    s.close()



def sslserv(certfile, keyfile) :
    global waitingfordata
    global sonicinst
    try :
        
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        #if world.pythonversion == "2.5" :
        #    contextobject = OpenSSL.SSL.Context(OpenSSL.SSL.SSLv3_METHOD)
        #    contextobject.use_certificate_file(conf.certfile)
        #    contextobject.use_privatekey_file(conf.keyfile)
        #    s = OpenSSL.SSL.Connection(contextobject, s)
        s = ssl.wrap_socket(s, certfile=certfile, keyfile=keyfile)
        s.bind(('', 6697))
        s.listen(1)
    except: traceback.print_exc()


    while True :
        try :        
            conn, addr = s.accept()
            if addr[0] not in [] :
                sonicinst.onConnect(conn, addr, True)
                if not waitingfordata :
                    waitingfordata = True
                    thread.start_new_thread(waitfordata, (sonicinst,))
            else : conn.close()
        except :
            traceback.print_exc()
            break

    s.close()
def counter(sonicinstance) :
    while True :
        if sonicinstance.timedevents.has_key(str(sonicinstance.count)) :
            actions = sonicinstance[str(sonicinstance.count)]
            for action in actions.keys() :
                thread.start_new_thread(action["function"], action["args"])
        time.sleep(1)
        sonicinstance.count += 1
sonicinst = sonicIRCd2(**configdict)
if os.path.exists(certfile) and os.path.exists(keyfile) :
    thread.start_new_thread(sslserv, (certfile, keyfile))
regserv()
