from pathlib import Path
import brawling

token = (Path(__file__).parent.parent / ".token").read_text()
client = brawling.Client(token, proxy=True)
log = client.get_battle_log("#UC8L2YC0")
print(len(log), log)
