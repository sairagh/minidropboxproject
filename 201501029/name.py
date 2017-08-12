if protocol == 3:
    logfile.close()
    sys.exit()
if protocol == 4:
    firsttime = 1
    lastsystime = 0
    lasttimedownload = ''
    while (True):
        presentsystime = time.time()

        if (presentsystime - lastsystime > 10):
            presenttime = time.strftime("%c")
            lastsystime = time.time()
            if firsttime:
                res = tcpconnection.send("index longlist", False, ip, directory)
                print res

            else:

                input_raw = "index shortlist " + lasttimedownload + " " + presenttime

                print input_raw
                inputs = input_raw.split(' ')
                messageserver = 'index shortlist ?' + inputs[2] + ' ' + inputs[3] + ' ' + inputs[4] + ' ' + \
                                inputs[5] + ' ' + inputs[6] + ' ? ' + inputs[7] + ' ' + inputs[8] + ' ' + inputs[
                                    9] + ' ' + inputs[10] + ' ' + inputs[11]
                print messageserver

                res = tcpconnection.send(messageserver, False, ip, directory)
                print res
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
                        print line, word
                        print "camehere"
                if line == '\n':
                    linebegin = 1
                    if not firsttime:
                        filelist.append(word)
                    print word
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
