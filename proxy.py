import socket
import sys
import os,time
import thread
if len(sys.argv) <= 1:
    print 'Usage: "python S.py port"\n[port : It is the port of the Proxy Server'
    sys.exit(2)

if not 'Cache' in os.listdir("."):
    os.system("mkdir Cache")


# Server socket created, bound and starting to listen
Serv_Port = int(sys.argv[1]) # sys.argv[1] is the port number entered by the user
Serv_Sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # socket.socket function creates a socket.

# Prepare a server socket
Serv_Sock.bind(('', Serv_Port))
Serv_Sock.listen(5)


def caching_object(splitMessage, Cli_Sock):
    #this method is responsible for caching
    Req_Type = splitMessage[0]
    Req_path = splitMessage[1]

    print "Request is", Req_Type, "to URL :", Req_path

    text = splitMessage[1].split('/')
    file_to_use = text[-1]
    if file_to_use is '':
        file_to_use = "main.html"
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.connect(("127.0.0.1", 20000))

    # Searching available cache if file exists
    if file_to_use in os.listdir('./Cache/'):
        string = "GET " + "/" + text[-1] + " HTTP/1.1\r\nIf-Modified-Since: " +time.ctime(os.path.getmtime("./Cache/"+file_to_use)) +"\r\n\r\n"
        conn.send(string)
        ans1=""
        while 1:
            modified=conn.recv(1024)
            ans1+=modified
            if not modified:
                break
        ans1 = ans1.split("\r\n")
        if '200' in ans1[0]:
            print "File Was Modified\n"
            file = open("./Cache/" + file_to_use, "w")
            file.write(ans1[-1])
            Cli_Sock.send(ans1[-1])
        else:
            file = open("./Cache/" + file_to_use, "r")
            data = file.readlines()
            print "File Present in Cache And Not Modified\n"
            for i in range(0, len(data)):
                Cli_Sock.send(data[i])
        print "Reading file from cache\n"

    else:
        print "File Doesn't Exists In Cache\nFetching file from server"
        try:
            string = "GET "+"/"+text[-1]+" HTTP/1.1\r\n\r\n"
            conn.send(string)
            print("Creating cache\n")
            ans=""
            while 1:
                data = conn.recv(1024)
                ans+=data
                if not data:
                    break
            ans = ans.split("\r\n")
            if '404' in ans[0]:
                print "File Does Not Exist\n\n"
                Cli_Sock.send(ans[-1])
                conn.close()
                Cli_Sock.close()
                return
            if len(os.listdir("./Cache/")) == 3:
                print "Cache Full"
                direc = ["./Cache/" + s for s in os.listdir("./Cache/")]
                print "Removing The Oldest File"
                os.system("rm "+min(direc, key=os.path.getctime))
            if text[-1] == '':
                text[-1]="main.html"
            with open("./Cache/"+text[-1],"wb") as cache:
                cache.write(ans[-1])
            Cli_Sock.send(ans[-1])
            print "File Sent Successfully"
            conn.close()

        except:
            print 'Illegal Request'

    Cli_Sock.close()
while True:
    # Start receiving data from the client
    Cli_Sock, addr = Serv_Sock.accept() # Accept a connection from client

    message = Cli_Sock.recv(1024) #Recieves data from Socket

    splitMessage = message.split()
    if not '127.0.0.1' in splitMessage[1]:
        Cli_Sock.send("Connection Established\n\n")
        Cli_Sock.close()
        continue

    if len(splitMessage) <= 1:
        continue
    thread.start_new_thread(caching_object,(splitMessage, Cli_Sock))
