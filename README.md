# Brawling

Synchronous API wrapper for Brawl Stars made by Supercell

## Installation

```
pip install brawling
```

To install with caching support (for performance, optional)

```
pip install brawling[cache]
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

# Prints "Battle(battle_time=...)"
print(battle_log[0])
```

For some endpoints, there's also a possibility to page over them:

```py
# Returns a generator which fetches up to 45 total pages
# of Ukrainian rankings for Shelly, each page
# being a list of BrawlerRanking model where 0 < len(page) <= 10
pages = client.page_brawler_rankings(
    brawling.BrawlerID.SHELLY,
    per_page=10, region='ua', max=450
)

# ^ Note that this operation was immediate,
# as no data is fetched yet.

# This will now fetch pages of 10 players,
# until either there are no players left,
# or we reach the max limit of 450.
for page in pages:
    print(page)
```

If you don't want to handle exceptions, want to use a dynamic IP address, or force disable caching, there are three additional options in the Client constructor:

```py
client = Client(TOKEN, proxy=True, strict_errors=False, force_no_cache=True)
```

With `strict_errors` set to False, the API methods can now silently fail instead of raising exceptions, and instead return an `ErrorResponse` object. It's your job to handle it.

The `proxy` argument will use a [3rd party proxy](https://docs.royaleapi.com/#/proxy). Details on setting up are on the linked page. DISCLAIMER: I am not responsible for anything related to the proxy. I am not in any way related to its developers, and it's not my fault if your API access gets blocked because of using it.

`force_no_cache` will disable the caching of requests no matter what. This setting is useless if you didn't install with `brawling[cache]`, and otherwise is only recommended if you're facing issues because of the cache (such as non-up-to-date responses)

## Disclaimer

This content is not affiliated with, endorsed, sponsored, or specifically approved by Supercell and Supercell is not responsible for it. For more information see Supercell’s Fan Content Policy: www.supercell.com/fan-content-policy.