def test(**args):
    print("testy", args)

def build(jade):
    print(jade)

    jade.functions["test"] = test
    jade.on("bork", "test")

    jade.trigger_first("bork", name = "Kai")

    jade.create("zone", "docks", name="Docks", description="The UNATCO Island docks.")
    jade.create("zone", "under_docks", name="Under the Docks", description="Underwater.")
    jade.link_zones("docks", "down", "under_docks")
    jade.new_actor("jcd")
    jade.focus("jcd")
    jade.move_actor("jcd", "docks")
    jade.walk("down")
    print("---")
    for key, ob in jade.all_objects.items():
        print("object", ob)

