# ProxyScrapeScraper
```
# Flask Proxy Fetcher and Checker

A Flask-based application designed to fetch, process, and check the speed of proxies from the ProxyScrape API, allowing users to filter proxies based on protocol, timeout, country, SSL support, and anonymity level. This application provides a user-friendly interface for fetching new proxies, refreshing proxy speeds, and downloading the processed proxy list.

## Features

- Fetch proxies dynamically based on user-defined criteria (protocol, timeout, country, SSL, anonymity).
- Check the speed and location of fetched proxies.
- Filter out proxies with unknown locations or that fail speed checks.
- Download the list of processed proxies as a text file.

## Installation

To set up this project locally, follow these steps:

1. Clone the repository:
```bash
git clone https://github.com/yourusername/flask-proxy-fetcher-checker.git
```

2. Navigate to the project directory:
```bash
cd flask-proxy-fetcher-checker
```

3. Install the required Python packages:
```bash
pip install -r requirements.txt
```

## Usage

To run the application:

```bash
python app.py
```

Navigate to `http://localhost:5000` in your web browser to access the application interface.

### Fetching New Proxies

1. Use the form on the homepage to specify your proxy criteria.
2. Click "Fetch Proxies" to retrieve proxies based on your criteria.

### Refreshing Proxy Speeds

- Click "Refresh Proxies" to update the speed information for the currently loaded proxies.

### Downloading Proxies

- Click "Download Proxies" to download the list of processed proxies as a `.txt` file.

## Contributing

Contributions to improve the application are welcome. Before contributing, please create an issue to discuss your ideas or choose an existing issue to work on. For major changes, please open an issue first to discuss what you would like to change.

Ensure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)
```

