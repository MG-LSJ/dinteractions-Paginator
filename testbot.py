from time import perf_counter

start = perf_counter()
import interactions
from dinteractions_Paginator import Paginator
from interactions import Embed

bot = interactions.Client(
    token="ODc0NzgwOTE4MDgxMDE1ODg5.YRL9Nw.8FIwW5yQNMVx92lyFc-XYIXE_gQ"
)
test_component = interactions.Button(style=1, label="test", custom_id="test")


@bot.command(name="test-paginator", description="None.", scope=874781880489222154)
async def my_paginator(ctx):
    await Paginator(
        bot,
        ctx,
        [
            Embed(title="1"),
            Embed(title="2"),
            Embed(title="3"),
            Embed(title="4"),
            Embed(title="5"),
        ],
    ).run()


@bot.event
async def on_ready():
    end = perf_counter()
    print(end - start)


@bot.component(test_component)
async def a_test_component(ctx):
    s = perf_counter()
    await ctx.send("lol")
    print(perf_counter() - s)


bot.start()
