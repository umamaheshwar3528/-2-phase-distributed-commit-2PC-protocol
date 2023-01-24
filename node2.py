import time
import xmlrpc.client
from xmlrpc.server import SimpleXMLRPCServer
from threading import Thread, Event
import multiprocessing
import sys


stop_event = Event()


class N2:
    def __init__(self):
        print("inside node2")
        self.instance_case = {}
        self.file = None
        self.rec = None
        self.trans_controller = None
        self.prep = {}
        self.abortjson = {}

    def find(self, case):
        key_value=int(case)
        if key_value == 1:
            return True
        elif key_value == 2:
            return True
        elif key_value == 3:
            return True
        elif key_value ==4:
            return False

    def com(self):
        self.file = open("node2.log", "r")
        lastline = None
        lines=self.file.readlines()[-1:]
        for line in self.file.readlines()[-1:]:
            print(line)
            lastline = line
        arr = lastline.split(" ")
        self.file.close()
        self.file = open("node2.log", "a+")
        print(arr)
        if arr[1] == "post":
            self.instance_case[arr[2]] = arr[3]
            print("Updated value" + str(self.instance_case))
            self.file.write("\nCommit " + arr[4])
        self.file.flush()
        self.file.close()
        return True

    def aborting(self, instance):
        self.file = open("node2.log", "a+")
        self.file.write("\n Aborting ")
        self.file.flush()
        self.abortjson[instance] = 1
        return True

    def wait(self,instance):
        for i in range(0,11) :
            print("Standby ... " + str(i))
            time.sleep(1)
        if instance not in self.preparejson:
            print("inside if")
            self.abortjson[instance] = 1
            self.trans_controller.aborting(instance)

    def log_change(self, idreq, case, number, instance):
        print("inside request")
        # self.lock.acquire()
        self.file = open('node2.log', 'a+')
        self.file.write("\nTransaction " + str(instance) + " " + idreq + " " + case + " " + number + "\n")
        self.file.close()
        print("done writing")
        thread_wo = Thread(target=self.wait, args=(instance,))
        thread_wo.start()
        return True

    def setting(self, idreq, case, number, instance):
        self.prep[instance] = 1
        flag = self.find(case)
        self.file = open('node2.log', 'a+')
        self.file.write("\nSetting " + str(instance))
        print("Setting " + idreq + " " + case + " " + number)
        set_thread = Thread(target=self.up_res, args=(idreq, case, number, instance))
        set_thread.start()
        return True

    def ins(inst):
        return str(inst)

    def up_res(self, idreq, case, number, instance):
        flag = self.find(case)
        self.file = open('node2.log', 'a+')
        #time.sleep(25)
        if flag and instance not in self.abortjson:
            #ina=self.ins(instance)
            self.file.write("\nYes " + idreq + " " + case + " " + number + " " + str(instance))
            self.file.close()
            print("Request Accepted")
            true_thread = Thread(target=self.trans_controller.req, args=(True, "2server" + str(instance),))
            true_thread.start()
        else:
            self.file.write("\nNo " + idreq + " " + case + " " + number + " " + str(instance))
            self.file.close()
            false_thread = Thread(target=self.trans_controller.req,args=(False, "1server" + str(instance),))
            false_thread.start()

def main():
    try:

        server = SimpleXMLRPCServer(("localhost", 5002))
        print("server listening on 5002")
        s2 = N2()
        registery = xmlrpc.client.ServerProxy("http://localhost:5003")
        s2.trans_controller = registery
        server.register_instance(s2)
        server.serve_forever()

    except Exception:
        print("Exception")


if __name__ == '__main__':
    main()
