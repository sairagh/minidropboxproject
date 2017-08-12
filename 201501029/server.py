# server.py

import socket                   # Import socket module
import os
import time
import mimetypes
import hashlib
from datetime import datetime
import glob
import re
logfile = open('serverhistory', 'a+')
querycheckfile = open('serverqueryresults', 'a+')
errorlog = open('servererrors', 'a+')
outputlog = open('serveroutbox', 'a+')

def md5(fname):
    hash_value = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_value.update(chunk)
    querycheckfile.write(str(hash_value.hexdigest))
    return hash_value.hexdigest()

class udp_server:

    def init(self,ip):
        port = 60001
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)             # Create a socket object
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((ip, port))
        querycheckfile.write(str(s))
        return s

    def runServer(self,ip, directory):
        s = self.init(ip)
        print 'started UDP server'

        while True:

            data, addr = s.recvfrom(1024)
            if data == 'Hello server':
                s.sendto('Hello Client', addr)
                outputlog.write('Hello Client')
            if "index" in data:
                if "shortlist" in data:
                    try:
                        data_arr = data.split('?')
                        querycheckfile.write(str(data_arr))
                        time_l = datetime.strptime(data_arr[1].strip(), "%a %b %d %H:%M:%S %Y")
                        time_r = datetime.strptime(data_arr[2].strip(), "%a %b %d %H:%M:%S %Y")
                        querycheckfile.write(str(time_l))
                        files = []
                        file_endings = []
                        for dp,dd,f in os.walk(directory):
                            for j in range(len(f)):
                                file_name = dp
                                if dp[len(dp)-1] != '/':
                                    file_name += '/'
                                file_name += f[j]
                                file_endings.append(os.path.relpath(file_name, os.path.commonprefix([file_name,directory])))
                                files.append(file_name)
                                logfile.write(file_name)
                        for f in range(len(files)):
                            filename = files[f]
                            created_time = time.ctime(os.path.getctime(filename))
                            act_time = datetime.strptime(created_time, "%a %b %d %H:%M:%S %Y")
                            querycheckfile.write(str(created_time))
                            if act_time <= time_r and act_time >= time_l:
                                s.sendto(file_endings[f] + '\n', addr)
                                outputlog.write(file_endings[f] + '\n')
                        s.sendto('#END#',addr)
                        outputlog.write('#END#')
                    except Exception,e:
                        print str(e) + ' : An error occured while fetching the filelist, make sure you enter the correct command'
                        errorlog.write(str(e) + ' : An error occured while fetching the filelist, make sure you enter the correct command')

                if "longlist" in data:
                    try:
                        files = []
                        file_endings = []
                        for dp,dd,f in os.walk(directory):
                            for j in range(len(f)):
                                file_name = dp
                                if dp[len(dp)-1] != '/':
                                    file_name += '/'
                                file_name += f[j]
                                file_endings.append(os.path.relpath(file_name, os.path.commonprefix([file_name,directory])))
                                files.append(file_name)
                                logfile.write(file_name)
                        for f in range(len(files)):
                            filename = files[f]
                            statinfo = os.stat(filename)
                            size = str(statinfo.st_size)
                            querycheckfile.write(filename)
                            modified_time = time.ctime(os.path.getmtime(filename))
                            created_time = time.ctime(os.path.getctime(filename))
                            querycheckfile.write(modified_time)
                            type_of_file, encoding = mimetypes.guess_type(filename,True)
                            if type_of_file:
                                s.sendto(file_endings[f] + '\t' + size + '\t' + modified_time + '\t' + created_time + '\t' + type_of_file + '\n', addr)  #send file list to server
                                outputlog.write(file_endings[f] + '\t' + size + '\t' + modified_time + '\t' + created_time + '\t' + type_of_file + '\n')
                            else:
                                s.sendto(file_endings[f] + '\t' + size + '\t' + modified_time + '\t' + created_time + '\t' + 'None' + '\n', addr)  #send file list to server
                                outputlog.write(file_endings[f] + '\t' + size + '\t' + modified_time + '\t' + created_time + '\t' + 'None' + '\n')
                        s.sendto('#END#',addr)
                        outputlog.write('#END#')
                    except Exception,e:
                        print str(e) + ' : An error occured while fetching the filelist, make sure you enter the correct command'
                        errorlog.write(str(e) + ' : An error occured while fetching the filelist, make sure you enter the correct command')

                if "regex" in data:
                    try:
                        invalid = False
                        regex = data.split('?')[1].strip()
                        querycheckfile.write(regex)
                        try:
                            re.search(regex,"")

                        except Exception,e:
                            invalid = True
                            print 'Invalid regex'
                            errorlog.write('Invalid regex')
                        if not invalid:
                            files = []
                            file_endings = []
                            for dp,dd,f in os.walk(directory):
                                for j in range(len(f)):
                                    file_name = dp
                                    if dp[len(dp)-1] != '/':
                                        file_name += '/'
                                    file_name += f[j]
                                    file_endings.append(os.path.relpath(file_name, os.path.commonprefix([file_name,directory])))
                                    files.append(file_name)
                                    querycheckfile.write(file_name)
                            for f in range(len(files)):
                                if re.search(regex,files[f]):
                                    s.sendto(file_endings[f] + '\n', addr)
                                    outputlog.write(file_endings[f] + '\n')
                        s.sendto('#END#', addr)
                        outputlog.write('#ENDE#')
                    except Exception,e:
                        print str(e) + ' : An error occured while fetching the filelist, make sure you enter the correct command'
                        errorlog.write(str(e) + ' : An error occured while fetching the filelist, make sure you enter the correct command')
                        continue

            if "download" in data:
                try:
                    command,value = data.split('?')
                    value=value.strip()
                    file_abspath = os.path.abspath(directory + value)
                    if file_abspath.find(os.path.abspath(directory)) != 0:
                        s.sendto('#102', addr)
                        outputlog.write('#102#')
                    elif os.path.isfile(directory + value):
                        filename=directory + value
                        statinfo = os.stat(filename)
                        size = str(statinfo.st_size)
                        querycheckfile.write(filename)
                        modified_time = time.ctime(os.path.getmtime(filename))
                        created_time = time.ctime(os.path.getctime(filename))
                        querycheckfile.write(modified_time)
                        hash_value = md5(filename)
                        s.sendto(value +'?'+size+'?'+modified_time+'?'+hash_value+'?', addr)
                        outputlog.write(value +'?'+size+'?'+modified_time+'?'+hash_value+'?')
                        data,addr = s.recvfrom(1024)
                        f = open(filename,'rb')
                        l = f.read(512)
                        seq_number = 1
                        while (l):
                            s.sendto(str(seq_number) + '#NEXT#' + l, addr)
                            outputlog.write(str(seq_number) + '#NEXT#' + l)
                            data,addr = s.recvfrom(1024)
                            while data != str(seq_number):
                                s.sendto(str(seq_number) + '#NEXT#' + l, addr)
                                outputlog.write(str(seq_number) + '#NEXT#' + l)
                                s.settimeout(5.0)
                                data,addr = s.recvfrom(1024)
                            seq_number += 1
                            l = f.read(512)
                        f.close()
                    else:
                        s.sendto("#101",addr)
                        querycheckfile.write("#101")
                    s.sendto('#END#',addr)
                    outputlog.write('#END#')
                except Exception,e:
                    print str(e) + ' : An error occured while fetching the file, make sure you enter the correct command'
                    errorlog.write(str(e) + ' : An error occured while fetching the file, make sure you enter the correct command')
            
            if "hash" in data:
                try:
                    if "verify" in data:
                        command1,filenameold = data.split('?')
                        filename = directory + filenameold.strip()
                        if os.path.isfile(filename):
                            s.sendto(filenameold + ' => ' + md5(filename) + ', ' + time.ctime(os.path.getmtime(filename)), addr)
                            outputlog.write(filenameold + ' => ' + md5(filename) + ', ' + time.ctime(os.path.getmtime(filename)))
                        else:
                            s.sendto("#101", addr)
                            outputlog.write("#101#")
                        s.sendto('#END#',addr)
                        outputlog.write('#END#')
                    elif "checkall" in data:
                        files = []
                        file_endings = []
                        for dp,dd,f in os.walk(directory):
                            for     j in range(len(f)):
                                file_name = dp
                                if dp[len(dp)-1] != '/':
                                    file_name += '/'
                                file_name += f[j]
                                file_endings.append(os.path.relpath(file_name, os.path.commonprefix([file_name,directory])))
                                files.append(file_name)
                                querycheckfile.write(file_name)
                        for f in range(len(files)):
                            s.sendto(file_endings[f] + ' => ' + md5(files[f]) + ', ' + time.ctime(os.path.getmtime(files[f])) + '\n', addr)
                            outputlog.write(file_endings[f] + ' => ' + md5(files[f]) + ', ' + time.ctime(os.path.getmtime(files[f])) + '\n')
                        s.sendto('#END#',addr)
                        outputlog.write('#END#')
                except Exception,e:
                    print str(e) + ' : An error occured while getting the hash of the file(s), make sure you enter the correct command'
                    outputlog.write(str(e) + ' : An error occured while getting the hash of the file(s), make sure you enter the correct command')


