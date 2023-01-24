from logging import exception
import xmlrpc.client
from xmlrpc.server import SimpleXMLRPCServer
import time
from threading import Thread
import threading
import sys, traceback



class Controller:
    def __init__(self):
        self.server_nodes = []
        self.file = None  # open("trans_controller.log", "a+")
        self.server_nodes_add = []
        self.lock = threading.Lock()
        self.jsonres = {}
        self.instance = 0
        self.isRecover = 0
        self.flag = False
        

    

    def Object(self, case, number):
        new_thread = Thread(target=self.post, args=(case, number))
        new_thread.start()
        return True
    
    def req(self, number, instance):
        num=str(number)
        print("Response is " + num)
        self.jsonres[instance] = number
        return True

    def post(self, case, number):
        print("Entering into the transaction controller")
        self.file = open("trans_controller.log", "a+")
        self.instance = self.instance + 1
        self.file.write("\nTransaction " + str(self.instance) + " post " + case + " " + number + "\n")
        self.file.close()
        print("Transaction " + str(self.instance) + " post " + case + " " + number + "\n")
        count = 0
        for item in self.server_nodes:
            item.log_change("post", case, number, self.instance)

        key_value=int(case)
        if key_value == 3:
            time.sleep(20)

        print("Setting " + str(self.instance) + " post" + " " + case + " " + number + "\n")
        for item in self.server_nodes:
            item.setting("post", case, number, self.instance)

        self.wait()
        node1 = False
        node2 = False
        tran_1 = '1server' + str(self.instance)
        tran_2 = '2server' + str(self.instance)
        if tran_1 in self.jsonres:
            node1 = self.jsonres[tran_1]
        if tran_2 in self.jsonres:
            node2 = self.jsonres[tran_2]
        # abort scenario
        if node1 and node2:
            print("Commit " + str(self.instance) + " post" + " " + case + " " + number + "\n")
            self.file = open("trans_controller.log", "a+")
            self.file.write("\nCommit " + str(self.instance) + " post" + " " + case + " " + number + " server " + str(count))
            self.file.close()
            try:
                self.com()
            except:
                print(" ")
        else:
            self.aborting(self.instance)
            self.file = open("trans_controller.log", "a+")
            self.file.write("\nAborting " + str(self.instance) + "\n")
            self.file.close()
            return "Aborting"

        return "Operation Done."

    def wait(self):
        for i in range(0,11):
            print("Standby ... " + str(i))
            time.sleep(1)

    

    def aborting(self, instance):
        print("All the nodes are getting aborted")
        for item in self.server_nodes:
            item.aborting(instance)
        return True

   
    def com(self):
        print("All nodes getting committed")
        for item in self.server_nodes:
            item.com()
        return True

def main():
    controller = Controller()

    server_nodes_add = ["http://localhost:5001", "http://localhost:5002"]
    for add in server_nodes_add:
        try:
            registery = xmlrpc.client.ServerProxy(add)
            print(registery)
        except Exception:
            print("Wrong one")

        controller.server_nodes.append(registery)

    try:
        server = SimpleXMLRPCServer(("localhost", 5003))
        print("TC listening on 5003")

        print("starting the transaction ")
        res = controller.Object("3", "Test_case")
        print(str(res) + "\n")
    # TC goes down before prepare message (TC fail)
    # res = controller.Object("3", "Test_case")
    # print(str(res) + "\n")

    # during voting one of the server says no to change
    # res = controller.Object("2", "Test_case")
    # print(str(res) + "\n")

    # during voting one fails
    #  res = controller.Object("1", "Test_case")
    #  print(str(res) + "\n")

    # during voting both say no .. tends to abort
    #res = controller.Object("4", "Test_case")
    #print(str(res) + "\n")



        server.register_instance(controller)
        server.serve_forever()

    except Exception:
       print("except")

   

if __name__ == '__main__':
    main()
