import jade
import importlib, readline
j = jade.JadeEngine()
f = importlib.import_module("builders.dx")
print(f)
f.build(j)

while True:
    l = input("> ")
    success = j.readln(l)
    
    if success:
        for item in j.buffer:
            print(item["sender"]+': '+item['line'])
        j.clear_buffer()
    else:
        print("What?")
