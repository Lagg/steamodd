import steam, sys

valid_modes = ["bp", "schema", "assets-catalog"]

try:
    testmode = sys.argv[2]
    testkey = sys.argv[1]
    if testmode not in valid_modes: raise Exception
except:
    sys.stderr.write("Run " + sys.argv[0] + " <apikey> " + "<" + ", ".join(valid_modes) + ">\n")
    raise SystemExit

steam.set_api_key(testkey)

test_schema = steam.tf2.item_schema(lang = "en")

def print_item_list(items):
    for item in items:
        print("\n\x1b[1m" + str(item) + "\x1b[0m\n")
        for attr in item:
            print attr

if testmode == "bp":
    test_pack = steam.tf2.backpack("stragglerastic", schema = test_schema)
    print_item_list(test_pack)
elif testmode == "schema":
    print_item_list(test_schema)
elif testmode == "assets-catalog":
    assets = steam.tf2.assets(currency = "usd")
    for item in test_schema:
        try:
            print("\x1b[1m" + str(item) + "\x1b[0m:\t $" + str(assets[item]))
        except KeyError:
            pass
