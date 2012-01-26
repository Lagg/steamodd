import steam, sys

def print_item_list(items):
    for item in items:
        print("\n\x1b[1m" + str(item) + "\x1b[0m\n")
        for attr in item:
            print attr

def bp_test():
    test_pack = steam.tf2.backpack("stragglerastic", schema = test_schema)
    print_item_list(test_pack)

def schema_test():
    print_item_list(test_schema)

def assets_test():
    assets = steam.tf2.assets(currency = "usd")
    for item in test_schema:
        try:
            print("\x1b[1m" + str(item) + "\x1b[0m:\t $" + str(assets[item]))
        except KeyError:
            pass

def gw_test():
    import time
    wrenches = steam.tf2.golden_wrench()

    for wrench in sorted(wrenches.get_wrenches(), key = wrenches.get_craft_number):
        print("Verifying wrench #{0}, crafted {1}".format(wrenches.get_craft_number(wrench), time.strftime("%Y-%m-%d %H:%M:%S", wrenches.get_craft_date(wrench))))
        try:
            owner = steam.user.profile(wrenches.get_owner(wrench))
            ownerbp = steam.tf2.backpack(owner)
            wrenchpresent = False
            print(owner.get_persona().encode("utf-8"))
            for item in ownerbp:
                if item.get_id() == wrenches.get_id(wrench):
                    wrenchpresent = True
                    print_item_list([item])
                    print('')
                    break

            if not wrenchpresent:
                print("\x1b[1mWrench missing\x1b[0m")
        except steam.items.Error as E:
            print(str(E))

tests = {"bp": bp_test,
         "schema": schema_test,
         "assets-catalog": assets_test,
         "golden-wrenches": gw_test}

try:
    testmode = sys.argv[2]
    testkey = sys.argv[1]
    tests[testmode]
except:
    sys.stderr.write("Run " + sys.argv[0] + " <apikey> " + "<" + ", ".join(tests) + ">\n")
    raise SystemExit

steam.set_api_key(testkey)

test_schema = steam.tf2.item_schema(lang = "en")

try:
    tests[testmode]()
except KeyError:
    sys.stderr.write(testmode + " is not a valid name, need one of " + ", ".join(tests) + "\n")
