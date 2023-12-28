import logging
import re
import json
from datetime import datetime

'''
reg way to extract information
'''
# def decode_logging_information():
#     log_data = ["2023-01-08 19:45:00 - ERROR - This is an error message"];
#     log_pattern = re.compile(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} - \w+ - (.*)');
#     for line in log_data:
#         match = log_pattern.match(line);
#         print(line);
#         if match:
#             message = match.group(1);
#             print(f"Extracted Message :{message}")
#         else:
#             print("No match")


'''
json format to log the informaiton
'''
# def write_read_json_logging_information():
#     # json_data_1 = {"key1": "value1", "key2": 42};
#     # json_data_2 = {"key1":["apple","banana"]};
#     # file_path = 'json_log.log'
#     # logging.basicConfig(filename=file_path, level=logging.INFO);
#     # logger = logging.getLogger("test_logger");
#     # json_data = json.dumps(json_data_1)
#     # print(json_data)
#     # logger.error(f"{json_data}");
#     with open('json_log.log','r') as file:
#         log_data = file.readlines();
#     log_data = log_data[-1];
#     json_string = log_data.split("ERROR:test_logger:")[-1].strip();
#     decoded_data = json.loads(json_string);
#
#     print("Decoded Data :", decoded_data);
#     print(decoded_data["key1"]);
#     print(decoded_data["key2"]);
#
#
#
# '''
# write logging information in a log file
# '''
#
# def write_logging_information():
#     log_format = ('');
#     logging.basicConfig(filename = 'my_log_file.log',level=logging.INFO, format=log_format);
#     logger = logging.getLogger();
#
#     logger.error("This is an error")
#
#
# '''
# read the latest new line in the logging file
# '''
# def read_latest_logging_information():
#     log_file_path = "my_log_file"
#     with open(log_file_path,'r') as file:
#         lines = file.readlines();
#
#     if lines:
#         last_line = lines[-1];
#         print("last line in the log file:",last_line);
#     else:
#         print("log file is empty or does not exist")

'''
logging system written here
Initially 
'''
def load_configuration():
    '''

    :return:
    '''
    merged_config = {}
    loaded_config = ""
    filename = "package.json"
    with open(filename, 'r') as file:
        lines = file.readlines()
        if lines:
            for line in lines:
                loaded_config += line
            loaded_config = loaded_config.rstrip('\n')
            result = json.loads(loaded_config)
    return result


class LoggingSystem():
    def __init__(self, logger_name, filename, level=logging.ERROR):
        self.logger_name = logger_name
        self.logger = logging.getLogger(logger_name)
        file_handler = logging.FileHandler(filename)
        file_handler.setLevel(level)
        self.logger.addHandler(file_handler)
        self.filename = filename

    def log_json_information(self, date, time,
                             error_code: list, debug_condition: bool):
        my_json_format = {
            "date": date,
            "time": time,
            "error_code": error_code,  # list of error code
            "debug_condition": debug_condition,
            "mark_condition": False
        }
        json_data = json.dumps(my_json_format)
        self.logger.error(json_data)

    def read_json_information(self):
        decoded_data = None
        with open(self.filename, 'r') as file:
            log_data = file.readlines()
            if log_data:
                log_data = log_data[-1]
                json_string = log_data.split(f"ERROR:{self.logger_name}:")[-1].strip()
                decoded_data = json.loads(json_string)

        return decoded_data;

    def debug_finished(self):
        with open(self.filename, 'r+') as file:
            lines = file.readlines()
            if lines:
                last_line_start = file.tell() - len(lines[-1])
                result = self.read_json_information()
                file.seek(last_line_start)
                file.truncate()
                result["debug_condition"] = True
                self.log_json_information(date=result["date"], time=result["time"],
                                          error_code=result["error_code"],
                                          debug_condition=result["debug_condition"])

    # def mark_finish(self):
    #     with open(self.filename,'r+') as file:
    #         lines = file.readlines();
    #         if lines:
    #             last_line_start = file.tell()-len(lines[-1]);
    #             result = self.read_json_information();
    #             file.seek(last_line_start);
    #             file.truncate();
    #             result["mark_condition"] = True;
    #             self.log_json_information(date = result["date"],time = result["time"],
    #                                       error_code = result["error_code"],
    #                                       debug_condition = result["debug_condition"]);

    def delete_all_newlines(self):
        with open(self.filename) as file:
            content = file.read()
        content_without_newlines = content.replace('\n', '')
        with open(self.filename, 'w+') as file:
            file.write(content_without_newlines)
