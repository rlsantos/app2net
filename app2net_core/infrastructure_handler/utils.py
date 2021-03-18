import pexpect
import time

class RemoteConnection:
    def __init__(self, *commands):
        print("Running:", commands[0])
        a = self.connection = pexpect.spawn(commands[0])
        print(a)
        for command in commands[1:]:
            a = self.connection.sendline(command)
            print(a)

    def run(self, command):
        a = self.connection.sendline(command)
        print(a)
        


if __name__ == "__main__":
    commands = input().split(" , ")
    a = RemoteConnection(*commands)
    while True:
        k = input("command to run")
        a.run(k)
