from flask import Flask, render_template, render_template_string, redirect, url_for, request, Response
import requests
from socket import socket, AF_INET, SOCK_STREAM
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import json
import os

app = Flask(__name__)

# Define the path to the JSON file that will act as a local database
DB_FILE = 'proxies.json'

@app.route('/download_proxies')
def download_proxies():
    proxies = load_proxies()
    proxy_list = '\n'.join([proxy['ip'] for proxy in proxies])
    return Response(proxy_list,
                    mimetype="text/plain",
                    headers={"Content-Disposition": "attachment;filename=proxies.txt"})


def fetch_proxies_api(protocol='all', timeout='10000', country='all', ssl='all', anonymity='all'):
    url = f"https://api.proxyscrape.com/v2/?request=displayproxies&protocol={protocol}&timeout={timeout}&country={country}&ssl={ssl}&anonymity={anonymity}"
    response = requests.get(url)
    if response.status_code == 200:
        proxies = response.text.strip().split('\n')
        # Filter out empty lines if any
        proxies = [proxy for proxy in proxies if proxy]
        return proxies
    else:
        return []


def get_proxy_location(ip):
    print(f'Getting location for IP: {ip}')   
    # Secondary attempt with ipinfo.io
    try:
        #https://ipinfo.io/{ip}/json?token=<yourtoken>
        response = requests.get(f"https://ipinfo.io/{ip}/json", timeout=5)
        print(f'ipinfo.io response: {response.json()}')
        if response.status_code == 200:
            json_response = response.json()
            return json_response.get('country', 'Unknown'), json_response.get('city', 'Unknown')
    except requests.RequestException as e:
        print(f'ipinfo.io request failed for IP {ip}: {e}')

    return 'Unknown', 'Unknown'



def check_proxy_speed(proxy):
    print(f"Checking speed and location for proxy: {proxy}")
    try:
        ip, port = proxy.split(':')
        country, city = get_proxy_location(ip)
        if country == 'Unknown' or city == 'Unknown':
            # If location is unknown, consider this a failure.
            print(f"Location check failed for proxy {proxy}.")
            return None
        start_time = time.time()
        with socket(AF_INET, SOCK_STREAM) as s:
            s.settimeout(5)
            s.connect((ip, int(port)))
            latency = time.time() - start_time
        print(f"Proxy {proxy} responded in {latency} seconds, located in {country}, {city}")
        return {"ip": proxy, "country": country, "city": city, "speed": latency}
    except Exception as e:
        print(f"Proxy {proxy} did not respond: {e}")
        return None




def save_proxies(proxies):
    with open(DB_FILE, 'w') as db_file:
        json.dump(proxies, db_file, indent=4)

def load_proxies():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, 'w') as db_file:
            json.dump([], db_file)  # Initialize the file with an empty list
    with open(DB_FILE, 'r') as db_file:
        return json.load(db_file)

@app.route('/test')
def test():
    return render_template_string('''
        <html>
            <body>
                <table>
                    <tr><td>Test IP</td><td>Test Country</td><td>Test City</td><td>0.123</td></tr>
                </table>
            </body>
        </html>
    ''')


def process_proxies(proxies):
    # Filter out proxies that are 'Unknown' after both checks
    filtered_proxies = [proxy for proxy in proxies if not (proxy['country'] == 'Unknown' and proxy['city'] == 'Unknown')]
    return filtered_proxies

@app.route('/')
def index():
    # Load proxies directly without performing geolocation checks
    proxies = load_proxies()
    return render_template('index.html', proxies=proxies)



@app.route('/refresh', methods=['GET'])
def refresh():
    proxies = load_proxies()
    updated_proxies = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_proxy = {executor.submit(check_proxy_speed, proxy['ip']): proxy for proxy in proxies}

        for future in as_completed(future_to_proxy):
            original_proxy = future_to_proxy[future]
            result = future.result()

            updated_proxy = original_proxy.copy()  # Copy original proxy details
            if result is not None:
                # Speed check successful, update the speed
                updated_proxy['speed'] = result['speed']
            else:
                # Speed check failed, mark the speed as "fail"
                updated_proxy['speed'] = "fail"
                
            updated_proxies.append(updated_proxy)

    save_proxies(updated_proxies)
    return redirect(url_for('index'))






@app.route('/fetch_new')
def fetch_new():
    protocol = request.args.get('protocol', 'all')
    timeout = request.args.get('timeout', '10000')
    country = request.args.get('country', 'all')
    ssl = request.args.get('ssl', 'all')
    anonymity = request.args.get('anonymity', 'all')
    
    new_proxies = fetch_proxies_api(protocol, timeout, country, ssl, anonymity)
    print(f'Fetched {len(new_proxies)} proxies.')

    # Process new proxies to include speed checks
    with ThreadPoolExecutor(max_workers=10) as executor:
        tasks = [executor.submit(check_proxy_speed, proxy) for proxy in new_proxies]
        processed_proxies = [task.result() for task in as_completed(tasks) if task.result() is not None]

    print(f'Processed {len(processed_proxies)} proxies with speed checks.')

    save_proxies(processed_proxies)
    return redirect(url_for('index'))



if __name__ == '__main__':
    app.run(debug=True)
