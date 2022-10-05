# Brawling

Sync + async wrapper for the Brawl Stars API

## Installation

To install normally (only sync)

```
pip install brawling
```

There are three additional extras you can install: async, cache, acache

To install with caching support (only sync, installs requests-cache)

```
pip install brawling[cache]
```

To install with async support (will install aiohttp)

```
pip install brawling[async]
```

To install with async caching support (will also install aiohttp, aiohttp-client-cache and aiosqlite)

```
pip install brawling[acache]
```

## Usage

Usage is very simple and straightforward:

```py
import brawling

# This can be either the API token,
# or the path to the file with it.
TOKEN = "..."

# Initialize the client

client = brawling.Client(TOKEN)
battle_log = client.get_battle_log("#yourtag")
client.close()

# or, in an async function

client = brawling.AsyncClient(TOKEN)
battle_log = await client.get_battle_log("#yourtag")
await client.aclose() # note the 'aclose'

# Prints "Battle(battle_time=...)"
print(battle_log[0])
```

Since 1.1 there are also context managers, to automatically release resources:

```py
with brawling.Client(TOKEN) as client:
    player = client.get_player("#...")

# or, in an async function

async with brawling.AsyncClient(TOKEN) as client:
    player = await client.get_player("#...")
```

For some endpoints, there's also a possibility to page over them:

```py
# Returns a generator which fetches up to 20 total pages
# of Ukrainian rankings for Shelly, each page
# being a list of BrawlerRanking model where 0 < len(page) <= 10
pages = client.page_brawler_rankings(
    brawling.BrawlerID.SHELLY,
    per_page=10, region='ua', max=200
)

# ^ Note that this operation was immediate,
# as no data is fetched yet.

# This will now fetch pages of 10 players,
# until either there are no players left,
# or we reach the max limit of 200.

# NOTE: Due to limitations of the API, page methods can return only return
# as many objects as get_* methods, so the only use for them is to
# minimize the traffic if you only need to retrieve a few objects.
for page in pages:
    print(page)
```

The client has additional options you can use when initializing:

```py
Client(TOKEN, proxy=True, strict_errors=False, force_no_cache=True, force_no_sort=True)
```

With `strict_errors` set to False, the API methods can now silently fail instead of raising exceptions, and instead return an `ErrorResponse` object. It's your job to handle it.

The `proxy` argument will use a [3rd party proxy](https://docs.royaleapi.com/#/proxy). Details on setting up are on the linked page. DISCLAIMER: I am not responsible for anything related to the proxy. I am not in any way related to its developers, and it's not my fault if your API access gets blocked because of using it.

`force_no_cache` will disable the caching of requests no matter what. This setting is useless if you didn't install with `brawling[cache]`, and otherwise is only recommended if you're facing issues because of the cache (such as non-up-to-date responses)

By default, some methods that return a list will attempt to sort it. `force_no_sort` will disable that, and return everything in the exact order as it was received. Note that for now, only `get_battle_log` does any sorting, because the other methods already give out a sorted list. This is undocumented and may change at any time though, but I still decided that I won't add sorting to all the other methods, due to being a potentially useless performance decrease.

## Disclaimer

This content is not affiliated with, endorsed, sponsored, or specifically approved by Supercell and Supercell is not responsible for it. For more information see Supercell’s Fan Content Policy: www.supercell.com/fan-content-policy.