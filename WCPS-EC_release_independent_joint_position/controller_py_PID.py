#!/usr/bin/env python
import sys
import socket
import os
import time
import serial
import math
import numpy
import re
from datetime import datetime
from threading import Thread
from socketserver import ThreadingMixIn

round_counter = 1
theta_ref = 0
thetaini = 0
uini = 0
delta_t = 0.05;
yh_last = 0
yh = 1
kp = 800
ki = 0
kd = 0
theta_last = thetaini
theta_last_last = thetaini
uout_last = uini
compu_latency = []

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('0.0.0.0', 8000) #IP address of linux PC
print >>sys.stderr, 'starting up on %s port %s' % server_address
sock.bind(server_address)
sock.listen(1)
while True:
    connection, client_address = sock.accept()
    print >>sys.stderr,'Connection from:', client_address
    try:
      while True:
            data=connection.recv(80) 
            #print data     
            if data:
                  t = time.time()
                  print data
                  print round_counter
                  timeT=datetime.now().strftime('%Y,%m,%d,%H,%M,%S.%f')
                  print "data=",data
                  #data_split = [float(x) for x in data.split(',')]
                  data_split = [float(x.strip()) for x in re.compile('-*\w+.\w+').findall(data.strip())]

                  #print data
                  if data_split[0] !=10000:
                    theta_ref = data_split[0]
                    theta = data_split[1]
                    theta_error = data_split[2]
                      

                    yh_last = yh
                    yh = data_split[3]
                    sensor_seq = data_split[4]
                    # print "theta_ref=",theta_ref,", theta=",theta, "theta_error=", theta_error
                    # print "theta_last=",theta_last
                    # print "theta_last_last=",theta_last_last
                    # print "sensor_seq", sensor_seq
                    if yh_last!=yh:
                      round_counter = 1
                      yh_last = yh

                    # print "out last:",uout_last
                    # print "kp*(theta_error - theta_last):",kp*(theta_error - theta_last)
                    # print "ki*delta_t*theta_error:", ki*delta_t*theta_error
                    # print "kd*(theta_error-2 * theta_last + theta_last_last)/delta_t:", kd*(theta_error-2 * theta_last + theta_last_last)/delta_t
                    if round_counter == 1:
                      theta_last_last = theta_error
                      theta_last = theta_error
                      uout_last = uini
                      # uout = uini
                      uout = uout_last + kp*theta_error + ki*delta_t*theta_error
                    
                    else:
                      uout = uout_last + kp*(theta_error - theta_last) + ki*delta_t*theta_error + kd*(theta_error-2 * theta_last + theta_last_last)/delta_t

                    uout_last = uout
                    theta_last_last = theta_last
                    theta_last = theta_error
                    

                    print "Uout generated by python code on server:", uout  
                    connection.send('% 3.4f,% 3.4f' % (uout, sensor_seq))
                    round_counter = round_counter + 1
                    elapsed = time.time() - t
                    print "Computational latency:", elapsed
                    compu_latency.extend([elapsed])
                    if sensor_seq>1198:
                      print "Computational latency list", compu_latency

            else:
                  break

    finally:
        connection.close()
        
