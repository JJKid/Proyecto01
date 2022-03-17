from configparser import ConfigParser
import json, sys
from urllib import request
from urllib.error import HTTPError
OPENWEATHER_API_URL = "http://api.openweathermap.org/data/2.5/weather"
class ApiRequester:
    """
    Class to represent an API requester object

    This object is used to make a request to OpenWeather API using a
    defined request url
    ...

    Attributes
    ----------
    requestUrl : str
        a url to make a request to OpenWeather API
    apiKey : str
        the key for OpenWeather API
    
    Methods
    -------
    getApiKey(sound=None)
        Return the api key contained in the keys.ini file

    """
    def __init__(self):            
        self.requestUrl = None
        self.apiKey = self.getApiKey();

    def getApiKey(self):        
        """ 
        Get API key from keys.ini file
        
        Raises
        -------
            KeyError: If could not locate api_key variable on .ini file
            
        Returns
        -------
            A string with apikey contained in the keys.ini file
        """
        configParser = ConfigParser()
        try:
            configParser.read("keys.ini")
            return configParser["openweather"]["api_key"]
        except KeyError:
            print("File doesn´t exist or api_key variable is not in file")
            sys.exit(1)
        
    def setRequestUrl(self, latitude, longitude):  
        """
        Build an url for the OpenWeather api call with the latitude and longitude parameters
        and set it to the requestUrl attribute of the class
        """      
        units = "metric"
        self.requestUrl = (f"{OPENWEATHER_API_URL}?lat={latitude}"
            f"&lon={longitude}&units={units}&appid={self.apiKey}")
    
    def makeRequest(self):   
        """
        Make a request to OpenWeather with the query built for
        a particular latitude and longitude

        Raises
        -------
            HTTPError: HTTP response status code if request was not succesful
        Returns
        -------
            A dictionary with OpenWeather API request response. Where each key is an attribute
             related to the requested city weather
        """ 
        try:             
            responseData = request.urlopen(self.requestUrl).read()
            return json.loads(responseData)
        except HTTPError as err:
            print(err.code)        
            

       

