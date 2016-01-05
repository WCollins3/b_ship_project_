import socket

class Ship:
    def __init__(self, size: int, x_location: int, y_location: int, direction):
        self.size = size
        self.x_location = x_location
        self.y_location = y_location
        self.direction = direction

        self.spaces = []

        #direction = up
        if self.direction == "up":
            for i in range(self.size):
                self.spaces.append((self.x_location, self.y_location + i))

        #direction = down
        if self.direction == "down":
            for i in range(self.size):
                self.spaces.append((self.x_location, self.y_location - i))

        #direction = right
        if self.direction == "right":
            for i in range(self.size):
                self.spaces.append((self.x_location + i, self.y_location))

        #direction = left
        if self.direction == "left":
            for i in range(self.size):
                self.spaces.append((self.x_location - i, self.y_location))

    def getShipLocations(self):
        return self.spaces

def main():

    print("Enter server IP")
    server_address = input()

    print("Enter server port")
    server_port = int(input())

    print("connecting")

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_address, server_port))

    message = ""
    while(message.endswith("end") == False):
        message = message + client_socket.recv(1024).decode(encoding='utf-8')

    print("Connected to server")

    ships = []

    print("Enter aircraft carrier location (x location <space> y location <space> direction(left, right, up, down))")
    acInfo = input().split(" ")
    ships.append(Ship(5, int(acInfo[0]), int(acInfo[1]), acInfo[2]))

    print("Enter battleship location (x location <space> y location <space> direction(left, right, up, down))")
    bsInfo = input().split(" ")
    ships.append(Ship(4, int(bsInfo[0]), int(bsInfo[1]), bsInfo[2]))

    print("Enter submarine location (x location <space> y location <space> direction(left, right, up, down))")
    subInfo = input().split(" ")
    ships.append(Ship(3, int(subInfo[0]), int(subInfo[1]), subInfo[2]))

    print("Enter Cruiser location (x location <space> y location <space> direction(left, right, up, down))")
    deInfo = input().split(" ")
    ships.append(Ship(3, int(deInfo[0]), int(deInfo[1]), deInfo[2]))

    print("Enter Patrol Boat location (x location <space> y location <space> direction(left, right, up, down))")
    ptInfo = input().split(" ")
    ships.append(Ship(2, int(ptInfo[0]), int(ptInfo[1]), ptInfo[2]))

    #prepare to send ship locations to server
    loc_string = ""
    for boat in ships:
        for loc in boat.getShipLocations():
            loc_string = loc_string + "(" + str(loc[0]) + "," + str(loc[1]) + ")+"
    loc_string = loc_string + "end"

    client_socket.send(loc_string.encode(encoding='utf-8'))

if __name__== '__main__':
    main()