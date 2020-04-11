#Author: Alex Orlov
#This program automatically checks the weather forecast for multiple user set parameters
#The user can add any number of locations to be checked
#To add a location, click the "Add location" button and populate all fields
#To start the system, click the "Start" button. The program will begin running, and immediately do a check based
#on your parameters. If you wish to modify fields, or add new locations, hit the "Stop" button.
#Then, make your changes and hit the "Start" button again.
#The program will automatically do a check every 3 hours after the "Start" button has been clicked

#Wire an RGB LED to BCM pins 16 (R), 20 (G), and 21 (B)
#Wire a pushbutton to 5V and BCM pin 18, with a current limiting resistor (100 ohm)


import tkinter
import requests
import smtplib
import ssl
import time
import RPi.GPIO as GPIO


running = False #Once the run button is pressed, set to True and run automatically every 3 hours

parameter_constant = 9 #constant which makes it easier for me to add parameters. Include 1 for the blank parameter
num_locations = 0 #we will increment this as we add locations

#an array to hold all the data
location_array = []

#Email stuff
port = 465  # For SSL
password = "<removed>"
sender_email = "<removed>"
# Create a secure SSL context
context = ssl.create_default_context()

def set_led(color):
    # white 
    if color == "white":
        GPIO.output(RED, GPIO.HIGH)
        GPIO.output(GREEN, GPIO.HIGH)
        GPIO.output(BLUE, GPIO.HIGH)
    
    elif color == "red":
        GPIO.output(RED, GPIO.HIGH)
        GPIO.output(GREEN, GPIO.LOW)
        GPIO.output(BLUE, GPIO.LOW)
    
    elif color == "green":
        GPIO.output(RED, GPIO.LOW)
        GPIO.output(GREEN, GPIO.HIGH)
        GPIO.output(BLUE, GPIO.LOW)
        
    elif color == "cyan":
        GPIO.output(RED, GPIO.LOW)
        GPIO.output(GREEN, GPIO.HIGH)
        GPIO.output(BLUE, GPIO.HIGH)
             
    elif color == "blue":
        GPIO.output(RED, GPIO.LOW)
        GPIO.output(GREEN, GPIO.LOW)
        GPIO.output(BLUE, GPIO.HIGH)
        
    elif color == "magenta":
        GPIO.output(RED, GPIO.HIGH)
        GPIO.output(GREEN, GPIO.LOW)
        GPIO.output(BLUE, GPIO.HIGH)
        
    elif color == "yellow":
        GPIO.output(RED, GPIO.HIGH)
        GPIO.output(GREEN, GPIO.HIGH)
        GPIO.output(BLUE, GPIO.LOW)
        
    elif color == "off":
        GPIO.output(RED, GPIO.LOW)
        GPIO.output(GREEN, GPIO.LOW)
        GPIO.output(BLUE, GPIO.LOW)
    
    else:
        print("Invalid input")
        
def setGPIO():
    channels=[RED, GREEN, BLUE]
    GPIO.setmode(GPIO.BCM) #Cable labeled with BCM numbers
    GPIO.setup(channels, GPIO.OUT, initial=GPIO.LOW)
    
def button_callback(channel):
    set_led("off")

