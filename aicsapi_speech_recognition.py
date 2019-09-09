import sys
import websocket
import io
import json
import base64
import gzip
import logging
import time
import threading
UTF8 = 'utf-8'


class SpeechRecognitionApi:
    EVENT_START = 'start'
    EVENT_FINISH = 'finish'
    EVENT_CLOSE = 'close'
    EVENT_ERROR = 'error'
    TIMEOUT = 2
    logger = None
    logger_handler = None

    def __init__(self
                , user_id=None
                , device_id=None
                , language='chn'
                , access_key=None):
        """Constructor of SpeechRecognitionApi

        Keyword Arguments:
            user_id {string} -- [user identity, e.g. aaaa-bbbb-cccc-dddd] (default: {None})
            device_id {string} -- [device identity] (default: {None})
            language {string} -- [preferred language. Speech service only support chn(chinese) now] (default: {'chn'})
            access_key {string} -- [access key for speech service] (default: {None})

        Raises:
            ValueError: [required parameter is not assigned]
        """
        self.callbacks = {}
        self.log = self.getLogger()
        self.uri = 'wss://aicsapi-speech-generic.southeastasia.cloudapp.azure.com/v1/speech/recognition/conversation/cognitiveservices'

        if not user_id:
            raise ValueError('user_id must be assigned')
        self.user_id = user_id

        if not device_id:
            raise ValueError('device_id must be assigned')
        self.device_id = device_id

        if not language:
            raise ValueError('language must be assigned')
        self.language = language

        if not access_key:
            raise ValueError('access_key must be assigned')
        self.access_key = access_key

        self.log.debug('Constructor arguments parsed')

    @staticmethod
    def getLogger():
        """This function initilize logging system
        """
        if not SpeechRecognitionApi.logger:
            logging.Formatter.converter = time.gmtime
            log = logging.getLogger('AICS')
            log.setLevel(logging.DEBUG)
            handler = logging.StreamHandler(sys.stdout)
            handler.setLevel(logging.ERROR)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            log.addHandler(handler)
            SpeechRecognitionApi.logger = log
            SpeechRecognitionApi.logger_handler = handler
        return SpeechRecognitionApi.logger

    @staticmethod
    def set_log_level(level):
        SpeechRecognitionApi.logger_handler.setLevel(level)

    def on_start(self, callback):
        self.on(self.EVENT_START, callback)

    def on_finish(self, callback):
        self.on(self.EVENT_FINISH, callback)

    def on_error(self, callback):
        self.on(self.EVENT_ERROR, callback)

    def on_close(self, callback):
        self.on(self.EVENT_CLOSE, callback)

    def on(self, event_name, callback):
        """registration of callback functions

        Arguments:
            event_name {string} -- one of ['start', 'finish', 'close', 'error']
            callback {function} -- user-defined callback function
        """
        if event_name not in self.callbacks:
            self.callbacks[event_name] = [callback]
        else:
            self.callbacks[event_name].append(callback)

    def trigger(self, event_name, *args):
        """Trigger callback function by event_name

        Arguments:
            event_name {string} -- one of ['start', 'finish', 'close', 'error']
        """
        self.log.debug('trigger event: %s' % event_name)
        if event_name in self.callbacks:
            for callback in self.callbacks[event_name]:
                callback(self, *args)

    def _gzip_in_mem(self, target):
        out = io.BytesIO()

        with gzip.GzipFile(fileobj=out, mode='w') as fo:
            fo.write(target)

        return out.getvalue()

    def _pack_meta(self, meta):
        return json.dumps(meta).encode(UTF8)

    def _send(self, data):
        self.ws.send(self._gzip_in_mem(data), opcode=websocket.ABNF.OPCODE_BINARY)

    def _on_start(self):
        self.trigger(self.EVENT_START)

    def _on_message(self, message):
        """Callable which is called when websocket received data
        """
        end = int(time.time() * 1000)
        self.trigger(self.EVENT_FINISH, message, (end - self.begin), (end - self.early))
        
    def _on_error(self, error):
        """Callable which is called when websocket get error
        """
        print("on_error" + error)

    def _on_close(self, code, reason):
        """Callable which is called when websocket closed the connection
        """
        print("### closed code : " + str(code) + " , reason : " + str(reason) + " ###")

    def connect(self):
        """Connect to speech recognition endpoint with authentication header.
        access key will be embedded into websocket header.
        """
        try:
            self.log.debug('connect to websocket server')
            websocket.enableTrace(False)
            websocket.setdefaulttimeout(2)
            self.ws = websocket.WebSocketApp(self.uri,header=['Ocp-Apim-Subscription-Key: %s' % self.access_key],
                                on_message = self._on_message,
                                on_error = self._on_error,
                                on_close = self._on_close)
            self.ws.on_open = self._on_start
            self.ws.run_forever()
        except Exception as err:
            self.trigger(self.EVENT_ERROR, err)

    def start(self, data):
        """Send configuration packet containing
        * user_id
        * device_id
        * language
        * sample rate (able to customize in the future)
        * first chunk of audio buffer

        Arguments:
            data {arraybuffer} -- audio buffer
        """
        try:
            self.log.debug('send config')

            meta = {
                'deviceid': 'this_is_device_id',
                'streaming': 1,
                'spk': self.user_id,
                'end': '0'
            }
            packedMetaData = self._pack_meta(meta)
            self._send(packedMetaData)
            self._send(data)
        except Exception as err:
            self.trigger(self.EVENT_ERROR, err)

    def send(self, data):
        """send audio buffer

        Arguments:
            data {arraybuffer} -- audio buffer
        """
        try:
            self.log.debug('send audio buffer')
            self._send(data)
        except Exception as err:
            self.trigger(self.EVENT_ERROR, err)

    def stop(self, timeout=TIMEOUT):
        """last packet indicate speech ends
        """
        try:
            self.log.debug('send end signal')
            self.early = int(time.time() * 1000)
            self._send(bytes())
            self.begin = int(time.time() * 1000)
        except Exception as err:
            self.trigger(self.EVENT_ERROR, err)
        finally:
            exit_flag = threading.Event()
            if not exit_flag.wait(timeout=timeout) and self.ws.sock is not None:
                self.log.debug('force close socket')
                self.close()

    def close(self):
        """close websocket connection and clear resources
        """
        try:
            self.ws.close()
            self.trigger(self.EVENT_CLOSE)
        except Exception as err:
            self.trigger(self.EVENT_ERROR, err)

    def is_running(self):
        """determine websocket connection is still alive or not

        Returns:
            boolean -- websocket connection is alive
        """
        return self.ws.connected

    def enableDebugLog(self):
        """Enable debug log
        """
        self.set_log_level(logging.DEBUG)
