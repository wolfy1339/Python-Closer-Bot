from . import config
import zirc
import ssl


class Bot(zirc.Client):
    def __init__(self):
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

    def on_privmsg(bot, event, irc):
        irc.reply(event, "It works!")
        #Or alternatively:
        #irc.privmsg(event.target, "It works!")

Bot()
