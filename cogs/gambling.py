import discord, secrets, os, asyncio, random
from discord.ext import commands
from discord.ext.commands import BucketType
from utils.checks import *

from cogs.shard_communication import user_on_cooldown as user_cooldown


class BlackJack:
    def __init__(self, ctx, money):
        self.deck = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] * 4
        self.cards = {
            "adiamonds": "<:adiamonds:508321810832556033>",
            "2diamonds": "<:2diamonds:508321809536385024>",
            "3diamonds": "<:3diamonds:508321809729585172>",
            "4diamonds": "<:4diamonds:508321809678991362>",
            "5diamonds": "<:5diamonds:508321810098683910>",
            "6diamonds": "<:6diamonds:508321810325176333>",
            "7diamonds": "<:7diamonds:508321810300010497>",
            "8diamonds": "<:8diamonds:508321810635292693>",
            "9diamonds": "<:9diamonds:508321810836881438>",
            "10diamonds": "<:10diamonds:508321811016974376>",
            "jdiamonds": "<:jdiamonds:508321810878824460>",
            "qdiamonds": "<:qdiamonds:508321811016974376>",
            "kdiamonds": "<:kdiamonds:508321811612696576>",
            "aclubs": "<:aclubs:508321811151192064>",
            "2clubs": "<:2clubs:508321809221812245>",
            "3clubs": "<:3clubs:508321809410818096>",
            "4clubs": "<:4clubs:508321809926717450>",
            "5clubs": "<:5clubs:508321810127912970>",
            "6clubs": "<:6clubs:508321810622971904>",
            "7clubs": "<:7clubs:508321810182438955>",
            "8clubs": "<:8clubs:508321810421514279>",
            "9clubs": "<:9clubs:508321810677497894>",
            "10clubs": "<:10clubs:508321810794676234>",
            "jclubs": "<:jclubs:508321811176488960>",
            "qclubs": "<:qclubs:508321811407306762>",
            "kclubs": "<:kclubs:508321811365101578>",
            "ahearts": "<:ahearts:508321810828361742>",
            "2hearts": "<:2hearts:508321809632854016>",
            "3hearts": "<:3hearts:508321809662345231>",
            "4hearts": "<:4hearts:508321810023186442>",
            "5hearts": "<:5hearts:508321810396348456>",
            "6hearts": "<:6hearts:508321810249678852>",
            "7hearts": "<:7hearts:508321810417451008>",
            "8hearts": "<:8hearts:508321810635423748>",
            "9hearts": "<:9hearts:508321810727829533>",
            "10hearts": "<:10hearts:508321810970836992>",
            "jhearts": "<:jhearts:508321811373621249>",
            "qhearts": "<:qhearts:508321867954782208>",
            "khearts": "<:khearts:508321811424083969>",
            "aspades": "<:aspades:508321810811584527>",
            "2spades": "<:2spades:508321809591173120>",
            "3spades": "<:3spades:508321809981112340>",
            "4spades": "<:4spades:508321810190696458>",
            "5spades": "<:5spades:508321810400673824>",
            "6spades": "<:6spades:508321810358599680>",
            "7spades": "<:7spades:508321810874630155>",
            "8spades": "<:8spades:508321810828492820>",
            "9spades": "<:9spades:508321810815647744>",
            "10spades": "<:10spades:508321810874499083>",
            "jspades": "<:jspades:508321811298254875>",
            "qspades": "<:qspades:508321868193726464>",
            "kspades": "<:kspades:508321811457507329>",
        }
        self.ctx = ctx
        self.msg = None
        self.over = False
        self.money = money

    def pretty(self, it):
        return " ".join(
            [
                self.cards[
                    f"{i if isinstance(i, int) else i.lower()}{random.choice(['diamonds', 'hearts', 'clubs', 'spades'])}"
                ]
                for i in it
            ]
        )

    def deal(self):
        hand = []
        for i in range(2):
            random.shuffle(self.deck)
            card = self.deck.pop()
            if card == 11:
                card = "J"
            if card == 12:
                card = "Q"
            if card == 13:
                card = "K"
            if card == 14:
                card = "A"
            hand.append(card)
        return hand

    def total(self, hand):
        total = 0
        no_aces = [h for h in hand if h != "A"]
        aces = [h for h in hand if h == "A"]
        for card in no_aces:
            if card == "J" or card == "Q" or card == "K":
                total += 10
            else:
                total += card
        for card in aces:
            if total >= 11:
                total += 1
            else:
                total += 11
        return total

    def has_bj(self, hand):
        if not [a for a in hand if a == "A"]:
            return False
        if not [a for a in hand if a == 10]:
            return False
        return True

    def hit(self, hand):
        card = self.deck.pop()
        if card == 11:
            card = "J"
        if card == 12:
            card = "Q"
        if card == 13:
            card = "K"
        if card == 14:
            card = "A"
        hand.append(card)
        return hand

    async def player_win(self):
        ### See https://media.discordapp.net/attachments/521026764659490836/521037532209741826/Bag.png
        # if not await has_money(self.ctx.bot, self.ctx.author.id, self.money):
        #    return await self.ctx.send("You spent the money in the meantime.. Bleh!")
        await self.ctx.bot.pool.execute(
            'UPDATE profile SET money=money+$1 WHERE "user"=$2;',
            self.money,
            self.ctx.author.id,
        )

    async def dealer_win(self):
        # if not await has_money(self.ctx.bot, self.ctx.author.id, self.money):
        #    return await self.ctx.send("You spent the money in the meantime.. Bleh!")
        await self.ctx.bot.pool.execute(
            'UPDATE profile SET money=money-$1 WHERE "user"=$2;',
            self.money,
            self.ctx.author.id,
        )

    async def results(self, bj=False, win=False):
        player = self.total(self.player)
        dealer = self.total(self.dealer)
        winner = None
        text = f"The dealer has a {self.pretty(self.dealer)} for a total of {dealer}\nYou have a {self.pretty(self.player)} for a total of {player}\n"
        if bj:
            if self.has_bj(self.dealer) and self.has_bj(self.player):
                text = f"{text}You both have a blackjack!"
                winner = "both"
            elif self.has_bj(self.player):
                text = f"{text}\nCongratulations! You got a Blackjack!"
                winner = "player"
            elif self.has_bj(self.dealer):
                text = f"{text}\nSorry, you lose. The dealer got a blackjack."
                winner = "dealer"
        if win:
            if player > 21:
                text = f"{text}Sorry. You busted. You lose."
                winner = "dealer"
            elif dealer > 21:
                text = f"{text}Dealer busts. You win!"
                winner = "player"
            elif player < dealer:
                text = (
                    f"{text}Sorry. Your score isn't higher than the dealer. You lose."
                )
                winner = "dealer"
            elif dealer < player:
                text = f"{text}Congratulations. Your score is higher than the dealer. You win"
                winner = "player"
            elif player == dealer:
                text = f"{text}It's a tie!"
                winner = "both"
        if not self.msg:
            self.msg = await self.ctx.send(text)
        else:
            await self.msg.edit(content=text)
        if winner == "player":
            self.over = True
            await self.player_win()
        elif winner == "dealer":
            self.over = True
            await self.dealer_win()
        elif winner == "both":
            self.over = True

    async def run(self):
        self.player = self.deal()
        self.dealer = self.deal()
        await self.results(bj=True)
        if self.over == True:
            return
        await self.msg.add_reaction("\U00002934")
        await self.msg.add_reaction("\U00002935")
        while (
            not self.over
            and self.total(self.dealer) < 22
            and self.total(self.player) < 22
        ):

            def check(reaction, user):
                return (
                    reaction.message.id == self.msg.id
                    and user == self.ctx.author
                    and str(reaction.emoji) in ["\U00002934", "\U00002935"]
                )

            try:
                reaction, user = await self.ctx.bot.wait_for(
                    "reaction_add", check=check, timeout=20
                )
            except asyncio.TimeoutError:
                await self.dealer_win()
                return await self.ctx.send("Blackjack timed out...")
            if reaction.emoji == "\U00002934":
                choice = "h"
            else:
                choice = "s"
            if choice == "h":
                self.hit(self.player)
                while self.total(self.dealer) < 17:
                    self.hit(self.dealer)
            elif choice == "s":
                while self.total(self.dealer) < 17:
                    self.hit(self.dealer)
                self.over = True
            await self.results()
        await self.results(win=True)


