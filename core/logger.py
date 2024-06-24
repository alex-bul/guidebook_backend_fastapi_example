import logging
import os
import datetime

if os.getcwd().endswith('core'):
    os.chdir('../sport-backend')

if 'logs' not in os.listdir():
    os.mkdir('logs')

LOGS_COUNT = 5
now_name = 'bot_' + str(datetime.datetime.now()).split('.')[0].replace(':', '.')
logname = f"./logs/{now_name}.log"

logging.basicConfig(level=logging.INFO,
                    format="%(name)-12s: %(asctime)-4s %(levelname)-8s %(message)s [%(threadName)s]",
                    datefmt="%Y-%m-%d %H:%M:%S")

logging.getLogger("requests").setLevel(logging.ERROR)
logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)

# logger = logging.getLogger("uvicorn.error")
# logger.propagate = False

file_handler = logging.FileHandler(filename=logname,
                                   encoding='utf-8', mode='a+')

formatter = logging.Formatter('%(name)-12s: %(asctime)s %(levelname)-8s %(message)s [%(threadName)s]')
file_handler.setFormatter(formatter)
logging.getLogger().addHandler(file_handler)

logger = logging.getLogger('logger')

log_files = sorted(os.listdir('./logs'))

for i in log_files[:LOGS_COUNT * -1]:
    os.remove('./logs/' + i)
