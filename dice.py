import re
from random import randrange

def match_dice(word):
    # returns tuple with number and sides of dice to roll, if the word is of the format 1d10.
    # if there's a + sign after the roll, it returns the number after the +; otherwise, the third number in the tuple
    # is 0.
    # otherwise returns (0,0,0)

    should_add = re.match(r'([0-9]+)d([0-9]+)\+([0-9]+)', word)
    m = re.match(r'([0-9]+)d([0-9]+)', word)
    if should_add:
        num = int(should_add.group(1))
        sides = int(should_add.group(2))
        adder = int(should_add.group(3))
        return num, sides, adder
    elif m:
        num = int(m.group(1))
        sides = int(m.group(2))
        return num, sides, 0
    else:
        return 0, 0, 0


def roll_dice(num, sides):
    rolls = []
    for i in range(num):
        rolls.append(randrange(sides) + 1)
    return rolls


def tryRollingDice(message, user, user_dict = None, init_list=None, sort=False):
    (num, sides, adder) = match_dice(message)
    # check for if addition is neccesary:
    if num > 0:
        dice = roll_dice(num, sides)
        # if userDatabase[user]["sort"] != "False"
        if user_dict:
            if user_dict[user]["sort"] == "True":
                dice.sort()
                # TODO: put back "SORTED"?
        if sort:
            dice.sort()
        words = message.split()
        roll = words[0]
        # (KEN: default diff doesn't seem to fit most use cases)
        # * diff = sides/2+1 # assume diff6 by default (for d10, diff11 for d20, etc.)
        explanation = ' '.join(words[1:]) + ' '  # the rest of the words, joined back by spaces
        success_string = ''

        # if "wp" in message:
        #   if user in userDictionary:
        #     if "WP" in userDictionary[user].keys():
        #       newWP = userDictionary[user]["WP"] - 1
        #       userDictionary = changeUserProperty(userDictionary, user, "WP", newWP)
        #       sendMsg(user + " spends 1WP, now has " + str(newWP) + "WP.")

        if len(words) > 1:
            for word in words:
                m = re.match(r'diff([0-9]+)', word)
                if m:
                    diff = int(m.group(1))
                    successes = get_successes(dice, diff)
                    success_string = successes_to_string(successes)
                    explanation = ' '.join(words[2:])

        if adder > 0:
            total = str(sum(dice) + adder)
            if init_list:
                if explanation.rstrip() == "":
                    init_tuple = (user, int(total), int(adder))
                else:
                    initTuple = (explanation, int(total), int(adder))
            init_list.append(initTuple)

            return user + ', ' + explanation + roll + ': ' + str(dice) + " = <" + total + "> " + success_string

        else:
            if explanation.rstrip() == "":
                return user + " = " + roll + ": " + str(dice) + " " + success_string
            else:
                return user + ', ' + explanation + "= " + roll + ': ' + str(dice) + " " + success_string


def get_successes(dice, diff):
    # A botch is going to return as an int with value -1
    successes = False
    numSuc = 0
    for die in dice:
        if die == 1:
            numSuc -= 1
        elif die >= diff:
            numSuc += 1
            successes = True
    if numSuc < 0 and successes == False:
        return -1
    elif numSuc <= 0:
        return 0
    else:
        return numSuc


def successes_to_string(numSuc):
    if numSuc == -1:
        return "(BOTCH)"
    elif numSuc == 0:
        return "(Fail)"
    elif numSuc == 1:
        return "(1 success)"
    else:
        return "(" + str(numSuc) + " successes)"


def initOutput(initList):
    initList.sort(key=itemgetter(2), reverse=True)
    initList.sort(key=itemgetter(1), reverse=True)
    initString = ""
    print
    initList
    for tuple in initList:
        initString = initString + tuple[0].rstrip() + ": " + str(tuple[1]) + "; "
    return initString
