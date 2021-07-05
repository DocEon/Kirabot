import irc.bot
import irc.strings
import re
from random import randrange
from dice import *
from logs import *

from irc.client import ip_numstr_to_quad, ip_quad_to_numstr


class TestBot(irc.bot.SingleServerIRCBot):

    def __init__(self, channel, nickname, server, port=6667, log_path = "/srv/especiallygreatliterature.com/kiralogs/"):
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
        self.channel = channel
        self.log_dictionary = load_logs(log_path)
        self.user_dictionary = load_user_dictionary()

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        c.join(self.channel)

    def on_privmsg(self, c, e):
        self.do_command(e, e.arguments[0])

    def on_pubmsg(self, c, e):
        full_arg = e.arguments[0]
        user = e.source.nick
        print(">> " + user + " : " + full_arg)
        a = e.arguments[0].split(":", 1)
        if len(a) > 1 and irc.strings.lower(a[0]) == irc.strings.lower(
            self.connection.get_nickname()
        ):
            self.do_command(e, a[1].strip())
        else:
            self.action_handler(c, user, full_arg)
        return

    def action_handler(self, c, user, full_arg):
        c = self.connection
        try:
            split_arg = full_arg.split(" ", 1)
            first_word = split_arg[0]
            if len(split_arg) > 1:
                rest_of_arg = split_arg[1]
        except ValueError:
            first_word = full_arg

        if first_word == "wz":
            output = "+o " + user
            c.send_raw("MODE "+"#mage" + " +o " + user)
        elif first_word.lower() == "kirasearch" and rest_of_arg:
            resultDictionary = log_search(rest_of_arg, self.log_dictionary)
            if " " in rest_of_arg:
                restOfText = rest_of_arg.replace(" ", "%20")
            if '"' in rest_of_arg:
                rest_of_arg = rest_of_arg.replace('"', "%20")
            print(resultDictionary["Metadata"][1])
            output = "You can find your " + str(resultDictionary["Metadata"][1]) + " results at http://" + "especiallygreatliterature.com" + "/kiralogs/results/" + rest_of_arg + ".html !"
            c.privmsg("#mage", output)
        else:
            dice_output = tryRollingDice(full_arg, user, user_dict=self.user_dictionary)
            if dice_output:
                c.privmsg("#mage", (dice_output))

    def do_command(self, e, cmd):
        nick = e.source.nick
        c = self.connection

        if cmd == "disconnect":
            self.disconnect()
        elif cmd == "die":
            self.die()
        elif cmd == "stats":
            for chname, chobj in self.channels.items():
                c.notice(nick, "--- Channel statistics ---")
                c.notice(nick, "Channel: " + chname)
                users = sorted(chobj.users())
                c.notice(nick, "Users: " + ", ".join(users))
                opers = sorted(chobj.opers())
                c.notice(nick, "Opers: " + ", ".join(opers))
                voiced = sorted(chobj.voiced())
                c.notice(nick, "Voiced: " + ", ".join(voiced))
        elif cmd == "dcc":
            dcc = self.dcc_listen()
            c.ctcp(
                "DCC",
                nick,
                "CHAT chat %s %d"
                % (ip_quad_to_numstr(dcc.localaddress), dcc.localport),
            )
        elif "roll" in cmd:
            c.notice(nick, "Rolling!")
        else:
            c.notice(nick, "Not understood: " + cmd)


def main():
    import sys

    if len(sys.argv) != 4:
        print("Usage: testbot <server[:port]> <channel> <nickname>")
        sys.exit(1)

    s = sys.argv[1].split(":", 1)
    server = s[0]
    if len(s) == 2:
        try:
            port = int(s[1])
        except ValueError:
            print("Error: Erroneous port.")
            sys.exit(1)
    else:
        port = 6667
    channel = sys.argv[2]
    nickname = sys.argv[3]

    bot = TestBot(channel, nickname, server, port)
    bot.start()


if __name__ == "__main__":
    main()