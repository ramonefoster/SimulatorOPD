import serial
import serial.tools.list_ports
import time

class Comm():
    def __init__(self):        
        self._serial = None
        self.connected = False 
        self.com_port = None   
        self._timeout = 2    
    
    def _ports(self):
        self.list = serial.tools.list_ports.comports()
        coms = []
        for element in self.list:
            coms.append(element.device)

        return(coms)
    
    def connect(self, value):
        if value:
            try:
                if len(self.com_port)>3 and self.com_port in self._ports():
                    print(f"CONNECTED TO {self.com_port}")
                    self._serial = serial.Serial(
                        port=self.com_port,
                        baudrate=9600,                
                        timeout=2,
                    )
                    self._serial.close()
                
            except Exception as e:
                print("Err Connect", e)
            if self._serial and not self._serial.is_open:
                try: 
                    self._serial.open()
                    self.connected = True
                except Exception as e:
                    self.connected = False
        else:
            if self._serial.is_open:
                try:
                    self._reset()
                    self._serial.close()
                    self.connected = False
                except Exception as e:
                    self.connected = False
    
    def _reset(self):
        self._serial.cancel_write()
        self._serial.cancel_read()
        self._serial.reset_output_buffer()
        self._serial.reset_input_buffer()  
        self._serial.flush() 
    
    def write(self, cmd):
        cmd = f"{cmd}\n"
        if self._serial.is_open:
            try:         
                self._serial.write(bytes(cmd, 'utf-8'))
                ack = self._serial.readline().decode('utf-8')
            except Exception as e:
                print("Err write", e)
                return ""
        else:
            return





