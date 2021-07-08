import os
import re
import json
from random import randrange

result_dir = "/Users/kenalba/Documents/GitHub/Kirabot"


def load_user_dictionary():
  f = open('JSONUsers.txt', 'r')
  userDictionary = json.load(f)
  f.close()
  return userDictionary

def load_quotes():
    quoteDatabase = {}
    f = open("quotes.txt", 'r')
    for line in f:
        if line.strip() == "":
            if quoteDatabase[len(quoteDatabase) - 1] != "":
                quoteDatabase.append("")
        else:
            quoteDatabase[len(quoteDatabase) - 1] += "\n" + line

    return quoteDatabase


def load_logs(log_dir):
    log_dict = {}
    for root, dirs, files in os.walk(log_dir, topdown=False):
        for name in files:
            if name.find("html") == -1:
                new_list = []
                f = open(os.path.join(root, name), )
                for line in f:
                    new_list.append(line)
                log_dict[os.path.join(root, name)] = new_list

    return log_dict


def log_search(string_to_find, log_dict):
    result_dict = {}
    if string_to_find[0] == '"':
        string_to_find = string_to_find.replace('"', " ")
    occurrences = 0
    key_list = log_dict.keys()

    for key in key_list:
        result_list = []
        # xrange is going from 0 to n where n is the number of lines in the list.

        for index in range(0, len(log_dict[key])):
            line = (log_dict[key])[index]
            if (line.lower()).find(string_to_find.lower()) != -1:
                occurrences += 1
                if index == 0:
                    index += 1
                try:
                    previous_line = (log_dict[key][index - 1])
                    next_line = (log_dict[key][index + 1])
                except IndexError:
                    nextLine = ""
                result_list.append(" - ")
                if previous_line != "":
                    result_list.append(previous_line)
                result_list.append(line)
                if next_line != "":
                    result_list.append(nextLine)
                if len(result_list) > 0:
                    result_dict[key] = result_list
    result_dict["Metadata"] = [string_to_find, occurrences]
    print("%s results found. Results exported to results.html" % (occurrences))
    write_search_results_to_file(result_dict, result_dir = result_dir, homeurl = "especiallygreatliterature.com")
    return result_dict


def write_search_results_to_file(result_dict, result_dir, homeurl = "especiallygreatliterature.com"):
    query = result_dict["Metadata"][0]
    filename = os.path.join(result_dir, "results/", (query + ".html"))
    if os.path.isfile(filename):
        os.remove(filename)
    result_file = open(filename, 'w')
    keys = list(result_dict.keys())
    keys.sort()

    result_file.write(
        "<!DOCTYPE HTML><html><body><body bgcolor='black'><font color='#D5D8DC'><body link='#5DADE2' vlink ='red'><font face='consolas'><font size='2'>")
    occurrences = str(result_dict["Metadata"][1])
    result_file.write("<h2>Searched for " + query + ". Found " + occurrences + " results:<h2>")

    for key in keys:
        filename = re.search('.*\/kiralogs\/(.*)', key)
        if filename == None:
            break
        real_filename = filename.group(1)
        result_file.write(
            "<h3>Results from <a href='http://" + homeurl + "/kiralogs/" + real_filename + "'>" + real_filename + "</a href>:\n</h3>")
        for line in result_dict[key]:
            if key != "Metadata":
                line = line.replace("<", "&#60")
                line = line.replace(">", "&#62")
                result_file.write(line + "<br>")
        result_file.write("<hr>")
    result_file.write("</body></html>")

    result_file.close()


def log_cleaner(line):
    m = re.split('(\d{2}:\d{2}:\d{2})\s:(\w*)!(~\S*)\s(\S*)\s', line)
    if len(m) < 4:
        clean_line = line
    elif m[4] == "PRIVMSG":
        n = re.split("(.*)\sPRIVMSG (#\S{0,10})\s:(.*)", line)
        clean_line = "[" + m[1] + "] <" + m[2] + "> " + n[3]
        # n[1] should be the stuff before privmsg, n[2] should be the channel, n[3] should be the text.
    else:
        clean_line = "[" + m[1] + "] <" + m[2] + "> " + m[4]
    return clean_line


def quote_search(query, quote_dict):
    # Loops through the quote array searching for a user-input string. When it finds the string,
    # it prints out that quote.
    # TODO: 'searchString[2]' prints out the second incidence of the string.
    searchNumber = 1
    matches = []
    for x in range(0, len(quote_dict)-1):
        if (quote_dict[x].lower()).find(query.lower()) != -1:
            if searchNumber == 1:
                # sendMsg("String \"" + searchString + "\" located in quote #" + str(quoteIndex) + ":\n")
                int(quoteIndex)
                matches.append(quoteIndex)
                # sendMsg(quoteDatabase[quoteIndex])
                quoteIndex = quoteIndex + 1

    if len(matches) == 0:
        return "No matches found."
        # works
    else:
        # build match list:
        strMatches = "#"
        first = True
        for i in matches:
            if first:
                strMatches += str(i)
                first = False
            else:
                strMatches += (", #" + str(i))
        strMatches += (".\n")
        return "Found match(es) in quotes " + strMatches


def kiraquote(restOfText, quote_db):
    """
    Takes either an index or no argument, returns either the quote with the index or nothing.
    """
    if restOfText == "":
        index = randrange(len(quoteDatabase))
        return "Quote #" + str(index) + ":" + "\n" + quote_db[index]
    else:
        index = int(restOfText)

        return "Quote #" + str(index) + ":" + "\n\x03" + quoteDatabase[index]
