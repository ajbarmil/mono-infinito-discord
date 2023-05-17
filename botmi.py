import discord, urllib, argparse, os
from discord.ext import commands
from SAR_p3_monkey_lib import Monkey

token = open("token.txt","r").read()

def is_url(url):
    return urllib.parse.urlparse(url).scheme != ""


parser = argparse.ArgumentParser(description='Ejecuta el bot de mono infinito.')

parser.add_argument('-p', action='store', required=False, type=str, default='!',
                    help='Prefijo que precede a todos los comandos. El predeterminado es !')

argums = parser.parse_args()

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix=argums.p, intents=intents)

m = Monkey()

block = {}

@client.event
async def on_ready():
    print(f"Sesión iniciada como {client.user}.")

@client.command()
async def construct(ctx, *args):
    blockbool = False
    if(ctx.author.id in block.keys()):
        blockbool = block[ctx.author.id]

    if(blockbool):
        await ctx.send(f"<@{ctx.author.id}> Ya estoy construyendo tu modelo. Si quieres reconstruirlo, tendrás que esperar a que termine.")
    else:
        block[ctx.author.id] = True
        joining = "\n\n"
        lim = 1000
        for i in range(len(args)):
            if(args[i] == "-j"):
                joining = "\n"
            elif(args[i] == "-l"):
                try:
                    lim = int(args[i+1])
                except:
                    pass

        await ctx.send(f"<@{ctx.author.id}> Preparando tu modelo...")

        if(not os.path.exists(f"./data/{ctx.guild.id}/")):
            os.mkdir(f"./data/{ctx.guild.id}/")

        mess = open(f"./data/{ctx.guild.id}/{ctx.author.display_name}.txt","w",encoding="utf8") # create & clean
        mess.close()
        mess = open(f"./data/{ctx.guild.id}/{ctx.author.display_name}.txt", "a",encoding="utf8")
        for channel in ctx.guild.text_channels:
            try:
                async for message in channel.history(limit=lim):
                    if (message.author == ctx.author and not is_url(message.content.replace(ctx.author.display_name + ": ", "")) and str(message.content.replace(ctx.author.display_name + ": ", "")) != ""):
                        mess.write(message.content.replace(ctx.author.display_name + ": ", "") + joining)
            except:
                pass
        mess.close()

        m.compute_lm([f"./data/{ctx.guild.id}/{ctx.author.display_name}.txt"], f"{ctx.author.display_name}", 5)
        m.save_lm(f"./data/{ctx.guild.id}/{ctx.author.display_name}.lm")

        block[ctx.author.id] = False
        await ctx.send(f'<@{ctx.author.id}> Se ha generado tu modelo, con nombre "{ctx.author.display_name}".')

@client.command()
async def talk(ctx, *args):
    if(len(args)!=1 and len(args)!=3):
        await ctx.send(f"<@{ctx.author.id}> Uso del comando talk: talk NOMBRE_MODELO [-n N-GRAMAS].")
    else:
        nn = 3
        allgood = True
        if(len(args)==3 and args[1]=="-n"):
            try:
                nn = int(args[2])
                if(nn not in [2,3,4,5]):
                    await ctx.send(
                        f"<@{ctx.author.id}> La cantidad de n-gramas tiene que ser un número entero del 2 al 5.")
                    allgood = False
            except:
                await ctx.send(f"<@{ctx.author.id}> La cantidad de n-gramas tiene que ser un número entero del 2 al 5.")
                allgood = False

        if(allgood):
            if(os.path.isfile(f"./data/{ctx.guild.id}/{args[0]}.lm")):
                m.load_lm(f"./data/{ctx.guild.id}/{args[0]}.lm")
                await ctx.send(f"[{args[0]}] {m.generate_sentences(n=nn, nsentences=1, prefix=None)}")
            else:
                await ctx.send(f"<@{ctx.author.id}> El modelo que has especificado no existe.")

client.run(token)