import argparse
import sys
import socket
import threading

#board object
#O = open ocean
#S = ship
#H = hit location
#M = miss location
class board:
    def __init__(self):
        self.numShipLocations = 17
        #create empty board
        self.spaces = []
        for i in range(10)
            self.spaces.append([])
            for j in range(10):
                self.spaces(i).append("O")

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

    #return status of location
    def get_location_status(self, x: int, y: int):
        return self.spaces[x][y]

def setup_game(player1Socket: socket.socket, player1Address, player2Socket: socket.socket, player2Address):
    sockets = []
    sockets.append(player1Socket)
    sockets.append(player2Socket)

    sockets[0].send("1end".encode(encoding='utf-8'))
    sockets[1].send("2end".encode(encoding='utf-8'))

    playersInfo = []
    playersInfo.append("")
    playersInfo.append("")

    def get_player_info(playerNum):
        while playersInfo[playerNum].endswith("end") == False:
            playersInfo[playerNum] = playersInfo[playerNum] + sockets[playerNum].recv(1024).decode(encoding='utf-8')
        print("received info from player " + str(playerNum + 1))

    for i in range(2):
        receive_thread = threading.Thread(target=get_player_info, args=(i,), daemon=True)
        receive_thread.start()

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('listen_address')
    parser.add_argument('port_number')

    args = parser.parse_args()

    listen_address = args.listen_address

    try:
        port_number = int(args.port_number)
    except ValueError:
        sys.exit('Port number must be an integer')

    max_port_number = 65535

    if port_number > max_port_number or port_number < 0:
        sys.exit('Port number out of range')

    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind((listen_address, port_number))
    serversocket.listen(5)
    print('listen on {0}:{1}'.format(listen_address, port_number))

    try:
        while True:

            player1Socket, player1address = serversocket.accept()
            print("Got player one's connection")

            player2Socket, player2address = serversocket.accept()
            print("Got player two's connection")

            gameThread = threading.Thread(target=setup_game, args=(player1Socket, player1address, player2Socket, player2address,), daemon=True)
            gameThread.start()

    except KeyboardInterrupt:
        print('Main caught keyboard interrupt')

if __name__== '__main__':
    main()