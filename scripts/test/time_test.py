from datetime import datetime
import time
if __name__ == '__main__':
    pre = datetime.now()
    time.sleep(3)
    cur = datetime.now()
    print((cur-pre).total_seconds())