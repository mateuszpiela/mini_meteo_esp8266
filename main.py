import machine
import socket
import ure
import json
import sys
import os
import ussl


do_connect()

def headers(conn,httpcode):
    conn.send('HTTP/1.1 '+httpcode+' OK\n')
    conn.send('Server: MateuszAPI\n')
    conn.send('Content-Type: application/json;charset=utf-8\n')
    conn.send('Connection: close\n\n')

def exception(conn,msg):
    headers(conn,'500')
    conn.sendall(json.dumps({"status": "0","msg": msg}))

def dht11(conn,path):
    path_param = path.split("/")
    if(len(path_param)-1 > 3):
        headers(conn,'404')
        return ""
    
    if(len(path_param)-1 < 3):
        headers(conn,'404')
        return ""
    pin = path_param[3]
    pin = int(pin)
    
    import dht

    d = dht.DHT11(machine.Pin(pin))
        
    try:
        d.measure()
        headers(conn,'200')
        conn.sendall(json.dumps({"status": "1", "data": {"temperature": d.temperature(),"humidity": d.humidity()}}))
    except OSError as e:
        if e.args[0] == 110:
            exception(conn,"Connection to sensor timed out :(")
        else:
            exception(conn,"General failure!")
    except:
        exception(conn,"General failure!")

def bmp180(conn,path):
    path_param = path.split("/")
    if(len(path_param)-1 > 4):
        headers(conn,'404')
        return ""
    
    if(len(path_param)-1 < 4):
        headers(conn,'404')
        return ""
    
    scl = path_param[3]
    sda = path_param[4]
    scl = int(scl)
    sda = int(sda)
    
    try:
        from bmp180_driver import BMP180
        
        headers(conn,'200')
        bus =  machine.I2C(scl=machine.Pin(scl), sda=machine.Pin(sda), freq=100000)   # on esp8266
        bmp180 = BMP180(bus)
        bmp180.oversample_sett = 2
        conn.sendall(json.dumps({"status": "1", "data": {"temperature": bmp180.temperature,"pressure": bmp180.pressure,"altitude": bmp180.altitude}}))
    except OSError as e:
        if e.args[0] == 110:
            exception(conn,"Connection to sensor timed out :(")
        else:
            exception(conn,"General failure!")

addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(5)

print("Starting main api server")
print("ip addr:" + net_if.ifconfig()[0])

while True:
    conn, addr = s.accept()
    print('Got a connection to api from %s' % addr[0])
    request = conn.recv(1024)
    request = str(request)
    request_arr = request.split("\\r\\n")
    path = request_arr[0]
    path = path.split()
    request_method = path[0]
    path = path[1]
    if "/sensors/dht11/" in path:
        dht11(conn,path)
    elif "/sensors/bmp180/" in path:
        bmp180(conn,path)
    else:
        headers(conn,'404')
    conn.close()


