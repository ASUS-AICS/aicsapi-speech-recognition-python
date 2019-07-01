import time
from types import NoneType
from argparse import ArgumentParser
from aicsapi_speech_recognition import SpeechRecognitionApi

try:
    import thread
except ImportError:
    import _thread as thread

SAMPLE_RATE = 16000
CHUNK_SIZE = 5760
SLEEP_TIME = CHUNK_SIZE / (SAMPLE_RATE * 2.0)

def error(inst, err):
    print(err)


def finish(inst, msg, dur, early):
    print('finish[%d][%d] : %s \n' % (dur, early, msg.decode('utf-8')))


def start(inst):
    def run(*args):
        with open('test.pcm', 'rb') as f:
            chunk = f.read(CHUNK_SIZE)
            
            while (not isinstance(inst.ws.sock, NoneType)) and (not inst.ws.sock.connected):
                pass
            inst.start(chunk)
            while True:
                time.sleep(SLEEP_TIME)
                chunk = f.read(CHUNK_SIZE)
                if not chunk:
                    break
                inst.send(chunk)
            # send last packet
            inst.stop()
    thread.start_new_thread(run, ())

if __name__ == "__main__":
    parser = ArgumentParser(description='Speech Recognition client')
    parser.add_argument("-k", "--key", help="speech server access key", dest="access_key", required=True)
    args = parser.parse_args()

    api = SpeechRecognitionApi(
        user_id='testuser-from-aicsapi-python-clientv1',
        device_id='please-fill-in-device-identity',
        language='chn',
        access_key = args.access_key
    )

    api.enableDebugLog()
    api.on_error(error)
    api.on_finish(finish)
    api.on_start(start)
    api.connect()
