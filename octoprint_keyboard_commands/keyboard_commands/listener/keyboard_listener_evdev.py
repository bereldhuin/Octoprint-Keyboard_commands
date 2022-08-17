# Python program raising
# exceptions in a python
# thread

import threading
import ctypes
import time
from evdev import InputDevice, categorize, ecodes, list_devices
from octoprint.events import eventManager
import os


class KeyboardListenerThread(threading.Thread):
    def __init__(self, name, device_path):
        threading.Thread.__init__(self, daemon=True)
        self.name = name
        self.device_path = device_path

    def run(self):
        device = InputDevice(self.device_path)

        key_dict = {}
        # TODO: maybe support 'hold' some day...
        KEY_STATE = ["released", "pressed", "pressed"]
        try:
            for event in device.read_loop():
                if event.type == ecodes.EV_KEY:
                    key_event = categorize(event)

                    key_name = key_event.keycode
                    key_name = key_name.replace("KEY_", "").lower()
                    key_state = KEY_STATE[key_event.keystate]
                    if key_name not in key_dict or key_dict.get(key_name) != key_state:
                        key_dict[key_name] = key_state
                        eventManager().fire("plugin_keyboard_commands_key_event",
                                            dict(key=key_name, key_state=key_state))
        finally:
            # device.ungrab(
            device.close()

    def get_id(self):

        # returns id of the respective thread
        if hasattr(self, '_thread_id'):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                return id

    def stop(self):
        thread_id = self.get_id()
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
                                                         ctypes.py_object(SystemExit))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
            print('Exception raise failure')

    def run_keyboard_listener(self):
        self.listener = KeyboardListenerThread('USB Keyboard Listener Thread')
        self.listener.start()

    def kill_keyboard_listener(self):
        self.listener.stop()
        # self.listener.join(0.1)

    def get_device_info(self):
        message = "Using evdev, additional listener configuration may be needed.\n"
        message += "Currently connected devices:\n"
        options = []

        for device in os.listdir('/dev/input/by-id'):
            message += f" - {device}\n"
            options.append('/dev/input/by-id/' + device)
        return message, options
