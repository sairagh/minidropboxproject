# client.py

import socket  # Import socket module
import sys
import datetime
import time
import os

logfile = open('history', 'a+')
querycheckfile = open('queryresults', 'a+')
errorlog = open('errors', 'a+')
outputlog = open('outbox', 'a+')


class udp_client:
    def send(self, message, file_request, ip, directory):
        try:
            s = self.connect(ip)
        except Exception, e:
            print str(e)
            errorlog.write(str(e))
            return
        receiving = True
        data = ""
        validity = True
        header = True

        s.sendto(message, (ip, 60001))
        outputlog.write(message)

        if file_request:
            try:
                sequence_number = 0
                file_path = os.path.join(directory, message.split('?')[1].strip())
                if not os.path.exists(os.path.dirname(file_path)):
                    try:
                        os.makedirs(os.path.dirname(file_path))
                        outputlog.write("made a directory with name" + file_path)
                    except Exception, e:
                        print str(e) + ' : Could not create the directory'
                        errorlog.write(str(e) + ' : Could not create the directory')
                        return
                with open(file_path, 'wb') as f:
                    while receiving:
                        data, addr = s.recvfrom(1024)
                        if header and len(data.split('?')) > 4:
                            print 'Received File \n' + data.split('?')[0] + '\n' + data.split('?')[1] + '\n' + \
                                  data.split('?')[2] + '\n' + data.split('?')[3] + '\n' + "End of header"
                            f.write(data.split('?')[4])
                            querycheckfile.write(data.split('?')[4])
                            s.sendto('0', (ip, 60001))
                            outputlog.write('0')
                            header = False
                        elif validity == True:
                            if data.split('#NEXT#')[0] == str(sequence_number + 1):
                                sequence_number += 1
                                s.sendto(str(sequence_number), (ip, 60001))
                                outputlog.write(str(sequence_number))
                                f.write(data.split('#NEXT#')[1])
                                querycheckfile.write(data.split('#NEXT#')[1])
                            else:
                                s.sendto('-1', (ip, 60001))
                                outputlog.write('-1')
                f.close()
                s.close()
                if validity:
                    return "File read"

            except Exception, e:
                print str(e)
                errorlog.write(str(e))
        else:
            try:
                while receiving:
                    data_cur, addr = s.recvfrom(1024)
                    if data_cur == '#END#':
                        receiving = False
                        break
                    data += data_cur
                s.close()
                return data
            except Exception, e:
                print str(e)
                errorlog.write(str(e))

    def connect(self, ip):
        return socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


class tcp_client:
    def connect(self, ip):
        s = socket.socket()
        print "connected to server"
        s.connect((ip, 60000))
        return s

    def send(self, message, file_request, ip, directory):
        try:
            s = self.connect(ip)
            print s
            querycheckfile.write(str(s))
        except Exception, e:
            print str(e) + ' : Failed to connect'
            errorlog.write(str(e) + ' : Failed to connect')
            return
        receiving = True
        data = ""
        validity = True
        header = True

        s.send(message)
        outputlog.write(message)
        if file_request:
            try:
                file_path = os.path.join(directory, message.split('?')[1].strip())
                if not os.path.exists(os.path.dirname(file_path)):
                    try:
                        os.makedirs(os.path.dirname(file_path))
                    except Exception, e:
                        print str(e) + ' : Could not create the directory'
                        errorlog.write(str(e) + ' : Could not create the directory')
                        return
                with open(file_path, 'wb') as f:
                    while True:
                        data = s.recv(1024)
                        if header and len(data.split('?')) > 4:
                            print 'Received File \n' + data.split('?')[0] + '\n' + data.split('?')[1] + '\n' + \
                                  data.split('?')[2] + '\n' + data.split('?')[3] + '\n' + "End of header"
                            f.write(data.split('?')[4])
                            querycheckfile.write(data.split('?')[4])
                            header = False
                        elif validity == True:
                            f.write(data)
                            querycheckfile.write(data.split('?')[4])
                            # write data to a file
                f.close()

                s.close()
                if validity:
                    return "File read"

            except Exception, e:
                print str(e) + ' : Unable to fetch file from server, please enter the correct command'
                errorlog.write(str(e) + ' : Unable to fetch file from server, please enter the correct command')

        else:
            try:
                while receiving:
                    data_cur = s.recv(1024)
                    if not data_cur:
                        receiving = False
                    data += data_cur
                s.close()
                querycheckfile.write(data)
                return data
            except Exception, e:
                print str(e) + ' : Unable to fetch data from server'
                errorlog.write(str(e) + ' : Unable to fetch data from server')


