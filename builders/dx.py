def test(**args):
    print("testy", args)

def playertick(**args):
    print("Player ticked!")

def build(jade):
    jade.set_meta("game_id", "deusex")
    jade.set_meta("game_name", "Deus Ex: Momento Mori")
    jade.set_meta("author", "Technomancer")

    jade.functions["test"] = test
    jade.functions["player_tick"] = playertick
    jade.on("bork", "test")

    jade.trigger_first("bork", name = "Kai")

    jade.create("zone", "docks", name="Docks", description="The UNATCO Island docks.")
    jade.create("zone", "under_docks", name="Under the Docks", description="Underwater.")
    jade.link_zones("docks", "down", "under_docks")
    jade.new_actor("jcd")
    jade.focus("jcd")
    jade.move_actor("jcd", "docks")
    jade.hook("jcd", "tick", "player_tick")
    #print("---")
    #for key, ob in jade.all_objects.items():
        #print("object", ob)