def weather_forecast():
    if(running):
        for i in range(num_locations):
            receiver_email = receiver_email_entry.get()
            zipcode = location_array[i]['zip_entry'].get()
            windspeed_low = int(location_array[i]['windspeed_low'].get())
            windspeed_high = int(location_array[i]['windspeed_high'].get())
            wind_direction_low = int(location_array[i]['wind_direction_low'].get())
            wind_direction_high = int(location_array[i]['wind_direction_high'].get())
            r = requests.get('http://api.openweathermap.org/data/2.5/forecast?zip=' + zipcode + ',us&appid=<removed>&units=imperial')
            json_object = r.json()
            location_info_json = json_object['city']
            forecast_array = json_object['list']
            # Clear last message and start a new one
            message = """\
            Weather Notification\n

            There may be a good flying day coming up!
            See below for details.

            Location info: """ + str(location_info_json)

            # clear last valid day boolean
            valid_day = False

            # parse the forecast and figure out if there are any valid days
            for i in range(len(forecast_array)):
                forecast_n = forecast_array[i]
                windspeed = forecast_n['wind']['speed']
                wind_direction = forecast_n['wind']['deg']
                if (windspeed < windspeed_high and windspeed > windspeed_low):
                    if (wind_direction < wind_direction_high and wind_direction > wind_direction_low):
                        valid_day = True
                        dt_text = forecast_n['dt_txt']
                        message += "\n\nDate and time: " + dt_text + "\nWindspeed: " + str(
                            windspeed) + "\nWind direction: " + str(wind_direction) + "\n"

            # if theres a valid day, send an email
            if valid_day:
                set_led("green")
                with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
                    server.login(sender_email, password)
                    server.sendmail(sender_email, receiver_email, message)
            else:
                set_led("off")
    else:
        print("Stopped")
        
    m.after(10800000, weather_forecast) #Unless the user hits Stop, after Start is pressed run every 3 hours

def add_fields():
    global num_locations, location_array #tell the interpreter to look for num_locations in the global scope. We've got an assignment statement, so we've got to do this
    location_array.append({})
    num_locations += 1
    base_loc = (num_locations*parameter_constant)+2
    tkinter.Label(m, text='Name').grid(row=base_loc)
    location_array[num_locations-1]['name'] = tkinter.Entry(m)
    location_array[num_locations-1]['name'].grid(row=base_loc, column=1)

    tkinter.Label(m, text='zipcode').grid(row=base_loc+1) #don't store, we don't care about saving this Label data field
    location_array[num_locations-1]['zip_entry'] = tkinter.Entry(m)
    location_array[num_locations-1]['zip_entry'].grid(row=base_loc+1, column=1)

    tkinter.Label(m, text='Windspeed Low (mph)').grid(row=base_loc+2)
    location_array[num_locations - 1]['windspeed_low'] = tkinter.Entry(m)
    location_array[num_locations - 1]['windspeed_low'].grid(row=base_loc+2, column=1)

    tkinter.Label(m, text='Windspeed High (mph)').grid(row=base_loc + 3)
    location_array[num_locations - 1]['windspeed_high'] = tkinter.Entry(m)
    location_array[num_locations - 1]['windspeed_high'].grid(row=base_loc + 3, column=1)

    tkinter.Label(m, text='Wind Direction Low (deg)').grid(row=base_loc + 4)
    location_array[num_locations - 1]['wind_direction_low'] = tkinter.Entry(m)
    location_array[num_locations - 1]['wind_direction_low'].grid(row=base_loc + 4, column=1)

    tkinter.Label(m, text='Wind Direction High (deg)').grid(row=base_loc + 5)
    location_array[num_locations - 1]['wind_direction_high'] = tkinter.Entry(m)
    location_array[num_locations - 1]['wind_direction_high'].grid(row=base_loc + 5, column=1)

    tkinter.Label(m, text='').grid(row=base_loc + 7)#Blank line in between locations for readability
    
def start_running():
    print("Start Running called")
    global running
    running = True
    weather_forecast() #kick off the infinite loop
    
def stop_running():
    global running
    running = False

#main

#GPIO
RED = 16
GREEN = 20
BLUE = 21
setGPIO()

GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.add_event_detect(18, GPIO.RISING, callback=button_callback)

#GUI stuff
m = tkinter.Tk()
m.title('Automatic Weather Forecast User Input')
run_button = tkinter.Button(m, text='Run', width = 25, command=start_running)
run_button.grid(row=0)
stop_button = tkinter.Button(m, text='Stop', width = 25, command=stop_running)
stop_button.grid(row=1)
add_fields_button = tkinter.Button(m, text='Add Location', width = 25, command=add_fields)
add_fields_button.grid(row=2)
tkinter.Label(m, text='Receiver Email').grid(row=3)
receiver_email_entry = tkinter.Entry(m)
receiver_email_entry.grid(row=3, column=1)
m.mainloop()
