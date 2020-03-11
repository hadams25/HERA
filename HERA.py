import discord
import file_utils as f
import dict_writer as writer
import random
import re


TOKEN = f.readToken()
client = discord.Client()
noreply = []
noreply = f.readBlacklist()
pre = "~"
stats = writer.dict_writer(file = "usage_stats.txt")
if not stats.does_exist: stats.generate_file()
def regexMatch(message, regex): 
    regex = re.compile(regex)
    return regex.match(message.content)

def regexSearch(message, regex): 
    regex = re.compile(regex)
    return regex.search(message.content)

def regexGetMatch(message, regex, index):
    regex = re.compile(regex)
    try:
        return regex.findall(message.content)[index]
    except:
        return False

def regexReplace(message, regex, replacement):
    regex = re.compile(regex)
    return re.sub(regex, replacement, message.content)

lastmsg = []

#this code is so bad
@client.event
async def on_message(message):
    global lastmsg
    channel = message.channel

    #keep history to the last 10 messages max
    while (len(lastmsg) > 10):
        lastmsg = lastmsg[1:]

    # Make sure the bot doesn't reply to itself
    if message.author == client.user:
        return

    #Commands
    if regexMatch(message, pre):
        message.content = message.content[1:]

        # Prints the help menu: "help"
        if  regexMatch(message, 'help\\s*\\Z'):
            msg = ("Hey, {0.author.mention} here's my list of commands.\n".format(message) +
            pre +'hello - Says hello back and pings you\n' +
            pre +'noreply - Toggles dad joke opportunity detection for you\n' +
            pre +"stats - Shows how many times you've been dad'ed\n" +
            pre +"leaderboard - Shows the top 10 most dad'ed users\n" +
            pre +'help - Displays this menu\n' +
            pre +'blacklist - Lists the currently ignored users\n' +
            pre +'ID - Replies with your UUID\n' +
            '**HERA** v1.50')
            lastmsg.append(await channel.send(msg))
            return

        # Essentially ping, without the time measurement: "hello"
        if regexMatch(message, 'hello(\\s)*\\Z'): 
            lastmsg.append(await channel.send('Hey {0.author.mention}'.format(message)))
            return

        # Adds/removes users from the blacklist: "noreply"
        if regexMatch(message, 'noreply\\b'):
            if message.author.id in noreply:
                noreply.remove(message.author.id)
                f.updateBlacklist(noreply)
                if (not regexSearch(message, "[\\-~](silent|[sS])")): 
                    lastmsg.append(await channel.send("You have been successfully removed from the blacklist"))
            else:
                noreply.append(message.author.id)
                f.updateBlacklist(noreply)
                if (not regexSearch(message, "[\\-~](silent|[sS])")): 
                    lastmsg.append(await channel.send("You have been added to the blacklist"))
            return
        
         # Replies with the amount of times HERA has replied to the specified user, if no username is given 
        # then it defaults to the author of the message: "stats"
        if regexMatch(message, 'stats\\b'):
            if len(message.mentions) == 1: 
                uuid = message.mentions[0].id
            elif len(message.mentions) > 1: return
            else: 
                uuid = message.author.id
            author_stats = stats.get_definition(str(uuid))
            if author_stats == None:
                author_stats = 0
                stats.update_value({str(uuid) : author_stats})
            if int(author_stats) == 1:
                lastmsg.append(await channel.send(client.get_user(uuid).name + " has been dad'ed " + str(author_stats) + " time."))
            else:
                lastmsg.append(await channel.send(client.get_user(uuid).name + " has been dad'ed " + str(author_stats) + " times."))
            return
        
        # Shows the current top 10 users
        if regexMatch(message, 'leaderboard\\b'):
            if stats.get_length() < 10: _max = stats.get_length()
            elif (regexSearch(message, "[\\-~]([aA]ll|[aA])")): _max = stats.get_length()
            else: _max = 10
            board = []
            for i in range(0,_max):
                board.append([0,0])

            board[0][0] = stats.get_key(0)
            board[0][1] = int(stats.get_val_from_line(0))

            for i in range(0, stats.get_length()):
                tmp = int(stats.get_val_from_line(i))
                if client.get_user(int(stats.get_key(i))) == None: pass
                elif board[0][1] < tmp:
                    board = f.shift(board, 0)
                    board[0][0] = stats.get_key(i)
                    board[0][1] = tmp
                elif board[len(board) - 1][1] > tmp: continue
                elif board[0][1] > tmp:
                    j = 1
                    while board[j][1] > tmp and j < len(board):
                        j += 1
                    if j != len(board) - 1:
                        board = f.shift(board, j)
                        board[j][0] = stats.get_key(i)
                        board[j][1] = tmp
            users = ""
            times = ""
            for x in board:
                if not x[0] == 0:
                    users += "\n" + client.get_user(int(x[0])).name
                    times += "\n" + str(x[1])
            embed=discord.Embed(title="Dad Bot Leaderboard", color=0x800040)
            embed.add_field(name="Users", value=users, inline=True)
            embed.add_field(name="Times they've been got", value=times, inline=True)
            lastmsg.append(await channel.send(embed=embed))
            return

        # Prints the current blacklist: "blacklist"
        if regexMatch(message, 'blacklist\\s*\\Z'):
            blacklist = []
            for i in noreply:
                user = await client.fetch_user(i)
                blacklist.append(str(user.display_name))
            msg = "Currently blacklisted users are: " + ", ".join(blacklist)
            lastmsg.append(await channel.send(msg))
            return

        # Reply with the user's UUID: "id"
        if regexMatch(message, '[iI][dD](\\s)*\\Z'): 
            if len(message.mentions) == 1: 
                uuid = message.mentions[0].id
            elif len(message.mentions) > 1: return
            else: 
                uuid = message.author.id
            lastmsg.append(await channel.send(client.get_user(uuid).name +"'s UUID is: " + str(uuid)))
            return

    #creator only commands
        #checks if the author's user id is @Ketchup#1687
        if message.author.id == 243885191527923723:
            #kills the bot
            if regexMatch(message, 'stop\\b'):
                if (not regexSearch(message, "[\\-~](silent|[sS])")): 
                    await channel.send("Going offline...")
                await client.logout()
            
            #makes the bot repeat whatever you say
            if regexMatch(message, 'speak\\b'):
                lastmsg.append(await channel.send(message.content[6:]))
                return

            #Edits the specified users dad count
            if regexMatch(message, 'update\\b'):
                msg = message.content
                if len(message.mentions) != 1 or not regexSearch(message, "[\\-+][0-9]+"): 
                    lastmsg.append(await channel.send("Bad syntax:\n" + pre +" @user +/-[value]"))
                    return
                else: uuid = message.mentions[0].id
                value = int(regexGetMatch(message, "[\\-+][0-9]+", 0))
                lastmsg.append(await channel.send("Bad syntax:\n" + pre +" @user +/-[value]"))
                author_stats = stats.get_definition(str(uuid))
                if author_stats == None: author_stats = 0
                stats.update_value({str(uuid) : int(author_stats) + value})
                if (not regexSearch(message, "[\\-~](silent|[sS])")): 
                    lastmsg.append(await channel.send(client.get_user(uuid).name +" has now been dad'ed " + str(stats.get_definition(str(uuid)) + " times.")))
                return
            
            #Removes most recent daddening
            if regexMatch(message, 'delete\\b'):
                if(lastmsg == []): 
                    lastmsg.append(await channel.send("No messages in history."))
                    return
                if(regexSearch(message, "[0-9]+")): index = int(regexGetMatch(message, "[0-9]+", 0)) + 1
                if(regexSearch(message, "[\\-~](all|[aA])")): index = len(lastmsg)
                else: index = 1
                for _ in range(0, index):
                    tmpMsg = lastmsg.pop()
                    if (type(tmpMsg) is tuple):
                        try:
                            await tmpMsg[0].delete()
                        except:
                            print("\nError deleting message: " + tmpMsg[0].content +"\n")
                        stats.update_value({str(tmpMsg[1]) : int(stats.get_definition(str(tmpMsg[1]))) - 1})
                    else:
                        try:
                            await tmpMsg.delete()
                        except:
                            print("\nError deleting message: " + tmpMsg.content +"\n")
                if (not regexSearch(message, "[\\-~](silent|[sS])")): 
                    lastmsg.append(await channel.send("Deleted " + str(index) + " message(s)."))
                return
            
            if regexMatch(message, "history\\b"):
                if(lastmsg == []): 
                    lastmsg.append(await channel.send("No messages in history."))
                    return
                msg = "Here are the last " + str(len(lastmsg)) + " message(s): \n"
                for x in lastmsg:
                    if type(x) is tuple: msg += x[0].message + "\n\n"
                    else: msg += x.content + "\n\n"
                lastmsg.append(await channel.send(msg))
                return


    #End commands

    #Daddening Logic
    try:
        #if "im" or "me"
        if (regexMatch(message, "(([iI]['’]?[mM])|([Mm][Ee]))\\s+[^\\s]")):

            if message.author.id in noreply: return
            msg = message.content
            if len(msg.split()) < 2: return
            msg = msg[msg.find(" ") + 1:]
            if len(msg.split()) == 1:
                if msg[-1] == ".":
                    msg = msg[0:len(msg)-1]
                if len(msg) == 1 and not 97 <= ord(msg.lower()) <= 122: return
            elif len(msg.split()) >= 2:
                splitIndex = max([msg.find("."), msg.find(",")])
                if splitIndex == -1: splitIndex = len(msg)
                msg = msg[:splitIndex]
            if msg == "": return
            msg = msg.replace("\n", "")
            lastmsg.append((await channel.send("Hi "+msg+", I'm Hera"), message.author.id))
            author_stats = stats.get_definition(str(message.author.id))
            if author_stats == None:
                stats.update_value({str(message.author.id) : 1})
            else:
                stats.update_value({str(message.author.id) : int(author_stats) + 1})
    except:
        print(str(message.content))


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    game = discord.Game(pre + "leaderboard")
    await client.change_presence(status=discord.Status.idle, activity=game)

client.run(TOKEN)
