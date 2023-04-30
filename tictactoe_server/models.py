from asgiref.sync import async_to_sync
from django.db import models

# Create your models here.
class Player(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=16)
    player = models.JSONField(null=True)
    def __str__(self):
        return self.name

class Room(models.Model):
    players = models.ManyToManyField(Player)
    code = models.CharField(max_length=10)
    displayXO = models.JSONField(default=['', '', '', '', '', '', '', '', ''])
    filledBox = models.IntegerField(default=0)

    def startGame(self, message):
        player1 = self.players.all()[0]
        player2 = self.players.all()[1]
        playerX = 'Player X'
        playerO = 'Player O'

        player1.player.send(json.dumps({'type': 'start_game', 'board': self.displayXO, 'you': playerX, 'xTurn': True, 'room_id': self.code}))
        player2.player.send(json.dumps({'type': 'start_game', 'board': self.displayXO, 'you': playerO, 'xTurn': True, 'room_id': self.code}))

    def move(self, message):
        player1 = self.players.all()[0].player
        player2 = self.players.all()[1].player
        print('Received message: ', message)
        jsonMessage = json.loads(message)
        index = jsonMessage.get("index")
        symbol = jsonMessage.get("symbol")
        player = jsonMessage.get("you")
        xTurn = jsonMessage.get("xTurn")
        roomID = jsonMessage.get("room_id")
        print('index: ', index)
        self.displayXO[index] = symbol
        print(self.displayXO)

        player1.player.send(json.dumps({'type': 'start_game', 'status': 'ok', 'board': self.displayXO, 'you': 'Player X', 'xTurn': xTurn, 'room_id': roomID}))
        player2.player.send(json.dumps({'type': 'start_game', 'status': 'ok', 'board': self.displayXO, 'you': 'Player O', 'xTurn': xTurn, 'room_id': roomID}))

    def __str__(self):
        return 'Room' + self.code

