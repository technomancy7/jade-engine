import readline

class JTemplates:
    def _directions(self):
        return [
            "north", "east", "west", "south",
            "up", "down", "in", "out"
        ]

    def invert_direction(self, d):
        match d:
            case "north":
                return "south"
            
            case "south":
                return "north"

            case "east":
                return "west"

            case "west":
                return "east"

            case "up":
                return "down"

            case "down":
                return "up"

            case "in":
                return "out"
            
            case "out":
                return "in"

    def _actor(self, **args):
        o = {
            "id": "", 
            "name": "DEFAULT_NAME", 
            "description": "DEFAULT_DESCRIPTION", 
            "contains": [], 
            "location": "",
            "type": "actor",
            "events": {}
        }
        o.update(**args)
        return o

    def _zone(self, **args):
        o = {
            "id": "", 
            "name": "DEFAULT_NAME", 
            "description": "DEFAULT_DESCRIPTION", 
            "contains": [], 
            "type": "zone",
            "exits": {},
            "events": {}
        }

        for d in self._directions():
            o["exits"][d] = {
                "target": "",
                "locked": False,
                "events": {
                    "on_exit": [], 
                    "on_exit_failed": []
                }
            }

        o.update(**args)
        return o

class JEventing:
    def __init__(self):
        # str -> str : events that would be called by the system automatically, points to a function
        self.events = {}

        super().__init__()

    def tick(self):
        turns = self.get_var("_turns", 0) + 1
        self.set_var("_turns", turns)

        self.trigger_all("tick")

        for obj in self.all_objects:
            if obj["events"].get("tick", None) != None:
                for evt in obj["events"]["tick"]:
                    self.run(evt, target = obj, source = "tick")

    def on(self, event_name, function_name):
        if self.events.get(event_name, None) == None:
            self.events[event_name] = []

        self.events[event_name].append(function_name)

    def trigger_first(self, event, **args):
        if self.events.get(event, None) != None and len(self.events[event]) > 0:
            self.run(self.events[event][0], **args)

    def trigger_last(self, event, **args):
        if self.events.get(event, None) != None and len(self.events[event]) > 0:
            self.run(self.events[event][-1], **args)

    def trigger_any(self, event, **args):
        import random

        if self.events.get(event, None) != None and len(self.events[event]) > 0:
            self.run(random.choice(self.events[event]), **args)

    def trigger_all(self, event, **args):
        if self.events.get(event, None) != None and len(self.events[event]) > 0:
            for evt in self.events[event]:
                self.run(evt, **args)

class JActions:
    def readln(self, line):
        act = line.split(" ")[0]
        ln = " ".join(line.split(" ")[1:])
        return self.run_action(act, ln)

    def run_action(self, name, line):
        if self.actions.get(name):
            self.actions[name](engine = self, line = line)
            return True
        return False

    def _say(self, **args):
        self.writeln(sender = "Player", line = args.get("line"))

    def __init__(self):
        # str -> str : actions the player takes, points to a function
        self.actions = {}

        self.actions["say"] = self._say
        super().__init__()

class JFunc:
    def _echo(self, jade, str):
        print(str)
    
    def run(self, fn_name, **args):
        if self.functions.get(fn_name) != None:
            self.functions[fn_name](**args)

    def __init__(self):
        # str -> fn : functions that game scripting can call
        self.functions = {}

        self.functions["echo"] = self._echo
        super().__init__()

class JObjectManager:
    def __init__(self):
        self.all_objects = {}
        super().__init__()

    def create(self, jtype, id, **keys):
        if jtype == "actor":
            keys["id"] = id
            act = self._actor(**keys)
            self.all_objects[id] = act
            return self.all_objects[id]

        if jtype == "zone":
            keys["id"] = id
            act = self._zone(**keys)
            self.all_objects[id] = act
            return self.all_objects[id]


    def get_object(self, id, filter_type = None):
        for key, ob in self.all_objects.items():
            if ob["id"] == id:
                if filter_type != None:
                    if filter_type == ob["type"]:
                        return ob
                    else: continue
                else:
                    return ob
        return id

    def move_actor(self, id, new_zone):
        ob = self.get_object(id, "actor")
        target = self.get_object(new_zone)
        if ob["location"] != "":
            old_zone = self.get_object(ob["location"])
            old_zone["contains"].remove(id)
        
        target["contains"].append(id)
        ob["location"] = new_zone

    def walk(self, direction):
        print(self.player_id(), self.get_object(self.player_id()))
        self.walk_actor(self.player_id(), direction)

    def walk_actor(self, id, direction):
        ob = self.get_object(id, "actor")
        cz = self.get_object(ob["location"])
        nz = cz["exits"][direction]["target"]

        self.move_actor(id, nz)

    def player_id(self):
        return self.get_meta("player")

    def focus(self, object_id = ""):
        if object_id == "":
            return self.get_object(self.get_meta("player"))
            
        self.set_meta("player", object_id)

    def player_location(self):
        return self.get_object(self.focus()["location"])

    def current(self):
        return self.focus(), self.player_location()

    def link_zones(self, z1, direction, z2):
        if direction in self._directions():
            z1 = self.get_object(z1, "zone")
            z2 = self.get_object(z2, "zone")

            z1["exits"][direction]["target"] = z2["id"]
            z2["exits"][self.invert_direction(direction)]["target"] = z1["id"]

    # Shortcuts for creating each type
    def new_zone(self, id, **keys):
        return self.create("zone", id, **keys)

    def new_actor(self, id, **keys):
        return self.create("actor", id, **keys)  

class JSaveStateManager:
    def __init__(self):
        self.game_id = ""
        super().__init__()

    def save_state(self, path):
        import json
        with open(path, "w+") as f:
            d = {
                "variables": self.variables,
                "actions": self.actions,
                "events": self.events,
                "meta": self.meta
            }
            json.dump(d, f)

    def load_state(self, path):
        import json
        with open(path, "r") as f:
            data = json.load(f)
            self.variables = data.get("variables", {})
            self.actions = data.get("actions", {})
            self.events = data.get("events", {})
            self.meta = data.get("meta", {})

            # make it get extensions from meta to load files to load the functions

class JadeEngine(JFunc, JActions, JEventing, JObjectManager, JTemplates, JSaveStateManager):
    def __init__(self):
        # str -> str : story details
        self.meta = {}

        # str -> any
        self.variables = {}

        self.buffer = []

        super().__init__()

    def writeln(self, **args): 
        ob = {"sender": "World", "line": ""}
        ob.update(**args)
        self.buffer.append(ob)

    def clear_buffer(self):
        self.buffer.clear()

    def set_var(self, key, value):
        self.variables[key] = value

    def get_var(self, key, default = None):
        return self.variables.get(key, default)

    def set_meta(self, key, value):
        self.meta[key] = value

    def get_meta(self, key, default = None):
        return self.meta.get(key, default)
