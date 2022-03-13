from configparser import ConfigParser
import csv, json
from urllib import parse, request
OPENWEATHER_API_URL = "http://api.openweathermap.org/data/2.5/weather"
class WebService:
    def __init__(self) -> None:
        # Dictionary with city code as key and (latitude,longitude) as value
        self.citiesCoordinates = {}
        # Dictionary with city code as key and city current temperature as value
        self.citiesTemperature = {}
        # List with lists [origin_city, destination_city] associated to each flight
        self.destinationOriginForFlights = []
        self.numberOfApiCalls = 0

    '''Get API key from keys.ini file'''
    def getApiKey(self):
        configParser = ConfigParser()
        configParser.read("keys.ini")
        return configParser["openweather"]["api_key"]
    """Build an url for the OpenWeather api call with the latitude and longitude parameters"""
    def buildOpenWeatherUrl(self, latitude, longitude):
        api_key = self.getApiKey()
        units = "metric"
        url = (f"{OPENWEATHER_API_URL}?lat={latitude}"
            f"&lon={longitude}&units={units}&appid={api_key}")
        return url

    """Make a request to OpenWeather with the query built for a particular latitude and longitude"""
    def makeRequest(self, queryUrl):
        responseData = request.urlopen(queryUrl).read()
        return json.loads(responseData)

    '''Read CSV and import the origin and destination coordinates into
        a dictionary with city code as key and (latitude, longitude) as value
        Also sets the destinationOriginForFlights list, with information for the destination and origin cities for 
        the flight on each row'''
    def readCsv(self, filename):    
        file = open(filename)
        csvreader = csv.reader(file)   
        next(csvreader, None)
        for row in csvreader:
            for i in range(2):
                currCity = row[i]
                if currCity not in self.citiesCoordinates:
                    currCityLatitude = row[(i * 2) + 2] 
                    currCityLongitude = row[(i * 2) + 3]
                    self.citiesCoordinates[currCity] = (currCityLatitude, currCityLongitude)
            self.destinationOriginForFlights.append([row[0], row[1]])
        file.close()

    """ Fetch a city temperature by building a query using it's latitude and longitude values as parameters"""
    def getTemperature(self, city):        
        currCityCoordinates = self.citiesCoordinates[city]
        responseData = self.makeRequest(self.buildOpenWeatherUrl(currCityCoordinates[0], currCityCoordinates[1]))            
        return responseData['main']['temp']

    " Get every city temperature and saves it into the self.citiesTemperature dictionary "
    def updateTemperatureRecords(self):
        for city in self.citiesCoordinates:
            # Avoid making duplicate queries if temperature is already available
            if city not in self.citiesTemperature:
                self.citiesTemperature[city] = self.getTemperature(city)   
                self.numberOfApiCalls+=1
    """For each lists asocciated with one flight row adds the current temperature of both cities
        Then writes this modified list into a csv file """
    def writeOutputCsv(self, output):
        for i in range(len(self.destinationOriginForFlights)):
            destinationOriginList = self.destinationOriginForFlights[i]
            destinationOriginList+= [str(self.citiesTemperature[destinationOriginList[0]]) + "°C", str(self.citiesTemperature[destinationOriginList[1]]) + "°C"]
        with open(output, "w", newline="") as outputCsv:
            writer = csv.writer(outputCsv)
            writer.writerows(self.destinationOriginForFlights)
            
def main():
    webService = WebService()
    webService.readCsv("../data/dataset1.csv")    
    webService.updateTemperatureRecords()
    print("Number of API calls", webService.numberOfApiCalls)    
    webService.writeOutputCsv("out.csv")    

if __name__ == "__main__":
    main()


