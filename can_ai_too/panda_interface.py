import usb.core
import usb.util
import threading
import time
import struct

class PandaInterface:
    def __init__(self):
        self.dev = None
        self.running = False
        self.listeners = []
        self.log = []

    def connect(self):
        self.dev = usb.core.find(idVendor=0xbbaa, idProduct=0xddcc)
        if self.dev is None:
            raise Exception("Panda not found")

        self.dev.set_configuration()
        print("✅ Panda connected")

    def start(self):
        self.running = True
        threading.Thread(target=self._read_loop, daemon=True).start()

    def stop(self):
        self.running = False

    def _read_loop(self):
        while self.running:
            try:
                data = self.dev.read(1, 0x40, timeout=100)

                for i in range(0, len(data), 16):
                    frame = data[i:i+16]

                    addr = struct.unpack("I", frame[0:4])[0] >> 21
                    bus = (frame[1] >> 4) & 0xF
                    dat = frame[8:16]

                    msg = {
                        "id": addr,
                        "bus": bus,
                        "data": dat,
                        "ts": time.time()
                    }

                    self.log.append(msg)

                    for cb in self.listeners:
                        cb(msg)

            except Exception:
                pass

    def clear_log(self):
        self.log = []

    def get_log(self):
        return self.log
