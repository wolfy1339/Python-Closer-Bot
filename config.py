"""Config file for the BMN Python Thread Closer Bot"""
import json
with open("config.json") as config_file:
    config = json.load(config_file)
# Configuration variables
server = config["network"]["server"]
port = config["network"]["port"]
channels = ",".join(config["channels"])
errorchannel = config["errorchannel"]
botNick = config["user"]["nick"]
botIdent = config["user"]["ident"]
botRealname = config["user"]["realname"]
botAccount = config["user"]["username"]
botPassword = config["user"]["password"]
NickServ = True
ownerHostmasks = config["owner"]["hostmask"]
adminHostmasks = config["admin"]["hostmask"]
commandChar = config["prefix"]
encoding = config["encoding"]
disabledPlugins = []

tpt = config["tpt"]

# A string containing python code that is run whenever an error happens
errorCode = """with socket.socket() as sock:
    sock.connect(("termbin.com", 9999))
    sock.send(traceback.format_exc().encode("utf-8", "replace"))
    SendMessage(errorchannel, "Error: " + sock.recv(1024).decode("utf-8"))"""