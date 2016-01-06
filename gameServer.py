import argparse
import sys
import socket
import threading

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

    #return status of location
    def get_location_status(self, x: int, y: int):
        return self.spaces[x][y]

    def get_board_health(self):
        return self.numShipLocations

def setup_game(player1Socket: socket.socket, player1Address, player2Socket: socket.socket, player2Address):
    sockets = []
    sockets.append(player1Socket)
    sockets.append(player2Socket)

    sockets[0].send("1end".encode(encoding='utf-8'))
    sockets[1].send("2end".encode(encoding='utf-8'))

    playersInfo = []
    playersInfo.append("")
    playersInfo.append("")

    boards = []
    boards.append(Board())
    boards.append(Board())

    playerReady = []
    playerReady.append(False)
    playerReady.append(False)

    def get_player_info(playerNum):
        while playersInfo[playerNum].endswith("end") == False:
            playersInfo[playerNum] = playersInfo[playerNum] + sockets[playerNum].recv(1024).decode(encoding='utf-8')
        print("received info from player " + str(playerNum + 1))

        #get ship locations from client message
        ship_locations = []
        for i in range(len(playersInfo[playerNum].split("+")) - 1):
            elem = playersInfo[playerNum].split("+")[i]
            x_val = int(elem[1])
            y_val = int(elem[3])
            ship_locations.append((x_val, y_val))

        #set board locations
        for loc in ship_locations:
            boards[playerNum].set_ship_location(loc[0], loc[1])

        playerReady[playerNum] = True

        return

    for i in range(2):
        receive_thread = threading.Thread(target=get_player_info, args=(i,), daemon=True)
        receive_thread.start()

    while True:
        if(playerReady[0] == True and playerReady[1] == True):
            gameThread = threading.Thread(target=playGame, args=(sockets[0], player1Address, sockets[1], player2Address, boards[0], boards[1]), daemon=True)
            gameThread.start()
            return

def playGame(player1Socket: socket.socket, player1Address, player2Socket: socket.socket, player2Address, board1: Board, board2: Board):
    sockets = []
    sockets.append(player1Socket)
    sockets.append(player2Socket)

    boards = []
    boards.append(board1)
    boards.append(board2)

    #send ready message
    sockets[0].send("1end".encode(encoding='utf-8'))
    sockets[1].send("2end".encode(encoding='utf-8'))

    currPlayer = 0
    currOpponent = 1
    while boards[0].get_board_health() != 0 and boards[1].get_board_health() != 0:
        attack_message = ""
        while attack_message.endswith("end") == False:
            attack_message = attack_message + sockets[currPlayer].recv(1024).decode(encoding='utf-8')
        attack = attack_message.split(",")
        x_att = int(attack[0])
        y_att = int(attack[1])
        boards[currOpponent].strike(x_att, y_att)
        response = boards[currOpponent].get_location_status(x_att, y_att) + "end"
        sockets[currPlayer].send(response.encode(encoding='utf-8'))
        if boards[currOpponent].get_board_health != 0:
            sockets[currOpponent].send(attack_message.encode(encoding='utf-8'))

        #switch players
        temp = currPlayer
        currPlayer = currOpponent
        currOpponent = temp

    if boards[0].get_board_health() == 0:
        sockets[0].send("loseend".encode(encoding='utf-8'))
        sockets[1].send("winend".encode(encoding='utf-8'))
    else:
        sockets[1].send("loseend".encode(encoding='utf-8'))
        sockets[0].send("winend".encode(encoding='utf-8'))




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