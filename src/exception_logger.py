import logging
import re
import json
from datetime import datetime
import yaml

'''
logging system written here
Initially 
'''


def load_configuration(filename):
    """
    Load configuration from yaml or json file based on filepath
    :param filename: path of a file
    :return: return decoded
    """
    with open(filename, 'r') as file:
        # lines = file.readlines()
        # if lines:
        #     for line in lines:
        #         loaded_config += line
        #     loaded_config = loaded_config.rstrip('\n')
        #     result = json.loads(loaded_config)
        # return result
        if filename.endswith('.yaml') or filename.endswith('.yml'):
            return yaml.safe_load(file)
        elif filename.endswith('.json'):
            return json.load(file)
        else:
            raise Exception(f'loading configuration file:{filename} failure')


class LoggingSystem:
    """
    a class to manage log file
    """
    def __init__(self, logger_name, filename, level=logging.ERROR):
        self.logger_name = logger_name
        self.logger = logging.getLogger(logger_name)
        file_handler = logging.FileHandler(filename)
        file_handler.setLevel(level)
        self.logger.addHandler(file_handler)
        self.filename = filename

    def log_json_information(self, date, time,
                             error_code: list, debug_condition: bool):
        """
        record a logging information
        :param date:
        :param time:
        :param error_code: list of error_code
        :param debug_condition: record a condition indicating whether error is solved or not;False isnt solved True: solved
        :return:
        """
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
        """
        :return: read the latest json information from log file
        """
        decoded_data = None
        with open(self.filename, 'r') as file:
            log_data = file.readlines()
            if log_data:
                log_data = log_data[-1]
                json_string = log_data.split(f"ERROR:{self.logger_name}:")[-1].strip()
                decoded_data = json.loads(json_string)

        return decoded_data

    def debug_finished(self):
        """
        rewrite the log file and change the debug condition as True
        :return:
        """
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
