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
                        outputlog.write("made a directory with name")
                    except Exception, e:
                        print str(e) + ' : Could not create the directory'
                        errorlog.write(str(e) )
                        return
                with open(file_path, 'wb') as f:
                    while receiving:
                        data, addr = s.recvfrom(1024)
                        if data == '#END#':
                            receiving = False
                            break
                        if data == "#101" or data == '#102':
                            validity = False
                        if data == "#102":
                            return 'Please give path to file in shared folder'
                        if not data:
                            break
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
        s.connect((ip, 60006))
        return s

    def send(self, message, file_request, ip, directory):
        try:
            s = self.connect(ip)


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
                        if data == '#END#':
                            receiving = False
                            break
                        if data == "#101" or data == '#102':
                            validity = False
                        if data == "#102":
                            return 'Please give path to file in shared folder'
                        if not data:
                            break
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
                        print "2"
                        receiving = False
                    data += data_cur

                s.close()

                querycheckfile.write(data)
                return data
            except Exception, e:
                print str(e) + ' : Unable to fetch data from server'
                errorlog.write(str(e) + ' : Unable to fetch data from server')




def main(ip, directory):
    tcpconnection = tcp_client()
    udpconnection = udp_client()
    type_raw = input("1.general 2.automatic")

    if type_raw == 1:

        while True:
            input_raw = raw_input()
            try:
                if 'index' in input_raw and 'shortlist' in input_raw:
                    logfile.write(datetime.datetime.fromtimestamp(time.time()).strftime(
                        '%Y-%m-%d %H:%M:%S') + '\t' + input_raw + '\n')
                    querycheckfile.write(datetime.datetime.fromtimestamp(time.time()).strftime(
                        '%Y-%m-%d %H:%M:%S') + '\t' + input_raw + '\n')
                    inputs = input_raw.split(' ')
                    messageserver = 'index shortlist ?' + inputs[2] + ' ' + inputs[3] + ' ' + inputs[4] + ' ' + inputs[
                        5] + ' ' + inputs[6] + ' ? ' + inputs[7] + ' ' + inputs[8] + ' ' + inputs[9] + ' ' + inputs[
                                        10] + ' ' + inputs[11]
                    if 'TCP' in input_raw:
                        # IndexGet shortlist Wed Feb 10 15:51:38 2016 Wed Feb 10 15:51:54 2017
                        res = tcpconnection.send(messageserver, False, ip, directory)
                        querycheckfile.write('results:' + res)
                    elif 'UDP' in input_raw:
                        res = udpconnection.send(messageserver, False, ip, directory)
                        querycheckfile.write(('results' + res))
                    if res:
                        print res
                if 'index' in input_raw and 'longlist' in input_raw:
                    logfile.write(datetime.datetime.fromtimestamp(time.time()).strftime(
                        '%Y-%m-%d %H:%M:%S') + '\t' + input_raw + '\n')
                    querycheckfile.write(datetime.datetime.fromtimestamp(time.time()).strftime(
                        '%Y-%m-%d %H:%M:%S') + '\t' + input_raw + '\n')

                    if 'TCP' in input_raw:

                        res = tcpconnection.send("index longlist", False, ip, directory)
                        querycheckfile.write(res)
                    elif 'UDP' in input_raw:
                        res = udpconnection.send("index longlist", False, ip, directory)
                        querycheckfile.write('results' + res)
                    if res:
                        print res

                if 'index' in input_raw and 'regex' in input_raw:
                    logfile.write(datetime.datetime.fromtimestamp(time.time()).strftime(
                        '%Y-%m-%d %H:%M:%S') + '\t' + input_raw + '\n')
                    querycheckfile.write(datetime.datetime.fromtimestamp(time.time()).strftime(
                        '%Y-%m-%d %H:%M:%S') + '\t' + input_raw + '\n')
                    messageserver = 'index regex ?' + input_raw.split(' ')[2]
                    if 'TCP' in input_raw:
                        res = tcpconnection.send(messageserver, False, ip, directory)
                        querycheckfile.write('results' + res)
                    elif 'UDP' in input_raw:
                        res = udpconnection.send(messageserver, False, ip, directory)
                        querycheckfile.write('results' + res)
                    else:
                        res = udpconnection.send(messageserver, False, ip, directory)
                        querycheckfile.write('results' + res)
                    if res:
                        print res

                if 'download' in input_raw:
                    logfile.write(datetime.datetime.fromtimestamp(time.time()).strftime(
                        '%Y-%m-%d %H:%M:%S') + '\t' + input_raw + '\n')
                    querycheckfile.write(input_raw + '\n')
                    messageserver = 'download ? '
                    cnt = 0
                    for com in input_raw.split(' '):
                        if cnt >= 2:
                            messageserver += com
                        cnt += 1
                    if 'TCP' in input_raw:
                        res = udpconnection.send(messageserver, True, ip, directory)
                        querycheckfile.write('results' + str(res))
                    elif 'UDP' in input_raw:
                        res = udpconnection.send(messageserver, True, ip, directory)
                        querycheckfile.write('results' + str(res))
                    if res:
                        print res

                if 'hash' in input_raw:
                    logfile.write(datetime.datetime.fromtimestamp(time.time()).strftime(
                        '%Y-%m-%d %H:%M:%S') + '\t' + input_raw + '\n')
                    querycheckfile.write(datetime.datetime.fromtimestamp(time.time()).strftime(
                        '%Y-%m-%d %H:%M:%S') + '\t' + input_raw + '\n')
                    messageserver = 'hash ' + input_raw.split(' ')[1] + ' ? '
                    cnt = 0
                    for com in input_raw.split(' '):
                        if cnt >= 2:
                            messageserver += com
                        cnt += 1
                    if 'TCP' in input_raw:
                        res = tcpconnection.send(messageserver, False, ip, directory)
                        querycheckfile.write(res)
                    elif 'UDP' in input_raw:
                        res = udpconnection.send(messageserver, False, ip, directory)
                        querycheckfile.write(res)
                    else:
                        res = udpconnection.send(messageserver, False, ip, directory)
                    if res:
                        print res
                    else:
                        print 'Failed to get hash'
            except Exception, e:
                print str(e) + ' : Could not establish connection'
    elif type_raw == 2:

        firsttime = 1
        lastsystime = 0
        lasttimedownload = ''
        while (True):
            presentsystime = time.time()
            #print lastsystime,presentsystime
            if (presentsystime - lastsystime > 10):
                presenttime = time.strftime("%c")
                lastsystime = time.time()
                if firsttime:
                    res = udpconnection.send("index longlist", False, ip, directory)
                    print res

                else:

                    input_raw = "index shortlist " + lasttimedownload + " " + presenttime

                    inputs = input_raw.split(' ')
                    messageserver = 'index shortlist ?' + inputs[2] + ' ' + inputs[3] + ' ' + inputs[4] + ' ' + \
                                    inputs[5] + ' ' + inputs[6] + ' ? ' + inputs[7] + ' ' + inputs[8] + ' ' + inputs[
                                        9] + ' ' + inputs[10] + ' ' + inputs[11]

                    res = udpconnection.send(messageserver, False, ip, directory)
                    if res == None:
                        continue
                filelist = []
                word = ''
                linebegin = 1
                for line in res:
                    # print line,"completed"


                    if linebegin == 1:
                        if line == '\t':
                            linebegin = 0
                            filelist.append(word)
                            word = ''
                        else:
                            word += line
                    if line == '\n':
                        linebegin = 1
                        if not firsttime:
                            filelist.append(word)
                        word = ''
                firsttime = 0

                print filelist
                for word in filelist:
                    input_raw = "download " + word
                    messageserver = 'download ? '
                    cnt = 0
                    for com in input_raw.split(' '):
                        if cnt >= 1:
                            messageserver += com
                        cnt += 1
                    res = udpconnection.send(messageserver, True, ip, directory)
                    if res:
                        print res

                lasttimedownload = presenttime

