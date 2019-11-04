import discord
import file_utils as f
import dict_writer as writer
import random

TOKEN = f.readToken()
client = discord.Client()
noreply = []
noreply = f.readBlacklist()
pre = "?"
stats = writer.dict_writer(file = "usage_stats.txt")
if not stats.does_exist: stats.generate_file()
def msgStartsWith(message, str): return message.content.lower().startswith(str)

@client.event
async def on_message(message):
    channel = message.channel

    # Make sure the bot doesn't reply to itself
    if message.author == client.user:
        return

    # Essentially ping, without the time measurement: pre + "hello"
    if msgStartsWith(message, pre + 'hello'): await channel.send('Hey {0.author.mention}'.format(message))

    # Reply with the user's UUID
    if msgStartsWith(message, pre + 'id'): 
        if len(message.mentions) > 1: return
        elif len(message.mentions) == 1: 
            uuid = message.mentions[0].id
            msg_length = len(message.content)
            if msg_length - len(message.mentions[0].mention) > len(pre + "id "): 
                await channel.send("Bad syntax: `" + pre + "id [@mention]` \n" +
                "`//mention is optional, if none is given then it will return the author's uuid`")
                return
        else: 
            uuid = message.author.id
        await channel.send(client.get_user(uuid).name +"'s UUID is: " + str(uuid))

    # Adds/removes users from the blacklist: pre + "noreply"
    if msgStartsWith(message, pre + 'noreply'):
        if message.author.id in noreply:
            noreply.remove(message.author.id)
            f.updateBlacklist(noreply)
            await channel.send("You have been successfully removed from the blacklist")
        else:
            noreply.append(message.author.id)
            f.updateBlacklist(noreply)
            await channel.send("You have been added to the blacklist")

    # Prints the current blacklist: pre + "blacklist"
    if msgStartsWith(message, pre + 'blacklist'):
        blacklist = []
        for i in noreply:
            user = await client.fetch_user(i)
            blacklist.append(str(user.display_name))
        msg = "Currently blacklisted users are: " + ", ".join(blacklist)
        await channel.send(msg)

    # Prints the help menu: pre + "help"
    if  msgStartsWith(message, pre + 'help'):
        msg = ("Hey, {0.author.mention} here's my list of commands.\n".format(message) +
        pre +'hello - Says hello back and pings you\n' +
        pre +'noreply - Toggles dad joke opportunity detection for you\n' +
        pre +"stats - Shows how many times you've been dad'ed\n" +
        pre +"leaderboard - Shows the top 10 most dad'ed users\n" +
        pre +'help - Displays this menu\n' +
        pre +'blacklist - Lists the currently ignored users\n' +
        pre +'ID - Replies with your UUID\n' +
        '**HERA** v1.03')
        await channel.send(msg)

    # Replies with the amount of times HERA has replied to the specified user, if no username is given 
    # then it defaults to the author of the message
    if msgStartsWith(message, pre + 'stats'):
        if len(message.mentions) == 1: 
            uuid = message.mentions[0].id
            msg_length = len(message.content)
            if msg_length - len(message.mentions[0].mention) > len(pre + "stats "): 
                await channel.send("Bad syntax: `" + pre + "stats [@mention]` \n" +
                "`//mention is optional, if none is given then it will return the author's stats`")
                return
        elif len(message.mentions) > 1: return
        else: 
            uuid = message.author.id
        author_stats = stats.get_definition(str(uuid))
        if author_stats == None:
            author_stats = 0
            stats.update_value({str(uuid) : author_stats})
        if int(author_stats) == 1:
            await channel.send(client.get_user(uuid).name + " has been dad'ed " + str(author_stats) + " time.")
        else:
            await channel.send(client.get_user(uuid).name + " has been dad'ed " + str(author_stats) + " times.")

    try:
        #I’m
        # this if statement causes an error for some reason
        if msgStartsWith(message, "im ") or msgStartsWith(message, "me ") or ( ord(message.content.lower()[0]) == 105 and (ord(message.content.lower()[1]) == 39 or ord(message.content.lower()[1]) == 8217) and ord(message.content.lower()[2]) == 109 and message.content.lower()[3] == " "):
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
            await channel.send("Hi "+msg+", I'm Hera")
            author_stats = stats.get_definition(str(message.author.id))
            if author_stats == None:
                stats.update_value({str(message.author.id) : 1})
            else:
                stats.update_value({str(message.author.id) : int(author_stats) + 1})
    except:
        print(str(message.content))
    
    if msgStartsWith(message, pre + 'leaderboard'):
            if stats.get_length() < 10: _max = stats.get_length()
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
            await channel.send(embed=embed) 


    #creator only commands
    if message.author.id == 243885191527923723:
        if msgStartsWith(message, '?stop') and client.user.name == "HeraBeta":
            await channel.send("Beta shutdown...")
            await client.logout()

        if msgStartsWith(message, pre + 'stop'):
            await channel.send("Going offline...")
            await client.logout()
        
        if msgStartsWith(message, pre + 'speak'):
           await channel.send(message.content[7:])

        if msgStartsWith(message, pre + 'embed'):
            if stats.get_length() < 10: _max = stats.get_length()
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
                print(str(x[0]))
                if not x[0] == 0:
                    users += "\n" + client.get_user(int(x[0])).name
                    times += "\n" + str(x[1])
            embed=discord.Embed(title="Dad Bot Leaderboard", color=0x800040)
            embed.add_field(name="Users", value=users, inline=True)
            embed.add_field(name="Times they've been got", value=times, inline=True)
            await channel.send(embed=embed) 

        if msgStartsWith(message, pre + 'update'):
            msg = message.content
            if len(message.mentions) != 1 or (msg.find("+") == -1 and msg.find("-") == -1): 
                await channel.send("Bad syntax:\n" + pre +" @user +/-[value]")
                return
            else: uuid = message.mentions[0].id
            split = max([msg.find("+"), msg.find("-")])
            if msg[split] == "+": split += 1
            value = int(msg[split:].strip())
            author_stats = stats.get_definition(str(uuid))
            if author_stats == None: author_stats = 0
            stats.update_value({str(uuid) : int(author_stats) + value})
            await channel.send(client.get_user(uuid).name +" has now been dad'ed " + str(stats.get_definition(str(uuid)) + " times."))


            

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    game = discord.Game(pre + "leaderboard")
    await client.change_presence(status=discord.Status.idle, activity=game)

client.run(TOKEN)