class tcp_server:

    def init(self,ip):
        port = 60006             # Reserve a port for your service.
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)             # Create a socket object
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        host = socket.gethostname()     # Get local machine name
        s.bind((ip, port))            # Bind to the port
        s.listen(5)                     # Now wait for client connection.
        return s

    def runServer(self,ip, directory):
        s = self.init(ip)
        print 'TCP server listening....'
        querycheckfile.write('TCP server listening....')
        while True:
            conn, addr = s.accept()     # Establish connection with client.
            data = conn.recv(1024)
            if data=="Hello server!":
                conn.send("Hello client!")
                outputlog.write("Hello client!")

            if "index" in data:
                if "shortlist" in data:
                    try:
                        data_arr = data.split('?')
                        querycheckfile.write(str(data_arr))
                        time_l = datetime.strptime(data_arr[1].strip(), "%a %b %d %H:%M:%S %Y")
                        time_r = datetime.strptime(data_arr[2].strip(), "%a %b %d %H:%M:%S %Y")
                        querycheckfile.write(str(time_l))
                        files = []
                        file_endings = []
                        for dp,dd,f in os.walk(directory):
                            for j in range(len(f)):
                                file_name = dp
                                if dp[len(dp)-1] != '/':
                                    file_name += '/'
                                file_name += f[j]
                                file_endings.append(os.path.relpath(file_name, os.path.commonprefix([file_name,directory])))
                                files.append(file_name)
                                querycheckfile.write(file_name)
                        for f in range(len(files)):
                            filename = files[f]
                            created_time = time.ctime(os.path.getctime(filename))
                            act_time = datetime.strptime(created_time, "%a %b %d %H:%M:%S %Y")
                            if act_time <= time_r and act_time >= time_l:
                                conn.send(file_endings[f] + '\n')
                                outputlog.write(file_endings[f] + '\n')
                    except Exception,e:
                        print str(e) + ' : An error occured while fetching the filelist, make sure you enter the correct command'
                        outputlog.write(str(e) + ' : An error occured while fetching the filelist, make sure you enter the correct command')

                if "longlist" in data:
                    try:
                        files = []
                        file_endings = []
                        for dp,dd,f in os.walk(directory):
                            for j in range(len(f)):
                                file_name = dp
                                if dp[len(dp)-1] != '/':
                                    file_name += '/'
                                file_name += f[j]
                                file_endings.append(os.path.relpath(file_name, os.path.commonprefix([file_name,directory])))
                                files.append(file_name)
                        for f in range(len(files)):
                            filename = files[f]
                            statinfo = os.stat(filename)
                            size = str(statinfo.st_size)
                            outputlog.write(filename)
                            modified_time = time.ctime(os.path.getmtime(filename))
                            created_time = time.ctime(os.path.getctime(filename))
                            outputlog.write(modified_time)
                            type_of_file, encoding = mimetypes.guess_type(filename,True)
                            if type_of_file:
                                conn.send(file_endings[f] + '\t' + size + '\t' + modified_time + '\t' + created_time + '\t' + type_of_file + '\n')  #send file list to server
                                outputlog.write(file_endings[f] + '\t' + size + '\t' + modified_time + '\t' + created_time + '\t' + type_of_file + '\n')
                            else:
                                conn.send(file_endings[f] + '\t' + size + '\t' + modified_time + '\t' + created_time + '\t' + 'None' + '\n')  #send file list to server
                                outputlog.write(file_endings[f] + '\t' + size + '\t' + modified_time + '\t' + created_time + '\t' + 'None' + '\n')
                    except Exception,e:
                        print str(e) + ' : An error occured while fetching the filelist, make sure you enter the correct command'
                        outputlog.write(str(e) + ' : An error occured while fetching the filelist, make sure you enter the correct command')

                if "regex" in data:
                    try:
                        invalid = False
                        regex = data.split('?')[1].strip()
                        try:
                            re.search(regex,"")
                        except Exception,e:
                            invalid = True
                            print 'Invalid regex'
                            errorlog.write('Invalid regex')
                        if not invalid:
                            files = []
                            file_endings = []
                            for dp,dd,f in os.walk(directory):
                                for j in range(len(f)):
                                    file_name = dp
                                    if dp[len(dp)-1] != '/':
                                        file_name += '/'
                                    file_name += f[j]
                                    file_endings.append(os.path.relpath(file_name, os.path.commonprefix([file_name,directory])))
                                    files.append(file_name)
                                    querycheckfile.write(file_name)
                            for f in range(len(files)):
                                if re.search(regex,files[f]):
                                    conn.send(file_endings[f] + '\n')
                                    outputlog.write(file_endings[f] + '\n')
                    except Exception,e:
                        print str(e) + ' : An error occured while fetching the filelist, make sure you enter the correct command'
                        errorlog.write(str(e) + ' : An error occured while fetching the filelist, make sure you enter the correct command')
                        continue

            if "download" in data:
                try:
                    command,value = data.split('?')
                    value=value.strip()
                    file_abspath = os.path.abspath(directory + value)
                    if file_abspath.find(os.path.abspath(directory)) != 0:
                        conn.send('#102')
                        outputlog.write('#102')
                    elif os.path.isfile(directory + value):
                        filename=directory + value
                        statinfo = os.stat( filename)
                        size = str(statinfo.st_size)
                        querycheckfile.write(filename)
                        modified_time = time.ctime(os.path.getmtime(filename))
                        created_time = time.ctime(os.path.getctime(filename))
                        querycheckfile.write(modified_time)
                        hash_value = md5(filename)
                        conn.send(value+'?'+size+'?'+modified_time+'?'+hash_value+'?')
                        outputlog.write(value+'?'+size+'?'+modified_time+'?'+hash_value+'?')
                        f = open(filename,'rb')
                        l = f.read(1024)
                        while (l):
                            conn.send(l)
                            outputlog.write(l)
                            l = f.read(1024)
                        f.close()
                    else:
                        conn.send("#101")
                        outputlog.write("#101")
                except Exception,e:
                    print str(e) + ' : An error occured while fetching the file, make sure you enter the correct command'
                    errorlog.write(str(e) + ' : An error occured while fetching the file, make sure you enter the correct command')

            if "hash" in data:
                try:
                    if "verify" in data:
                        command1,filenameold = data.split('?')
                        filename = directory + filenameold.strip()
                        if os.path.isfile(filename):
                            conn.send(filenameold + ' => ' + md5(filename) + ', ' + time.ctime(os.path.getmtime(filename)))
                            outputlog.write(filenameold + ' => ' + md5(filename) + ', ' + time.ctime(os.path.getmtime(filename)))
                        else:
                            conn.send("#101")
                            outputlog.write("#101")
                    elif "checkall" in data:
                        files = []
                        file_endings = []
                        for dp,dd,f in os.walk(directory):
                            for j in range(len(f)):
                                file_name = dp
                                if dp[len(dp)-1] != '/':
                                    file_name += '/'
                                file_name += f[j]
                                file_endings.append(os.path.relpath(file_name, os.path.commonprefix([file_name,directory])))
                                files.append(file_name)
                                querycheckfile.write(file_name)
                        for f in range(len(files)):
                            conn.send(file_endings[f] + ' => ' + md5(files[f]) + ', ' + time.ctime(os.path.getmtime(files[f])) + '\n')
                            outputlog.write(file_endings[f] + ' => ' + md5(files[f]) + ', ' + time.ctime(os.path.getmtime(files[f])) + '\n')
                except Exception,e:
                    print str(e) + ' : An error occured while getting the hash of the file(s), make sure you enter the correct command'
                    errorlog.write(str(e) + ' : An error occured while getting the hash of the file(s), make sure you enter the correct command')
            
            conn.close()

# Error codes
#101 for file not found
#102 for permission denied 

def tcp_main(ip, directory):
    server = tcp_server()
    server.runServer(ip, directory)

def udp_main(ip, directory):
    server = udp_server()
    server.runServer(ip, directory)
