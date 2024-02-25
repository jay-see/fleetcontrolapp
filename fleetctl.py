import time
import datetime
import threading
import requests
import json
import ipaddress

# global variables
currentstate = "" # mode
eventlog = {} # dictionary of dictionaries with IP address as the key of the outer dictionary,
              # and datetime in microseconds as the key of the inner dictionary

# global constant
MAX_MINERS = 256

# base URL of the REST API
base_url = "http://localhost:5000/api"

# This is the primary function that starts the application
def fleetctl():
    base_ip = "none"
    base = "1.1.1."
    # Keep asking how many miners until user input is an integer between 0 and 256
    while True:
        num_miners = input(f"How many miners are there in the fleet ({MAX_MINERS} maximum)? ")

        try:
            if 0 < int(num_miners) <= MAX_MINERS:
                break
            else:
                print("Answer out of range")
        except:
            print("Answer must be an integer")

    # Ask user for a valid base address. Hitting enter will use the default
    while not(is_ip_ending_with_zero(base_ip) | (base_ip == "")):
        base_ip = input(f"Enter base IP address - must end with .0 (default is 1.1.1.0): ").strip()
    # base is base_ip without the '0' at the end
    if base_ip != "":
        base = base_ip[:-1]
    for count in range(int(num_miners)):
        ip = base+str(count)
        print("Logging IP address: "+ip)
        eventlog[ip] = {}
    initFleet()
    startListening()
    # Check the time every 60 seconds and update modes according to schedule
    while True:
        current_time = time.localtime()
        ################################################
        ##### MODIFY THE SCHEDULE BELOW FOR TESTING #####
        ################################################
        if current_time.tm_hour == 0 and current_time.tm_min == 0:
            updateAllMiners("overclock")
        if current_time.tm_hour == 6 and current_time.tm_min == 0:
            updateAllMiners("normal")
        if current_time.tm_hour == 12 and current_time.tm_min == 0:
            updateAllMiners("underclock")
        if current_time.tm_hour == 18 and current_time.tm_min == 0:
            updateAllMiners("curtailed")

        time.sleep(60)  # Sleep for 60 seconds (1 minute) until the next time check

# Create and start the thread for input listener
def startListening():
    input_thread = threading.Thread(target=inputlistener, daemon=True)
    input_thread.start()

# This thread listens for the user's selection, while not affecting 
# the main thread that updates the modes on schedule
def inputlistener():
    while True:
        option = input("Press 'M' for current mode of miners or 'L' for current logs of all miners: ")
        if (option == 'L') | (option == 'l'):
            print(json.dumps(eventlog, indent=4))
        else:
            current_time = datetime.datetime.now()
            print("Current mode:", currentstate, "at", current_time.strftime("%Y-%m-%d %H:%M:%S"))

# Assign the initial mode of the miners based on these buckets
# [0,6) overclock
# [6,12) normal
# [12,18) underclock
# [18,24) curtailed
def initFleet():
    current_time = time.localtime()
    if 0 <= current_time.tm_hour < 6:
        updateAllMiners("overclock")
    if 6 <= current_time.tm_hour < 12:
        updateAllMiners("normal")
    if 12 <= current_time.tm_hour <18:
        updateAllMiners("underclock")
    if 18 <= current_time.tm_hour < 24:
        updateAllMiners("curtailed")

# Since all the IP's are in the eventlog, traverse the eventlog and for each miner IP,
# call the appropriate API endpoints to update the mode
def updateAllMiners(mode):
    global currentstate
    currentstate = mode
    for ip in eventlog:
        token = login(ip)
        if mode == "curtailed":
            setCurtail(ip, token, "sleep")
        else:
            setCurtail(ip, token, "active")
            setProfile(ip, token, mode)
        logout(ip)

# This is the login API POST request
def login(ip):
    eventlog[ip][datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")] = "login"
    data = {
        "miner_ip": ip
    }
    headers = {
        "Content-Type": "application/json"
    }
    # Make a POST request
    response = requests.post(f"{base_url}/login", json=data, headers=headers)

    token = response.json()['token']
    print("Login Response: "+response.json()['message']+" New token: " + token)
    return token

# This is the curtail API POST request
def setCurtail(ip, token, state):
    eventlog[ip][datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")] = "curtail "+state
    data = {
        "token": token,
        "mode": state
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(f"{base_url}/curtail", json=data, headers=headers)
    print("Curtail Response: "+response.json()['message'])

# This is the profileset API POST request 
def setProfile(ip, token, mode):
    eventlog[ip][datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")] = "profileset "+mode
    data = {
        "token": token,
        "profile": mode
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(f"{base_url}/profileset", json=data, headers=headers)
    print("Profileset Response: "+response.json()['message'])

# This is the logout API POST request
def logout(ip):
    eventlog[ip][datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")] = "logout"
    data = {
        "miner_ip": ip
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(f"{base_url}/logout", json=data, headers=headers)
    print("Logout Response: "+response.json()['message'])

# Validate the base IP address input format from the user
def is_ip_ending_with_zero(ip_str):
    try:
        ipaddr = ipaddress.ip_address(ip_str)
        if ipaddr.version == 4:  # Only for IPv4 addresses
            return str(ipaddr).endswith('.0')
        else:
            return False
    except ValueError:
        return False

if __name__ == '__main__':
    fleetctl()

