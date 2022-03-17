import csv, sys
from apiRequester import ApiRequester
class WeatherReporter:
    """
    Class used to represent an weather reporter program
    ...

    Attributes
    ----------   
    citiesCoordinates : dict
        Dictionary with city code as key, and a tuple (latitude,longitude) as value
    citiesTemperature : dict
        Dictionary with city code as key, and city current temperature as value
    destinationOriginForFlights : list
        List of lists of the format [origin_city, destination_city], associated to each flight of 
        the input
    numberOfApiCalls : int
        Counter used to keep track of how much calls are made in total 
        to the OpenWeather API
   
    """

    def __init__(self, apiRequester):
        """
        Parameters
        ----------
        apiRequester : ApiRequester
            Api requester object used to fetch the temperature for an specific city
        
        """
        self.apiRequester = apiRequester
        self.citiesCoordinates = {}
        self.citiesTemperature = {}
        self.destinationOriginForFlights = []
        self.numberOfApiCalls = 0


    def readCsv(self, filename):
        """ 
        Extract cities coordinates and flights information from the input csv file
        ...

        Saves the coordinates of each city into the citiesCoordinates dictionary
        with city code as key, and a tuple (latitude, longitude) as value

        Then, adds a list of the format [origin_city, destination_city]
        for each flight corresponding to each row into the destinationOriginForFlights list.

        Parameters
        ----------
        filename : str
            The input csv filename

        Raises
        -------
            FileNotFoundError: If could not found the specified file
            OSError: If an I/O error ocurred when trying to read file

        """   
        try:
            file = open(filename)
        except FileNotFoundError:
                print("File not found")
                sys.exit(1)
        except OSError:
            print(f"Error occurred when trying to open {filename}")
            sys.exit(1)
        else:
            with file:
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
        finally:
            file.close()
    
    def getTemperature(self, cityCode): 
        """ 
        Fetch a city temperature
        
        Set the request url for the apiRequester object,
        using the city latitude and longitude values as parameters,
        then makes the request

        Parameters
        ----------
        cityCode : str
            A 3 characters city code for the city we want to get it's temperature

        Returns
        -------
            A string containing the temperature for this city. 
            N/A if could not fetch temperature value from OpenWeather API
        """       
        temperature = "N/A"
        currCityCoordinates = self.citiesCoordinates[cityCode]
        self.apiRequester.setRequestUrl(currCityCoordinates[0], currCityCoordinates[1])
        responseData = self.apiRequester.makeRequest()
        if responseData != None:
            temperature = responseData['main']['temp']
        return temperature

    def updateTemperatureRecords(self):
        """
        Fetch every city temperature (if this city temperature isn't available) 
        and saves it into the citiesTemperature dictionary used as cache
        
        Also, update the numberOfApiCalls counter on each request to the API. 
        """
        for city in self.citiesCoordinates:
            if city not in self.citiesTemperature:
                self.citiesTemperature[city] = self.getTemperature(city)   
                self.numberOfApiCalls+=1
    
    def writeOutputCsv(self, output):
        """
        To each list [origin_city, destination_city] 
        asocciated with each flight information inside destinationOriginForFlights
        appends the current temperature of both cities obtained from OpenWeather
        
        Finally, writes this modified list of lists, into a csv file

        Raises
        -------
            OSError: If an I/O error ocurred when trying to open file
        """
        for i in range(len(self.destinationOriginForFlights)):
            destinationOriginList = self.destinationOriginForFlights[i]
            destinationOriginList+= [str(self.citiesTemperature[destinationOriginList[0]]) + "°C", str(self.citiesTemperature[destinationOriginList[1]]) + "°C"]
        try:
            with open(output, "w", newline="") as outputCsv:
                writer = csv.writer(outputCsv)
                writer.writerows(self.destinationOriginForFlights)
        except OSError:
            print(f"Error occurred when trying to open {output}")
            sys.exit(1)

def main():
    apiRequester =  ApiRequester()
    weatherReporter = WeatherReporter(apiRequester)
    weatherReporter.readCsv("../data/dataset1.csv") 
    print("Input csv read. Fetching temperature info for each city ...")
    weatherReporter.updateTemperatureRecords()
    print("Number of calls to OperWeather API", weatherReporter.numberOfApiCalls)
    weatherReporter.writeOutputCsv("out.csv")    
    print("Results written in out.csv file in current folder")    

if __name__ == "__main__":
    main()

