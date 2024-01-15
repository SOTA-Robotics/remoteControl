
from src.socket_tcp import *
from src.share_variables import *
import time


if __name__ == '__main__':
    global configurations;
    tcp_cl = tcp_client(configurations["host"], configurations["port"]);
    result = tcp_cl.connect_client();
    data = {
        "temperature":[1,2,3,4],
        "conveyor": False,
        "robot": False,
        "start":False,
        "pause": False,
        "stop": False,
    };
    commands = ["start","pause","stop"];
    if result:
        print("Connected to host")
    while result:
        user_input = input("Enter command:Start/Stop/pause: ");
        if(user_input == "Start"):
            data["start"] = True;
        elif user_input == "Stop":
            data["stop"] = True;
        elif user_input == "Pause":
            data["pause"] = True;
        tcp_cl.sent_to_server(data);
        for key in commands:
            data[key] = False;
        # result = tcp_cl.read_from_server();
        # for key in result:
        #     print(key + ": " + str(result[key]));
        time.sleep(0.1);