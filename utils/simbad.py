from astroquery.simbad import Simbad

from utils.conversion import Convertion

from astropy.coordinates import SkyCoord
from astropy import units as u

class SimbadQ():
    @staticmethod
    def get_radec(id):
        """Input: Simbad ID
        Return ra (hours), dec (degrees)"""
        identifier = id  
        try:

            result_table = Simbad.query_object(identifier)

            ra = result_table["RA"][0]
            dec = result_table["DEC"][0]

            # ra = Convertion.hms_to_hours(ra)
            # dec = Convertion.dms_to_degrees(dec)
        except:
            ra = None 
            dec = None
        return(ra, dec)
    





