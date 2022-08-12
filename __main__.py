from jade import JadeEngine
import importlib, readline, sys, os

APP_PATH = os.path.dirname(os.path.realpath(__file__))+"/"
sys.path.append(APP_PATH)
sys.path.append(APP_PATH+"libraries/")

j = JadeEngine()

def internal_cmd(cmd, line):
    match cmd:
        case "build":
            f = importlib.import_module(f"builders.{line}")
            f.build(j)
            print(f"Built {line}")
            j.save_state(save_dir = APP_PATH+"states/")

if j.config.get("autorun", []):
    for command in j.config["autorun"]:
        if command.startswith("."):
            cmd = command[1:]
            line = " ".join(cmd.split(" ")[1:])
            cmd = cmd.split(" ")[0]
            internal_cmd(cmd, line)
        else:
            success = j.readln(command)
            if success:
                for item in j.buffer:
                    print(item["sender"]+': '+item['line'])
                j.clear_buffer()

while True:
    l = input("> ")

    if l.startswith("."):
        cmd = l[1:]
        line = " ".join(cmd.split(" ")[1:])
        cmd = cmd.split(" ")[0]
        internal_cmd(cmd, line)
    else:
        if j.get_meta("game_id", "") == "" and not l.startswith("load "):
            print("No state loaded.")
        else:
            success = j.readln(l)
            
            if success:
                for item in j.buffer:
                    print(item["sender"]+': '+item['line'])
                j.clear_buffer()
            else:
                print("What?")
