# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
import uos, machine
#uos.dupterm(None, 1) # disable REPL on UART(0)

import wifi_creds
import network
net_if = network.WLAN(network.STA_IF)

def do_connect():
    if not net_if.isconnected():
        import wifi_creds
        net_if.active(True)
        net_if.connect(wifi_creds.WIFI_SSID,wifi_creds.WIFI_PASSWD)
        net_if.config(dhcp_hostname=wifi_creds.WIFI_DEV_HOSTNAME)
        while not net_if.isconnected():
           pass

#import webrepl
#webrepl.start()

import gc
gc.collect()


