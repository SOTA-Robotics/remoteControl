from src.socket_tcp import *
import time
from src.exception_logger import *
import threading


def input_with_timeout(inputstr: str, timeout):
    print(f"You have {timeout} seconds to respond...")
    input_result = []

    def get_input():
        input_result.append(input(inputstr))

    input_thread = threading.Thread(target=get_input)
    input_thread.start()

    input_thread.join(timeout)
    if input_thread.is_alive():
        print("Time is up!")
    else:
        print(input_result)
        return input_result


if __name__ == '__main__':
    config_path = '../../config/socket_config.yaml'
    configs = load_configuration(config_path)
    configs_tcp = configs["tcp"][0]
    tcp_cl = tcp_client(configs_tcp["host"], configs_tcp["port"])
    result = tcp_cl.connect_server()
    print(result)
    data = {
        "temperature": [1, 2, 3, 4],
        "conveyor": True,
        "robot": True,
        "start": False,
        "pause": False,
        "stop": False,
    }

    commands = ["start", "pause", "stop"]
    if result:
        print("Connected to host")
    while result:
        # user_input = input_with_timeout("Enter command:Start/Stop/Pause: ",3)
        # user_input = input("Enter command:Start/Stop/Pause: ")
        # print(user_input)
        # if user_input == "Start":
        #     data["start"] = True
        # elif user_input == "Stop":
        #     data["stop"] = True
        # elif user_input == "Pause":
        #     data["pause"] = True
        # elif user_input == "conveyor":
        #     data["conveyor"] = not data["conveyor"]
        # elif user_input == "robot":
        #     data["robot"] = not data["robot"]
        tcp_cl.sent_to_server(data)
        for key in commands:
            data[key] = False
        # result = tcp_cl.read_from_server();
        # for key in result:
        #     print(key + ": " + str(result[key]));
        time.sleep(0.1)
