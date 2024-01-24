import platform
def get_os():
    os_name = platform.system()
    if os_name == 'Windows':
        return "Windows"
    elif os_name == 'Linux':
        return "Linux"
    else:
        return "Unknown"

if __name__ == '__main__':
    current_os = get_os()
    print(f"The code is running on {current_os}")