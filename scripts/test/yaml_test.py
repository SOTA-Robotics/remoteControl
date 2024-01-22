import yaml
import json

# Step 1: Define the Device Classes
class Smartphone:
    def __init__(self, brand, model):
        self.brand = brand
        self.model = model

class Laptop:
    def __init__(self, brand, processor):
        self.brand = brand
        self.processor = processor

# Step 2: Assuming you have a YAML or JSON file with device specifications
# Example YAML content:
# - type: Smartphone
#   brand: "Apple"
#   model: "iPhone 13"
# - type: Laptop
#   brand: "Dell"
#   processor: "Intel i7"

# Step 3: Read the YAML or JSON File
def read_device_config(file_path):
    with open(file_path, 'r') as file:
        if file_path.endswith('.yaml') or file_path.endswith('.yml'):
            return yaml.safe_load(file)
        else:
            raise ValueError("Unsupported file format")

def print_device_config(name,unit):
    print(f"device is {name} and its slave id is {unit} ")


# Example Usage
if __name__ == '__main__':
    config_path = '../../config/devices.yaml'  # or .json
    device_specs = read_device_config(config_path)
    device = device_specs["port"]
    device = device[0]
    for spec in device:
        #device_type = spec.pop('type')
        #print_device_config(**spec)
        print(spec)


    device_read = device_specs["devices_read"]
    print(device_read)
    for device in device_read:
        print(device)

    config_path = '../../config/package.yaml'  # or .json
    device_specs = read_device_config(config_path)
    print(device_specs)