class Gambling:
    def __init__(self, bot):
        self.bot = bot

    @user_cooldown(5)
    @commands.command(description="Draw a card!", aliases=["card"])
    async def draw(self, ctx):
        await ctx.trigger_typing()
        files = os.listdir("cards")
        await ctx.send(file=discord.File(f"cards/{secrets.choice(files)}"))

    @has_char()
    @user_cooldown(5)
    @commands.command(description="Flip a coin to win some money!", aliases=["coin"])
    async def flip(self, ctx, side: str = "heads", amount: int = 0):
        side = side.lower()
        if not side in ["heads", "tails"]:
            return await ctx.send(f"Use `heads` or `tails` instead of `{side}`.")
        if amount < 0:
            return await ctx.send("Invalid money amount. Must be 0 or higher.")
        if amount > 100_000:
            return await ctx.send("You will think of a better way to spend this.")
        if not await has_money(self.bot, ctx.author.id, amount):
            return await ctx.send("You are too poor.")
        result = secrets.choice(["heads", "tails"])
        if result == "heads":
            resultemoji = "<:heads:437981551196897281>"
        else:
            resultemoji = "<:tails:437981602518138890>"
        async with self.bot.pool.acquire() as conn:
            if result == side:
                await conn.execute(
                    'UPDATE profile SET money=money+$1 WHERE "user"=$2;',
                    amount,
                    ctx.author.id,
                )
                await ctx.send(
                    f"{resultemoji} It's **{result}**! You won **${amount}**!"
                )
            else:
                await conn.execute(
                    'UPDATE profile SET money=money-$1 WHERE "user"=$2;',
                    amount,
                    ctx.author.id,
                )
                await ctx.send(
                    f"{resultemoji} It's **{result}**! You lost **${amount}**!"
                )

    @has_char()
    @user_cooldown(5)
    @commands.command(description="Roll the dice and win some money!")
    async def bet(self, ctx, maximum: int = 6, tip: int = 6, money: int = 0):
        if maximum < 2:
            return await ctx.send("Invalid Maximum.")
        if tip > maximum or tip < 1:
            return await ctx.send(
                f"Invalid Tip. Must be in the Range of `1` to `{maximum}`."
            )
        if money < 0:
            return await ctx.send("Invalid money amount. Must be 0 or higher.")
        if money * (maximum - 1) > 100_000:
            return await ctx.send("Spend it in a better way. C'mon!")
        if not await has_money(self.bot, ctx.author.id, money):
            return await ctx.send("You're too poor.")
        randomn = secrets.randbelow(maximum + 1)
        async with self.bot.pool.acquire() as conn:
            if randomn == tip:
                await conn.execute(
                    'UPDATE profile SET money=money+$1 WHERE "user"=$2;',
                    money * (maximum - 1),
                    ctx.author.id,
                )
                await ctx.send(
                    f"You won **${money*(maximum-1)}**! The random number was `{randomn}`, you tipped `{tip}`."
                )
            else:
                await conn.execute(
                    'UPDATE profile SET money=money-$1 WHERE "user"=$2;',
                    money,
                    ctx.author.id,
                )
                await ctx.send(
                    f"You lost **${money}**! The random number was `{randomn}`, you tipped `{tip}`."
                )

    @user_cooldown(15)
    @commands.command(aliases=["bj"], description="Play some Blackjack")
    async def blackjack(self, ctx, amount: int):
        if amount < 0:
            return await ctx.send("Meh, choose a positive value!")
        elif amount > 1000:
            return await ctx.send(
                "Sorry, due to this being in an experimental status, more than $1000 is not allowed."
            )
        if not await has_money(self.bot, ctx.author.id, amount):
            return await ctx.send("You're too poor.")
        bj = BlackJack(ctx, amount)
        await bj.run()


def setup(bot):
    bot.add_cog(Gambling(bot))
