[![Tests](https://img.shields.io/badge/Tests-Passing-success)](https://github.com/Astosi/data_enricher/actions)
# Data Enrichment App 

The Data Enrichment Application is a robust, production-ready Python-based software solution designed to facilitate and automate data enrichment. 

Leveraging the power of Python, the application takes a raw dataset in CSV format and carries out enrichment by fetching additional data from an external API -Gleif API. The 'lei' field from each row in the input dataset is utilized to query the API, and the 'country', 'legalName', and 'bic' fields from the API response are appended to each input row, enriching the dataset. Moreover, the application conducts specific calculations to introduce a new 'transaction_costs' field to the output dataset based on country transition policies. 

## Design
Adhering to the SOLID principles, the project was designed with extensibility, maintainability, and scalability in mind. Each class has a single responsibility and interfaces like IClient, IDataParser, IDataValidator, and ICache were created to allow easy extension and segregation of functionalities. The system's architecture respects the Dependency Inversion Principle, ensuring a flexible structure where high-level modules are not directly dependent on low-level ones. Leveraging Python and essential packages such as aiohttp, multiprocessing, and pandas, a robust data enrichment application capable of efficiently handling HTTP requests, parsing responses, validating, and caching data was developed.

## Environment and Packages
The Python development environment was configured with the necessary packages to ensure efficient and effective project development. These include:
- `aiohttp`: This package was chosen to enable asynchronous HTTP requests. The asynchronous nature of the requests allows the application to handle multiple operations concurrently, which can lead to significant improvements in performance and responsiveness, especially when working with a large amount of data or making numerous API calls.
- `multiprocessing`: This library was chosen to facilitate parallel computing. This is particularly useful in situations where you want to maximize CPU utilization and speed up processing time, as is the case in data-intensive applications. 
- `pandas`: This is one of the most widely used data processing libraries in Python. It provides robust and high-performing data manipulation capabilities, making it an excellent choice for handling the dataset in this project.

## Components
The project comprises components such as;
* `Data parser`: Parses the data from API responses into a specific format.,
* `Data validator`: Validates the input and output data, 
* `Data source`: Handles the loading and saving of data, 
* `Data enricher`: Uses an API client to fetch and parse data, and then enriches the input data., 
* `Transaction calculator`: Calculates the custom transaction costs based on the business logic.,

Each component performs distinct roles, from parsing API responses, validating data, fetching and parsing data, to carrying out specific calculations.


### Data Enricher
I implemented DataEnricher, a class that enriches a given DataFrame with additional data from the Gleif API(For LEI lookup). This class takes an IClient and IDataParser, illustrating dependency injection principles.
```bash
class DataEnricher:
    def __init__(self, client: IClient, data_parser: IDataParser):
    self.client = client
    self.data_parser = data_parser
```

### Client
The client class, in this case, LeiLookupClient, is used for fetching data from the Gleif API using LEI filter. This class is a derivative of the IClient interface, and it implements methods to fetch data, adhere to rate limiting, and handle retry attempts in case of failed requests. The client also integrates a caching mechanism to store previously fetched data, improving the application's efficiency. Different APIs or request methods can be applied following interface structure.
```
class IClient(ABC):
    @abstractmethod
    async def fetch(self, id_: str) -> Optional[str]:
        pass
```



```bash
 def __init__(self, cache: ICache = LeiLookupCache(100), sleep_rate: float = 0.6, retry_attempts: int = 3):
        """
        :param cache: An instance of the cache to store fetched data. Default is LeiLookupCache with a cache size of 100.
        :param sleep_rate: The rate at which to pause between requests to adhere to rate limiting. Default is 0.6 seconds.
        :param retry_attempts: The number of retry attempts in case of failed requests. Default is 3 attempts.
        """
        self.session = None
        self.cache = cache
        self.base_url = 'https://api.gleif.org/api/v1/lei-records?filter[lei]='
        self.rate_limit_pause = sleep_rate
        self.retry_attempts = retry_attempts

    async def fetch(self, id_: str) -> Optional[str]:
```



### Multiprocessing for Calculations
In the calculate function, I used the multiprocessing library to parallelize the calculation formula applied to each row in the DataFrame. This allowed us to leverage multiple CPU cores to speed up computation.
```bash
df[column_name] = pool.map(formula.apply, [row for _, row in df.iterrows()])
```

### Caching Mechanism
This cache implementation is quite simple but efficient for scenarios where repeated requests for the same data occur, and the data source is slow or expensive to access (like an API call). It can significantly speed up the program by serving repeated requests directly from the cache, reducing the need for additional API calls. To avoid overusage of memory I set a casche size.
```bash
    def add(self, key, value):
        if len(self.cache) >= self.cache_size:
            self.cache.popitem(last=False)
        self.cache[key] = value
```

### Custom Logger
Another important part of the project was the implementation of a custom logging system. This logger was designed to provide granular control over what gets logged and where. It's implemented using the singleton design pattern via the LoggerSingleton class, which ensures that only a single instance of the logger exists throughout the application. This is useful as it prevents the creation of duplicate loggers and provides a single point of access to the logger.
```bash
class LoggerSingleton:
    __instance: 'LoggerSingleton' = None
    __log_level: int = DEFAULT_LOGGING_LEVEL
    __log_dir: str = DEFAULT_LOG_DIR

    @classmethod
    def get_instance(cls) -> 'LoggerSingleton':
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance

    def __init__(self) -> None:
        self.loggers = {}
```

### Unit Testing
Alongside development, I also wrote unit tests (pytest) to ensure the functionality of each component and maintain high code quality. It also includes integration testing to ensure the endpoint is still available when the code runs.


### Automated Testing
Alongside the robust application design, Git Actions were implemented as a critical part of the project infrastructure. This continuous integration/continuous deployment (CI/CD) tool ensured that the codebase remained clean, stable, and deployable at any point in time.

## Usage
Once the repository is cloned, and the required packages are installed, the application can be executed using:

```bash
python main.py --client LeiLookupClient --cache_size 100 --sleep_rate 0.6 --retry_attempts 3 --log_level INFO --input_file data/input_dataset.csv --output_file data/output_data.csv
```
### Environment Variables
Before running the data_enricher project, it's crucial to set up the environment variables properly in the .env file.

* `ROOT_DIR` : This defines the root directory for the project.
* `LOG_DIR` : This specifies the directory where log files will be stored.

You can also use command-line arguments to customize the behavior of the script (they all have default values so it's not obligatory):

    --client: The client used to fetch data from the API. The default is LeiLookupClient.
    --cache_size: The size of the cache. The default is 100.
    --sleep_rate: The rate at which to pause between requests to adhere to rate limiting. The default is 0.6 seconds.
    --retry_attempts: The number of retry attempts in case of failed requests. The default is 3.
    --log_level: The level of logging. The default is INFO.
    --input_file: The path to the input file. The default is data/input_dataset.csv.
    --output_file: The path to the output file. The default is data/output_data.csv.

## Tests
To ensure that the components function as expected, unit tests were created using pytest. To run the tests, use:
```bash
pytest tests/
```
