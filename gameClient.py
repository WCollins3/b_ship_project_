import socket

#board object
#O = open ocean
#S = ship
#H = hit location
#M = miss location
class Board:
    def __init__(self):
        self.numShipLocations = 17
        #create empty board
        self.spaces = []
        for i in range(10):
            self.spaces.append([])
            for j in range(10):
                self.spaces[i].append("O")

    #Put ship location on board
    def set_ship_location(self, x: int, y: int):
        self.spaces[x][y] = "S"

    #Send hit or miss
    def strike(self, x: int, y: int):
        if(self.spaces[x][y] == "O" or self.spaces == "M"):
            self.spaces[x][y] = "M"
        else:
            self.spaces[x][y] = "H"
            self.numShipLocations -= 1

    def set_hit(self, x: int, y: int):
        self.spaces[x][y] = "H"

    def set_miss(self, x: int, y: int):
        self.spaces[x][y] = "M"

    #return status of location
    def get_location_status(self, x: int, y: int):
        return self.spaces[x][y]

    def print_board(self):
        for j in range(10):
            prntstr = ""
            for i in range(10):
                prntstr = prntstr + self.spaces[i][j] + " "
            print(prntstr)
            print(" ")

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

    print("Waiting on other player")

    ready_message = ""
    while ready_message.endswith("end") == False:
        ready_message = ready_message + client_socket.recv(1024).decode(encoding='utf-8') #Game is ready
    print("Game started")

    playerNum = ready_message.split("end")[0]

    myBoard = Board()
    opponentsBoard = Board()

    #put ships on myBoard
    for s in ships:
        for location in s.getShipLocations():
            myBoard.set_ship_location(location[0], location[1])

    def wait_for_turn():
        server_message = ""
        while server_message.endswith("end") == False:
            server_message = server_message + client_socket.recv(1024).decode(encoding='utf-8')
        if server_message == "winend":
            print("You won")
            return
        if server_message == "loseend":
            print("You lost")
            return
        else:
            opponent_attack = server_message.split("end")[0]
            opp_x = int(opponent_attack.split(",")[0])
            opp_y = int(opponent_attack.split(",")[1])
            myBoard.strike(opp_x, opp_y)
            attack()

    def attack():
        #show boards
        print("Attack Board")
        print(" ")
        opponentsBoard.print_board()
        print(" ")
        print("Your Board")
        print(" ")
        myBoard.print_board()
        #get attack info
        print(" ")
        print("enter attack location (x <space> y")
        attack_loc = input().split(" ")
        attack_message = attack_loc[0] + "," +attack_loc[1] + "," + "end"
        client_socket.send(attack_message.encode(encoding='utf-8'))

        response = ""
        while response.endswith("end") == False:
            response = response + client_socket.recv(1024).decode(encoding='utf-8')
        print(" ")
        response = response.split("end")[0]
        print("result: " + response)

        if response == "M":
            opponentsBoard.set_miss(int(attack_loc[0]), int(attack_loc[1]))

        if response == "H":
            opponentsBoard.set_hit(int(attack_loc[0]), int(attack_loc[1]))

        wait_for_turn()

    if playerNum == "1":
        attack()
    else:
        wait_for_turn()


if __name__== '__main__':
    main()