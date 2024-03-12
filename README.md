# Miner Control Application


## ASSUMPTIONS: 
1 - There are maximum 256 miners in the fleet, each with distinct IP addresses incrementing from a BASE IP address that ends in .0
Example: 123.45.67.0 is a valid BASE IP but 123.45.67.10 is not.  
2 - The default BASE IP address is 1.1.1.0  
Example: If there are 7 miners in the fleet, and the default BASE IP address is used, then their IP addresses must be:  
* 1.1.1.0  
* 1.1.1.1  
* 1.1.1.2  
* 1.1.1.3  
* 1.1.1.4  
* 1.1.1.5  
* 1.1.1.6  
If these IP addresses do not match the IP addresses of the miners, then the IP addresses must be re-configured, or the code changed.  

3 - Your machine has the latest version of python3 installed and the following python modules available: time, datetime, threading, requests, json, ipaddress


## HOW TO RUN MY APPLICATION:
1 - It is recommended to use a Linux based operating system, or WSL for Windows  
2 - Open a terminal and run 'python3 app.py' to start the Flask API server  
3 - On a different terminal, start my application by entering 'python3 fleetctl.py'  


## HOW TO TEST MY APPLICATION:
1 - Once my application is begun, you are asked to specify how many miners are in the fleet, up to a maximum of 256 miners. My application checks that you enter a valid number that is within range.  
2 - Then you must specify a base IP address from which the miners are assigned in incremental order. My application checks that the base IP address you enter is a valid IP address and ends with .0  
3 - Once that information is entered and validated, my application will report results of all requests to the Flask API endpoints.  
4 - Finally, after those results are reported, there is a prompt running in its own thread, that gives you two options:  
    - Press 'M' to display the current mode that the miners are in.  This is one sentence, since all miners in the fleet are in the same mode.  
    - Press 'L' to display the action logs for every miner since my application began running. These logs are printed in JSON format and are indexed by the time the action occurs in microseconds.  Microseconds are used to ensure the inner dictionary keys are distinct and not overwritten.  The times are reported in ascending order, which means the last state reported for each miner will match the current state of all the miners (that you see when pressing 'M').  
5 - While testing these options, the main thread of my application checks the time every 60 seconds and detects when the mode of the miners must change, based on this schedule:  
  - From 00:00 to 06:00, the miner is overclocked.
  - From 06:00 to 12:00, the miner is normal.
  - From 12:00 to 18:00, the miner is underclocked.
  - From 18:00 to midnight, the miner is curtailed.  

6 - To test that this schedule works, and without waiting multiple hours, the source code of my application can be changed in the area with the comment, "##### MODIFY THE SCHEDULE BELOW FOR TESTING #####". Once you modify the schedule, my application's timing can be tested immediately or within minutes.
