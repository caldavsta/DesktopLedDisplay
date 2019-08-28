#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2018-2019 Caleb Stamper
# PYTHON_ARGCOMPLETE_OK

import sys
from random import randrange
from luma.core import cmdline, error
from luma.core.render import canvas
from luma.core.virtual import viewport
from luma.core.legacy import text
from luma.core.legacy.font import proportional, TINY_FONT, CP437_FONT, LCD_FONT
import schedule
import time
import argparse
import forecastio
import asyncio
import threading


weather_string = "??f"
time_string = "xx:xx:xx"
scroll_text_current = 0 #beta
weather_requested = 0
loading_animation_status = 1

# the following method is Copyright (c) 2014-17 Richard Hull 
def get_device(actual_args=None):
    """
    Create device from command-line arguments and return it.
    """
    if actual_args is None:
        actual_args = sys.argv[1:]
    parser = cmdline.create_parser(description='luma.examples arguments')
    args = parser.parse_args(actual_args)

    if args.config:
        # load config from file
        config = cmdline.load_config(args.config)
        args = parser.parse_args(config + actual_args)

    print(display_settings(args))

    # create device
    try:
        device = cmdline.create_device(args)
    except error.Error as e:
        parser.error(e)

    return device

# the following method is Copyright (c) 2014-17 Richard Hull 
def display_settings(args):
    """
    Display a short summary of the settings.

    :rtype: str
    """
    iface = ''
    display_types = cmdline.get_display_types()
    if args.display not in display_types['emulator']:
        iface = 'Interface: {}\n'.format(args.interface)

    lib_name = cmdline.get_library_for_display_type(args.display)
    if lib_name is not None:
        lib_version = cmdline.get_library_version(lib_name)
    else:
        lib_name = lib_version = 'unknown'

    import luma.core
    version = 'luma.{} {} (luma.core {})'.format(
        lib_name, lib_version, luma.core.__version__)

    return 'Version: {}\nDisplay: {}\n{}Dimensions: {} x {}\n{}'.format(
        version, args.display, iface, args.width, args.height, '-' * 60)

def update_weather():
    global weather_string
    global weather_requested
    api_key = "af481cf756054f887d74f276bc87a791"
    lat = 47.237223
    lng = -122.453909

    forecast = forecastio.load_forecast(api_key, lat, lng, callback=forecast_received)
    weather_requested = 1
    
    
def update_time():
    global time_string
    now=time.localtime(time.time())
    time_string = time.strftime("%-I:%M:%S", now)

def forecast_received(forecast):
    global weather_string
    global weather_requested
    print("forecast_recieved")
    weather_requested = 0
    #if the response is not an error
    if (forecast.response.status_code == 200):
        weather_string = "{:.0f}".format(forecast.currently().temperature) + "f"
    else:
        weather_string = "??f"

def draw_loading_animation(draw):
    global loading_animation_status
    if (loading_animation_status < 50):
        draw.rectangle((63,0,63,0), fill="white")
    else:
        draw.rectangle((63,1,63,1), fill="white")
    
    if (loading_animation_status > 100):
        loading_animation_status = 0
    else:
        loading_animation_status += 1

def main():
    device.height=8
    device.width=64
    max_depth = 64
    device.contrast(50)
    
    update_time()
    
    update_weather()
    schedule.every(10).minutes.do(update_weather)



    while True:        
        with canvas(device) as draw:
            update_time()
            
            text(draw,(0,0), weather_string + " " + time_string, fill="white", font=proportional(LCD_FONT))
            
            if (weather_requested == 1):
                draw_loading_animation(draw)
            schedule.run_pending()


if __name__ == "__main__":
    try:
        device = get_device()

        main()
    except KeyboardInterrupt:
        pass
