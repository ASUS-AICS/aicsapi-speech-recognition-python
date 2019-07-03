# aicsapi-speech-recognition-python
This project consists of a python client that interacts with the AICS speech recognition service through its WebSockets interface. The client streams audio to the AICS speech recognition service and receives recognition result in real time. You can get free trial subscription keys from the [Speech Recognition Services subscription](https://aicsapi.asus.com/) page.

## Installation
In order to interact with the AICS speech recognition service via WebSockets, it is necessary to install pip, then run the following commands:

`
pip install -r requirements.txt
`

## Examples
`
python sample.py -k <access_token>
`
