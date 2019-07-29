# AICS API - Speech Recognition in Python
This project consists of a python client that interacts with the AICS speech recognition service through its WebSockets interface. The client streams audio to the AICS speech recognition service and receives recognition result in real time. 

## Setup

In order to interact with the AICS speech recognition service via WebSockets, it is necessary to install python, pip and use requirements.txt to install all dependencies in our python project

* Install [Python](https://www.python.org/downloads/)

* Install Pip
    - Download [get-pip.py](https://bootstrap.pypa.io/get-pip.py) to a folder on your computer.
    - Open a command prompt and navigate to the folder containing get-pip.py.
    - Run the following command:
        
        `$ python get-pip.py`

    - Pip is now installed!

* Install [virtualenv](https://virtualenv.pypa.io/) if you do not already have them.
* Create a virtualenv. Samples are compatible with Python 2.7 and 3.4+.

    `
    $ virtualenv env
    `

    `
    $ source env/bin/activate
    `

* Clone python-docs-samples and change directory to the sample directory you want to use.

    `
    $ git clone https://github.com/ASUS-AICS/aicsapi-speech-recognition-python.git
    `

* Run the following commands to install the dependencies :

    `
    $ pip install -r requirements.txt
    `

## Quickstart
To run this sample:

`
$ python sample.py -k <access_token>
`

### Set audio path
You can set audio path that you wish to transcribe in `start()`

```python
def start(inst):
    def run(*args):
        with open('test.pcm', 'rb') as f:
            chunk = f.read(CHUNK_SIZE)
            inst.start(chunk)
            while True:
                time.sleep(SLEEP_TIME)
                chunk = f.read(CHUNK_SIZE)
                if not chunk:
                    break
                inst.send(chunk)
            # send last packet
            inst.stop(1)
    thread.start_new_thread(run, ())
```
Please note that this audio is a mono recording with a sample rate of **16000 (16 KHz)** and a bit resolution of 16 bits.

### Get recognition result
After send last audio chunk, you can get recognition result in `finish()` 

```python
def finish(inst, msg, dur, early):
    print('finish[%d][%d] : %s \n' % (dur, early, msg.decode('utf-8')))
```

### Get an API key
You can get subscription keys from the [Speech Recognition Services subscription](https://aicsapi.asus.com/) page.