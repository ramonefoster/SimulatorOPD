from utils.conversion import Convertion
from utils.coordinates import Coordinates
import win32com.client

class Telescope():  
    def __init__(self):        
        self._telescope = None
        self.connected = False
        self.coord = {}

    def connect(self):  
        try:
            self._telescope = win32com.client.Dispatch("ASCOM.Simulator.Telescope")            
            self._telescope.Connected = True
            self.set_site("-22 32 04", "-45:34:57", 1864)            
            self.connected = True
            self.get_position() 
            return self._telescope.Name
        except Exception as e:
            self.connected = False
            print("Error connecting Telescope: "+str(e))
            return "Error. Check Telescope LOG." 
    
    def disconnect(self):
        if self.connected:
            self.connected = False
            self._telescope.Connected = False
    
    def set_site(self, latitude, longitude, altitude):
        if self.connected:
            self._telescope.SiteLatitude = Convertion.dms_to_degrees(latitude)
            self._telescope.SiteLongitude = Convertion.dms_to_degrees(longitude)
            self._telescope.SiteElevation = altitude
    
    def get_position(self):
        if self.connected:
            ha = Convertion.ra_to_ah(self._telescope.RightAscension, self._telescope.SiderealTime)
            self.coord = {
                "right ascension" : self._telescope.RightAscension,
                "declination" : self._telescope.Declination,
                "sidereal" : self._telescope.SiderealTime,
                "hour angle": ha,
                "time limit" : Coordinates.get_observing_time(ha),
                "airmass": Coordinates.get_airmass(self._telescope.Altitude),
                "latitude": self._telescope.SiteLatitude,
                "longitude": self._telescope.SiteLongitude,
                "altitude": self._telescope.SiteElevation,
                "utc" : self._telescope.UTCDate,
                "tracking" : self._telescope.Tracking,
                "elevation" : self._telescope.Altitude,
                "azimuth" : self._telescope.Azimuth,
                "at park" : self._telescope.AtPark,
                "at home" : self._telescope.AtHome,
                "slewing" : self._telescope.Slewing,
                "can slew" : self._telescope.CanSlewAsync,
                "can home" : self._telescope.CanFindHome,
                "can slew_altaz" : self._telescope.CanSlewAltAzAsync,
                "can park" : self._telescope.CanPark,
                "can move ra": False,
                "can move dec": False
            }   
            return self.coord  
        else:
            return None               
    
    def abort_slew(self):
        if self.connected:
            if not self._telescope.AtPark and self._telescope.Slewing:
                self._telescope.AbortSlew()
    
    def slew_async(self, ra, dec):
        if self.connected:
            if not self._telescope.AtPark:
                if self._telescope.CanSlewAsync:
                    self._telescope.Tracking = True
                    self._telescope.SlewToCoordinatesAsync(ra, dec)  
    
    def pulse_guide(self, axis, rate):
        if self.connected:
            if self._telescope.CanPulseGuide:            
                self._telescope.PulseGuide(axis, rate*1000)

    def send_home(self):
        if self.connected:
            if self._telescope.CanFindHome:                
                self._telescope.FindHome()
                self._telescope.Tracking = False

    def find_home_thread(self):
        self._telescope.FindHome
        self._telescope.Tracking = False
        
    def set_track(self, state):
        if self.connected:
            try:
                if state and self._telescope.CanSetTracking:
                    self._telescope.Tracking = True
                elif not state and self._telescope.CanSetTracking:
                    self._telescope.Tracking = False
                return True
            except Exception as e:
                print("Error Tracking: "+str(e))
                return False
    
    def sync(self, ra, dec):
        if self.connected:
            if self._telescope.CanSync:                   
                self._telescope.SyncToCoordinates(ra, dec)
    
    def disconnect(self):
        if self.connected:  
            self._telescope.Connected = False
    
    def stop_move_axis(self):
        if self.connected:
            try:
                for i in range(4):
                    self.pulse_guide(i, 0)                
            except Exception as e:
                print("Error Stopping Axis: "+str(e))

    def move_axis(self, axis, rate):
        """move telescope slightly
        :param axis: int (0: North, 1: South, 2: East, 3: West)"""
        if self.connected:
            try:
                self.pulse_guide(axis, rate)
            except Exception as e:
                print("Error Moving Axis: "+str(e))
            
    
