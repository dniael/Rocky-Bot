import nextcord
from nextcord.ext import commands
import os
import numpy as np
import matplotlib.pyplot as plt
import simpleeval
import math
from cogs.help_cog import HelpCommand

my_names = simpleeval.DEFAULT_NAMES.copy()
my_functions = simpleeval.DEFAULT_FUNCTIONS.copy()


def is_prime(x):
    if x == 1:
        return False

    count = 2
    while count ** 2 <= x:
        if x % count == 0:
            return False
        count += 1
    return True


my_names.update(
    {
        "pi": math.pi,
        "e": math.e
    }
)

my_functions.update(
    sqrt=(lambda x: math.sqrt(x)),
    ceil=(lambda x: math.ceil(x)),
    floor=(lambda x: math.floor(x)),
    fact=(lambda x: math.factorial(x)),
    log=(lambda x, y: math.log(x)),
    sin=(lambda x: math.sin(x)),
    cos=(lambda x: math.cos(x)),
    tan=(lambda x: math.tan(x)),
    asin=(lambda x: math.asin(x)),
    acos=(lambda x: math.acos(x)),
    atan=(lambda x: math.atan(x)),
    deg=(lambda x: math.degrees(x)),
    rad=(lambda x: math.radians(x)),
    asinh=(lambda x: math.asinh(x)),
    acosh=(lambda x: math.acosh(x)),
    atanh=(lambda x: math.atanh(x)),
    sinh=(lambda x: math.sinh(x)),
    cosh=(lambda x: math.cosh(x)),
    tanh=(lambda x: math.tanh(x)),
    prime=(lambda x: is_prime(x)),
    lcm=(lambda x, y: np.lcm(x, y)),
    gcd=(lambda x, y: np.gcd(x, y)),
    cbrt=(lambda x: np.cbrt(x))

)


