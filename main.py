import sys

import requests
import validators
import threading
import time
import random
import json

from PyQt5 import QtWidgets, uic, QtTest
from PyQt5.QtCore import QTimer, QUrl, pyqtSlot
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QMessageBox

from utils.server import FlaskApp
from utils.conversion import Convertion
from utils.coordinates import Coordinates
from telescope import Telescope

from utils.instances import verify_coord_format
from utils.simbad import SimbadQ
from utils.comm import Comm
from screens.setup import SerialPortDialog

from utils.dso import DSO
from server import DisplayFlask


Ui_MainWindow, QtBaseClass = uic.loadUiType("main.ui")

class SimulatorOPD(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self._abort = threading.Event()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer_status()

        self.telescope = Telescope()
        self.telescope_status = {}
        self.thread_telescope = None
        self._disconnect_flag = False

        self.btnPoint.clicked.connect(self.slew)
        self.btnTracking.clicked.connect(self.tracking)
        self.btnAbort.clicked.connect(self.stop)
        self.btnNorth.pressed.connect(lambda: self.telescope.move_axis(0, 10))
        self.btnSouth.pressed.connect(lambda: self.telescope.move_axis(1, 10))
        self.btnEast.pressed.connect(lambda: self.telescope.move_axis(2, 10))
        self.btnWest.pressed.connect(lambda: self.telescope.move_axis(3, 10))
        self.btnNorth.released.connect(self.telescope.stop_move_axis)
        self.btnSouth.released.connect(self.telescope.stop_move_axis)
        self.btnEast.released.connect(self.telescope.stop_move_axis)
        self.btnWest.released.connect(self.telescope.stop_move_axis)

        self.btnRandom.clicked.connect(self.start_random)

        self.comboBox.currentIndexChanged.connect(self.change_telescope)

        self.btnGetImage.released.connect(self.get_image)
        self.btnSimbad.clicked.connect(self.from_simbad)

        self.WebSimbad.loadStarted.connect(self.loadStartedHandler)
        self.WebSimbad.loadProgress.connect(self.loadProgressHandler)
        self.WebSimbad.loadFinished.connect(self.loadFinishedHandler)

        self.btnSetup.clicked.connect(self.setup)
        self.comm = Comm()
        self.com_port = None

        self.random = False
        self.dsos = DSO

        self.connect_telescope()
        self.change_telescope()

        server_thread = threading.Thread(target=self.start_server)
        server_thread.daemon = True  # Set the thread as a daemon to stop it when the main thread exits
        server_thread.start()

        displays_thread = threading.Thread(target=self.start_displays)
        displays_thread.daemon = True  # Set the thread as a daemon to stop it when the main thread exits
        displays_thread.start()

        url = QUrl(f'http://127.0.0.1:5500/aladin')
        self.WebSimbad.load(url)
            
    def setup(self):
        # Open the dialog
        dialog = SerialPortDialog()
        dialog.port_selected.connect(self.handle_port_selection)
        dialog.exec_()
    
    def handle_port_selection(self, port):
        # Slot that updates the label with the selected port
        self.com_port = port
        print(f"Port selected: {port}")
        self.connect_comm(port)

    def connect_comm(self, port):
        if "COM" in port:
            try:
                if self.comm.connected:
                    self.comm.connected(False)
                    time.sleep(1)
                self.comm.com_port = port
                self.comm.connect(True)
                serial_thread = threading.Thread(target=self.start_comm)
                serial_thread.daemon = True  # Set the thread as a daemon to stop it when the main thread exits
                serial_thread.start()
            except Exception as e:
                print(e)
        
    def start_comm(self):
        while self.comm.connected:
            data = {
                'ra': round(self.telescope_status["right ascension"],4),
                'ha': round(self.telescope_status["hour angle"],4),
                'dec': round(self.telescope_status["declination"],4),
            } 
            json_data = json.dumps(data)  # Convert the dictionary to a JSON string
            self.comm.write(json_data)
            time.sleep(.8)

    def start_random(self):  
        self.random = not self.random

        if self.random:
            self.statRandom.setStyleSheet("background-color: lightgreen;\nborder-radius: 15px;")
            self.btnRandom.setText("STOP")
            self.random_obj()
        else:
            self.statRandom.setStyleSheet("background-color: indianred;\nborder-radius: 15px;")
            self.btnRandom.setText("START")       
        

    def change_telescope(self):
        """load outlet page"""
        if self.comboBox.currentIndex() == 0:
            url = QUrl("http://127.0.0.1:5500/")
        else:
            url = QUrl("http://127.0.0.1:5500/iag")

        if url.isValid():
            try:
                self.web160.load(url)
            except Exception as e:
                print(e)
    
    @pyqtSlot()
    def loadStartedHandler(self):
        pass

    @pyqtSlot(int)
    def loadProgressHandler(self, prog):
        self.progressBar.setValue(prog)

    @pyqtSlot()
    def loadFinishedHandler(self):
        pass
    
    def from_simbad(self, id = None):
        if id:
            ra, dec = SimbadQ.get_radec((id))
        else:
            ra, dec = SimbadQ.get_radec((self.txtSimbadID.text()).upper())

        if ra and dec:
            self.txtTargetRA.setText(ra)
            self.txtTargetDEC.setText(dec)

        return ra, dec
    
    def random_obj(self):
        latitude = "-22 32 04"
        t0 = time.time()

        id = random.randint(1, len(self.dsos)-1)

        current_obj = self.txtSimbadID.text()
        alt = 0
        while alt < 20:
            if time.time()-t0 > 10:
                print("TIMEOUT")
                break
            id = random.randint(1, len(self.dsos)-1)
            obj = self.dsos[id]
            if obj == current_obj:
                continue
            ra, dec = self.from_simbad(id=obj)
            if not ra or not dec:
                continue
            sidereal = self.telescope_status["sidereal"]           
            ha = Convertion.ra_to_ah(ra, sidereal)
            alt, az = Coordinates.get_elevation_azimuth(ha, dec, latitude)
        
        self.txtSimbadID.setText(obj)
        self.slew()
        QtTest.QTest.qWait(1500)
        while self.telescope_status["slewing"]:
            QtTest.QTest.qWait(500)
        self.get_image(target=obj)

    def update(self):
        if int(time.time() % 40) == 0:
            if self.random:
                if self.telescope_status["slewing"]:
                    self.stop()
                self.random_obj()

        if self.random:
            self.statRandom.setStyleSheet("background-color: lightgreen;\nborder-radius: 15px;")
            self.btnRandom.setText("STOP")
        else:
            self.statRandom.setStyleSheet("background-color: indianred;\nborder-radius: 15px;")
            self.btnRandom.setText("START")

        if self.telescope_status.get("connected"):
            if self.telescope_status["elevation"] <= 0 and self.telescope_status["tracking"]:
                self.stop()            

            self.telescope_stat_ui()

    def telescope_stat_ui(self):
        if self.telescope_status.get("connected"):
            self.statTeleConn.setStyleSheet("background-color: lightgreen;\nborder-radius: 15px;")
        else:
            self.statTeleConn.setStyleSheet("background-color: indianred;\nborder-radius: 15px;")
        self.txtCoordRA.setText(Convertion.hours_to_hms(self.telescope_status["right ascension"], decimal_digits=2))
        self.txtCoordDEC.setText(Convertion.degrees_to_dms(self.telescope_status["declination"]))
        self.txtCoordLST.setText(Convertion.hours_to_hms(self.telescope_status["sidereal"], decimal_digits=2))
        self.txtCoordTimeLimit.setText(Convertion.hours_to_hms(self.telescope_status["time limit"]))
        self.txtCoordElevation.setText(str(round(self.telescope_status["elevation"], 2)))
        self.txtCoordAzimuth.setText(str(round(self.telescope_status["azimuth"], 2)))
        self.txtCoordHA.setText(Convertion.hours_to_hms(self.telescope_status["hour angle"], decimal_digits=2))

        if self.telescope_status["slewing"]:
            self.statTeleSlew.setStyleSheet("background-color: lightgreen;\nborder-radius: 15px;")
        else:
            self.statTeleSlew.setStyleSheet("background-color: indianred;\nborder-radius: 15px;")

        if self.telescope_status["tracking"]:       
            self.statTeleTrack.setStyleSheet("background-color: lightgreen;\nborder-radius: 15px;")
            self.btnTracking.setText("ON")
            self.btnTracking.setStyleSheet("background-color: lightgreen;\nborder-radius: 15px;")
        else:
            self.statTeleTrack.setStyleSheet("background-color: indianred;\nborder-radius: 15px;")
            self.btnTracking.setText("OFF")
            self.btnTracking.setStyleSheet("background-color: indianred;\nborder-radius: 15px;")           
    
    def start_displays(self):
        try:
            DisplayFlask.run(host="127.0.0.1", port=5500)
        except Exception as e: 
            print("ALADIN OFF: ", e)

    def start_server(self):
        try:
            FlaskApp.run(host="127.0.0.1", port=5000)
            print("SERVER ONLINE")
        except Exception as e: 
            print("SERVER OFF: ", e)
    
    def get_image(self, ra=None, dec=None, target=None):
        if not ra or not dec:
            ra = self.telescope_status["ra"]
            dec = self.telescope_status["dec"]

        if self.telescope_status.get("connected") and self.telescope_status:
            try:
                if target:
                    requests.post(f"http://127.0.0.1:5500/aladin/set_target", json={'target': target, 'fov': 0.5})
                else:
                    requests.post(f"http://127.0.0.1:5500/aladin/set_target", json={'target': ra + dec, 'fov': 0.5})
                # url = QUrl(f'https://aladin.cds.unistra.fr/AladinLite/?target={ra.replace(" ", "%20")}{(dec.replace("+", "%2B"))}&fov=0.50&survey=CDS%2FP%2FDSS2%2Fcolor')
                # self.WebSimbad.load(url)
            except Exception as e:
                print("error", e)

    def tracking(self):        
        """turn on or off sidereal movement"""
        if self.telescope_status:
            if self.telescope_status["tracking"]:
                self.telescope.set_track(False)
            else:
                self.telescope.set_track(True)   
    
    def update_telescope_position(self):
        data = {
            'tag': 0,
            'hour_angle': self.telescope_status["hour angle"],
            'declination': self.telescope_status["declination"],
            'azimuth': self.telescope_status["azimuth"],
            'elevation': self.telescope_status["elevation"],
            'tracking': self.telescope_status["tracking"],
        }        
        url = f"http://127.0.0.1"
        if validators.url(url):
            try:
                response = requests.post(f"{url.rstrip('/')}:5000/api/telescope/position", json=data)
            except Exception as e:
                print(e)
    
    def move_axis(self, axis):
        """move telescope slightly
        :param axis: int (0: North, 1: South, 2: East, 3: West)"""
        if self.telescope:
            try:
                self.telescope.move_axis(axis, 10)
            except Exception as e:
                print(e)

    def stop(self):
        self.random = False
        self.btnAbort.setEnabled(False)
        QTimer.singleShot(3000, lambda: self.btnAbort.setDisabled(False))
        """stops any movement (dome and telescope)"""
        self._abort.set()  
        if self.telescope_status.get("connected"):            
            self.telescope.abort_slew()
            if self.telescope_status["tracking"]:
                self.telescope.set_track(False)
        
    def slew(self):
        """Points the telescope to a given Target"""
        self.btnPoint.setEnabled(False)
        QTimer.singleShot(1000, lambda: self.btnPoint.setDisabled(False)) 
        
        self.statTeleSlew.setStyleSheet("background-color: lightgreen;\nborder-radius: 15px;")
        self._abort.clear()
        
        if not verify_coord_format(self.txtTargetRA.text()) or not verify_coord_format(self.txtTargetDEC.text()):
            self.showDialog("RA e/ou DEC inválidos.")
        elif self.telescope_status.get("connected"):            
            ra = Convertion.hms_to_hours(self.txtTargetRA.text())
            dec = Convertion.dms_to_degrees(self.txtTargetDEC.text()) 
            sidereal = self.telescope_status["sidereal"]           
            ha = Convertion.ra_to_ah(ra, sidereal)
            latitude = "-22 32 04"
           
            try:                
                elevation, azimuth = Coordinates.get_elevation_azimuth(ha, self.txtTargetDEC.text(), latitude)
                if elevation > 0 and elevation<=90:                    
                    self.telescope.set_track(True)
                    self.telescope.slew_async(ra, dec)
                else:
                    self.showDialog("Objeto abaixo da linha do horizonte.")
            except Exception as e:
                print("Error poiting: " +str(e))
                self.statTeleSlew.setStyleSheet("background-color: indianred")
    
    def timer_status(self):
        self.timer.start(150)

    def showDialog(self, msgError):
        """
        Display a message box showing a warning or information message.
        Parameters:
            msgError (str): The message to be displayed in the message box.
        """
        msgBox = QtWidgets.QMessageBox()
        msgBox.setIcon(QtWidgets.QMessageBox.Information)
        msgBox.setText(msgError)
        msgBox.setWindowTitle("Warning")
        msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msgBox.exec()

    def update_telescope_status(self):
        while self._disconnect_flag:
            time.sleep(.75)

            self.telescope_status = self.telescope.get_position()
            self.update_telescope_position()    

    def connect_telescope(self):
        self.telescope.connect()
        self._disconnect_flag = True
        
        if self.thread_telescope == None:
            self.thread_telescope = threading.Thread(name="TELESCOPE", target = self.update_telescope_status)
            self.thread_telescope.daemon = True
            self.thread_telescope.start()

    def disconnect_telescope(self):
        if self.telescope_status.get("connected"):
            self.stop()
            self._disconnect_flag = False
            if self.thread_telescope != None:
                self.thread_telescope.join()
            self.thread_telescope = None
        
        self.telescope.disconnect()


    def closeEvent(self, event):
        """
        Event handler for closing the application.

        The function displays a message box asking the user to confirm if they want to close the application.
        If the user confirms, it disconnects all connections, terminates specific processes, and accepts the event to close the application.
        If the user cancels, it ignores the event and keeps the application running.

        Parameters:
            event (QCloseEvent): The close event triggered when the application is closed.
        """
        close = QMessageBox()
        close.setText("Tem certeza que deseja sair?")
        close.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        close = close.exec()

        if close == QMessageBox.Yes: 
            self._abort.set()        
            self.telescope.disconnect()
            event.accept()
        else:
            event.ignore()

if __name__ == "__main__":
    main_app = QtWidgets.QApplication(sys.argv)
    window = SimulatorOPD()

    window.show()
    sys.exit(main_app.exec_())


