import config
import zirc
import ssl
import socket


class Bot(zirc.Client):
    def __init__(self):
        if config.irc.ipv6:
            self.connection = zirc.Socket(wrapper=ssl.wrap_socket, family=socket.AF_INET6)
        else:
            self.connection = zirc.Socket(wrapper=ssl.wrap_socket)
        self.connect(address=config.irc.server,
                     port=config.irc.port,
                     nickname=config.irc.botNick,
                     ident=config.irc.botIdent,
                     realname=config.irc.botRealname,
                     channels=config.irc.channels,
                     sasl_user=config.irc.botAccount,
                     sasl_pass=config.irc.botPassword)

        self.start()

    def on_all(irc, raw):
        print("--> {}".format(raw))

    def on_send(irc, data):
        if not config.irc.debug:
            if not (data.find("CAP") != -1 or data.find("AUTHENTICATE") != -1 or data.find("USER") != -1):
                print("--> {}".format(data))
        else:
            print("--> {}".format(data))

    def on_privmsg(bot, event, irc):
        if config.irc.prefix in event.arguments or config.irc.botNick in event.arguments:
            if event.arguments.find('quit') != -1:
                Commands(bot).quit(event, irc)
        #irc.reply(event, "It works!")
        # Or alternatively:
        # irc.privmsg(event.target, "It works!")
    
class Commands():
    def __init__(self, bot):
        self = bot
    def quit(bot, event, irc):
        if self.getPerms('admin', event):
            irc.quit(event.arguments.split('quit')[1])
    def getPerms(bot, level, event):
        if level == 'admin':
            if event.source.host in config.irc.adminHostmasks or event.source.host in config.irc.ownerHostmasks:
                return True
            else:
                return False


Bot()