class Maffs(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.description = 'Math commands!'

    @commands.group(help='some commands relating to mathematics')
    async def math(self, ctx):
        if ctx.invoked_subcommand is None:
            group = HelpCommand()
            await group.send_group_help_poo(ctx, ctx.command)

    @math.command(aliases=['quad', 'q'], help='Gives you the roots and vertex')
    @commands.cooldown(5, 5, commands.BucketType.user)
    async def quadratic(self, ctx, a: float, b: float, c: float):
        xv, yv = 0, 0
        x1, x2 = 0, 0
        msg = ''
        no_roots = False
        one_root = False
        try:
            if b ** 2 - 4 * a * c > 0:
                x1 = round((-1 * b + math.sqrt(b ** 2 - 4 * a * c)) / (2 * a), 3)
                x2 = round((-1 * b - math.sqrt(b ** 2 - 4 * a * c)) / (2 * a), 3)
                xv = round((-1 * b) / (2 * a), 3)
                yv = round(a * xv ** 2 + b * xv + c, 3)
                msg = f'roots are {x1} and {x2} and vertex is ({xv}, {yv})'
            elif b ** 2 - 4 * a * c == 0:
                x = round((-1 * b + math.sqrt(b ** 2 - 4 * a * c)) / (2 * a), 3)
                xv = round((-1 * b) / (2 * a), 3)
                yv = round(a * xv ** 2 + b * xv + c, 2)
                one_root = True
                msg = f'root is {x} and vertex is ({xv}, {yv})'
            else:
                xv = round((-1 * b) / (2 * a), 3)
                yv = round(a * xv ** 2 + b * xv + c, 3)
                no_roots = True
                msg = f"the equation {a}x^2 + {b}x + {c} has no real roots and its vertex is ({xv}, {yv})"

        except ZeroDivisionError:
            await ctx.send(f'{ctx.author.mention}, You cannot divide by 0!')

        x = np.arange(-10, 10, 0.1)
        y = a * x ** 2 + b * x + c

        plt.grid(True)
        plt.plot(x, y)
        # plt.title(f'{ctx.author}\'s quadratic')
        plt.xlabel('x-axis')
        plt.ylabel('y-axis')

        if not one_root and no_roots:
            plt.scatter(x1, 0, color="black")
            plt.scatter(x2, 0, color="black")
            plt.text(x1, 0, f"({x1}, 0)")
            plt.text(x2, 0, f"({x2}, 0)")
        elif one_root:
            plt.scatter(x, 0, color="black")
            plt.text(x, 0, f"({x1}, 0)")

        plt.scatter(xv, yv, color="black")
        plt.text(xv, yv, f"({xv}, {yv})")
        plt.savefig(fname='quadratic')
        graph = nextcord.File("quadratic.png")
        embed = nextcord.Embed(title=f"Quadratic {a}x^2 + {b}x + {c}", description=msg)
        embed.set_image(url="attachment://quadratic.png")
        await ctx.send(file=graph, embed=embed)
        os.remove('quadratic.png')
        plt.clf()


    @math.command(aliases=['g'], help='graphs a equation of your choice, use r!help graph for more info')
    @commands.cooldown(5, 5, commands.BucketType.user)
    async def graph(self, ctx, a: float, b: float, c: float, eq_type=None):
        if not eq_type:
            await ctx.send(
                f"{ctx.author.mention}Please specify an equation type to graph! Currently available: linear, "
                f"quadratic")
        elif eq_type == 'linear':
            x = np.arange(-20, 20, 0.1)

            y_vals = a * x + b * x + c

            plt.grid(True)
            plt.plot(x, y_vals)
            plt.title(f'{ctx.author}\'s graph')
            plt.xlabel('x-axis')
            plt.ylabel('y-axis')
            plt.savefig(fname='graph')
            await ctx.send(file=nextcord.File('graph.png'))
            os.remove('graph.png')
            plt.clf()

        elif eq_type == 'quadratic':
            x = np.arange(-20, 20, 0.1)
            y = a * x ** 2 + b * x + c

            plt.grid(True)
            plt.plot(x, y)
            plt.title(f'{ctx.author}\'s graph')
            plt.xlabel('x-axis')
            plt.ylabel('y-axis')
            plt.savefig(fname='graph')
            await ctx.send(file=nextcord.File('graph.png'))
            os.remove('graph.png')
            plt.clf()

        else:
            await ctx.send(f'{ctx.author.mention}, {eq_type} is not a valid equation type!')

    @math.command(aliases=['eval', 'ev'])
    async def evaluate(self, ctx, *, function):
        """Evaluates simple mathematical functions"""

        try:
            if len(function) > 69:
                await ctx.send(f'{ctx.author.mention}, your equation is too long!')
            else:
                equation = function.replace(' ', '')
                equation = equation.replace('^', '**')
                answer = simpleeval.simple_eval(equation, functions=my_functions, names=my_names)
                await ctx.send(f'{ctx.author.mention}, {equation} = {answer}')
        except (TypeError, NameError, SyntaxError, ValueError):
            await ctx.send(f'{ctx.author.mention} Syntax Error!')
        except ZeroDivisionError:
            await ctx.send(f'{ctx.author.mention}, you cannot divide by zero!')
        except OverflowError:
            await ctx.send(f'{ctx.author.mention}, answer tooooooooooooo loooooooooooooooooooong')

    @math.command(aliases=['c', 'cel', 'C'], help='converts fahrenheit to celsius')
    async def celsius(self, ctx, temp: float = None):
        if not temp:
            await ctx.send(f'{ctx.author.mention}, you must specify a temperature!')
        else:
            cel = round((temp - 32) / 1.8, 3)
            await ctx.send(f'{temp} degrees fahrenheit is {cel} degrees celsius.')

    @math.command(aliases=['f', 'F'], help='converts celsius to fahrenheit')
    async def fahrenheit(self, ctx, temp: float = None):
        if not temp:
            await ctx.send(f'{ctx.author.mention}, you must specify a temperature!')
        else:
            fahr = round((temp * 1.8) + 32, 3)
            await ctx.send(f'{temp} degrees celsius is {fahr} degrees fahrenheit.')

    @math.command(aliases=['b', 'bc'], help='converts from base 10 to between bases 2-36')
    async def base_convert(self, ctx, base_num: int, num: int):
        try:
            converted_base = np.base_repr(num, base_num)
            await ctx.send(f'{num} in base {base_num} is {converted_base}.')

        except ValueError:
            await ctx.send(f'{ctx.author.mention}, you must specify a base between 2-36!')

    @graph.error
    async def graph_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                f'{ctx.author.mention} Invalid format, use: r!g <a> <b> <c> <type of equation (quadratic/linear)>')
        if isinstance(error, commands.BadArgument):
            await ctx.send(
                f'{ctx.author.mention} Invalid arguments, use: r!g <a> <b> <c> <type of equation (quadratic/linear)>')
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f'{ctx.author.mention}, you are on cooldown! Try again in {error.retry_after:.2f}s')

    @quadratic.error
    async def quadratic_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                f'{ctx.author.mention} Invalid format, use: r!quadratic <a (number)> <b (number)> <c (number)>')
        if isinstance(error, commands.BadArgument):
            await ctx.send(
                f'{ctx.author.mention} Invalid arguments, use: r!quadratic <a (number)> <b (number)> <c (number)>')
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f'{ctx.author.mention}, you are on cooldown! Try again in {error.retry_after:.2f}s')

    @celsius.error
    async def celsius_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(f'{ctx.author.mention}, the temperature must be a number!')

    @fahrenheit.error
    async def fahrenheit_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(
                f'{ctx.author.mention}, the temperature must be a number!')

    @base_convert.error
    async def base_convert_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f'{ctx.author.mention} '
                           f'Incorrect Format, use `r!{ctx.command.qualified_name} | '
                           f'{" | ".join([alias for alias in ctx.command.aliases])}'
                           f' <base_number> <number>`')
        if isinstance(error, commands.BadArgument):
            await ctx.send(f'{ctx.author.mention} '
                           f'Incorrect Format, use `r!{ctx.command.qualified_name} | '
                           f'{" | ".join([alias for alias in ctx.command.aliases])}'
                           f' <base_number> <number>`')

    @evaluate.error
    async def eval_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f'{ctx.author.mention} '
                           f'Incorrect Format, use `r!{ctx.command.qualified_name} | '
                           f'{" | ".join([alias for alias in ctx.command.aliases])} <function>`')


def setup(client):
    client.add_cog(Maffs(client))
