import steam, sys

def print_item_list(items):
    for item in items:
        print("\n\x1b[1m" + str(item) + "\x1b[0m\n")
        for attr in item:
            print attr

def bp_test():
    test_pack = steamodd_game_module.backpack("stragglerastic", schema = test_schema)
    print_item_list(test_pack)

def schema_test():
    print_item_list(test_schema)

def assets_test():
    assets = steamodd_game_module.assets(currency = "usd")
    for item in test_schema:
        try:
            print("\x1b[1m" + (str(item) + "\x1b[0m: ").ljust(50) + (str(assets[item])).ljust(50))
        except KeyError:
            pass

def gw_test():
    import time
    wrenches = steamodd_game_module.golden_wrench()

    for wrench in wrenches:
        print("Verifying wrench #{0}, crafted {1}".format(wrench.get_craft_number(), time.strftime("%Y-%m-%d %H:%M:%S", wrench.get_craft_date())))
        try:
            owner = steam.user.profile(wrench.get_owner())
            ownerbp = steamodd_game_module.backpack(owner)
            wrenchpresent = False
            print(owner.get_persona().encode("utf-8"))
            for item in ownerbp:
                if item.get_id() == wrench.get_id():
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

steamodd_game_module = None

try:
    mod = "tf2"
    testmode = sys.argv[2]
    testkey = sys.argv[1]

    moded = testmode.split('-')
    if len(moded) > 1:
        mod = moded[1]
        testmode = moded[0]

    tests[testmode]
    steamodd_game_module = getattr(steam, mod)
except:
    sys.stderr.write("Run " + sys.argv[0] + " <apikey> " + "<" + "-<mode>, ".join(tests) + "-<mode>>\n")
    raise SystemExit

steam.set_api_key(testkey)

test_schema = steamodd_game_module.item_schema(lang = "en")

try:
    tests[testmode]()
except KeyError:
    sys.stderr.write(testmode + " is not a valid name, need one of " + ", ".join(tests) + "\n")
