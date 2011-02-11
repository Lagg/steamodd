import steam

steam.set_api_key("D89B2C0025F1F31EF51575D3FBC50965")

test = steam.tf2.item_schema(lang = "en")

testpack = steam.tf2.backpack("stragglerastic", schema = test)

for item in testpack:
    print("\n\x1b[1m" + str(item) + "\x1b[0m\n")
    for attr in item:
        print attr
