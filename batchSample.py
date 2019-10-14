import time
import argparse
import os
import re
import json

from argparse import ArgumentParser
from aicsapi_speech_recognition import SpeechRecognitionApi

try:
    import thread
except ImportError:
    import _thread as thread

SAMPLE_RATE = 16000  # pcm file sampling rate, we currently support only 16k
CHUNK_SIZE = 5760  # an optional number of context size in byte when decoding
# a duration for simulating streaming
SLEEP_TIME = CHUNK_SIZE / (SAMPLE_RATE * 2.0)
TIMEOUT = 2  # response timeout (sec)

INPUT = "input_path"
OUTPUT = "output_path"
KEY = "access_key"


def error(inst, err):
    print(err)


def finish(inst, msg, dur, early):
    print('finish[%d][%d] : %s \n' % (dur, early, msg))
    global result
    result = ""
    jsonObj = json.loads(msg)
    for segment in re.split(r'\[|"|,|\]', jsonObj['result']):
        result += segment


def start(inst):
    def run(*args):
        global fullpath
        with open(fullpath, 'rb') as f:
            chunk = f.read(CHUNK_SIZE)
            inst.start(chunk)
            while True:
                time.sleep(SLEEP_TIME)
                chunk = f.read(CHUNK_SIZE)
                if not chunk:
                    break
                inst.send(chunk)
            # send last packet
            inst.stop(TIMEOUT)
    thread.start_new_thread(run, ())


def main(params):
    outputpath = params[OUTPUT]
    scpPath = params[INPUT]
    key = params[KEY]

    with open(scpPath, 'rt') as scp_file:
        with open(outputpath, 'wt') as output_file:
            for line in scp_file:
                global fullpath
                fullpath = os.path.join(os.getcwd(), line.split(' ')[1][:-1])
                api = SpeechRecognitionApi(
                    user_id='testuser-from-aicsapi-python-clientv2',
                    device_id='please-fill-in-device-identity',
                    language='chn',
                    access_key=key
                )

                api.enableDebugLog()
                api.on_error(error)
                api.on_finish(finish)
                api.on_start(start)
                api.connect()
                global result
                transcript = '{} {}\n'.format(line.split(' ')[0], result)
                output_file.write(transcript)


if __name__ == '__main__':
    parser = ArgumentParser(description='Speech Recognition client')
    parser.add_argument('-i', '--input', dest=INPUT, type=str,
                        help='Input scp file path', required=True)
    parser.add_argument('-o', '--output', dest=OUTPUT,
                        type=str, help='Output file path', required=True)
    parser.add_argument('-k', '-access_key', dest=KEY,
                        type=str, help='access key', required=True)

    args = parser.parse_args()
    main(vars(args))
