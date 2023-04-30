import os
import django
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from channels.layers import get_channel_layer
from channels.generic.websocket import AsyncWebsocketConsumer, AsyncJsonWebsocketConsumer
import json
from asgiref.sync import sync_to_async, async_to_sync

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()
from tictactoe_server.models import Room, Player

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await sync_to_async(django.setup)()
        await self.accept()

    async def disconnect(self, close_code):
        pass

    @sync_to_async
    def create_room(self, room_id_param, player1, name):
        room = Room.objects.create(code=room_id_param)
        player = Player.objects.create(player=player1, name=name)
        room.players.add(player)
        return room

    @sync_to_async
    def join_room(self, room_id_param, player2, name):
        room = Room.objects.get(code=room_id_param)
        player = Player.objects.create(player=player2, name=name)
        room.players.add(player)
        return room

    @sync_to_async
    def get_room(self, room_id_param):
        room = Room.objects.get(code=room_id_param)

        return room

    @sync_to_async
    def delete_room(self, room_id_param):
        isDeleted = False
        try:
            room = Room.objects.get(code=room_id_param)
            players = list(room.players.all())
            player1 = players[0].name
            player2 = players[1].name
            delete_player1 = Player.objects.get(name=player1)
            delete_player2 = Player.objects.get(name=player2)
            delete_player1.delete()
            delete_player2.delete()
            room.delete()
            isDeleted = True
        except Room.DoesNotExist:
            isDeleted = True
        return isDeleted

    @sync_to_async
    def update_board(self, room_id_param, index, symbol):
        room = Room.objects.get(code=room_id_param)
        board = room.displayXO
        board[index] = symbol

        return board

    @sync_to_async
    def update_room(self, room_id_param, board):
        room = Room.objects.get(code=room_id_param)
        room.displayXO = board

        return room

    @sync_to_async
    def check_winner(self, room_id_param):
        winnerFound = False
        game_over = False
        room = Room.objects.get(code=room_id_param)
        board = room.displayXO
        room.filledBox += 1
        room.save()
        if(board[0] == board[1] and board[0] == board[2] and board[0] != ''):
            winnerFound = True
            game_over = True
            print('X wins')
            if(board[0] == 'X'):
                async_to_sync(self.send_results)(room, 'Player X')
            else:
                async_to_sync(self.send_results)(room, 'Player O')

        if (board[3] == board[4] and board[3] == board[5] and board[3] != ''):
            winnerFound = True
            game_over = True
            print('X wins')
            if (board[3] == 'X'):
                async_to_sync(self.send_results)(room, 'Player X')
            else:
                async_to_sync(self.send_results)(room, 'Player O')

        if (board[6] == board[7] and board[6] == board[8] and board[6] != ''):
            winnerFound = True
            game_over = True
            print('X wins')
            if (board[6] == 'X'):
                async_to_sync(self.send_results)(room, 'Player X')
            else:
                async_to_sync(self.send_results)(room, 'Player O')

        if (board[0] == board[4] and board[0] == board[8] and board[0] != ''):
            winnerFound = True
            game_over = True
            print('X wins')
            if (board[0] == 'X'):
                async_to_sync(self.send_results)(room, 'Player X')
            else:
                async_to_sync(self.send_results)(room, 'Player O')

        if (board[2] == board[4] and board[2] == board[6] and board[2] != ''):
            winnerFound = True
            game_over = True
            print('X wins')
            if (board[2] == 'X'):
                async_to_sync(self.send_results)(room, 'Player X')
            else:
                async_to_sync(self.send_results)(room, 'Player O')

        if (board[0] == board[3] and board[0] == board[6] and board[0] != ''):
            winnerFound = True
            game_over = True
            print('X wins')
            if (board[0] == 'X'):
                async_to_sync(self.send_results)(room, 'Player X')
            else:
                async_to_sync(self.send_results)(room, 'Player O')

        if (board[1] == board[4] and board[1] == board[7] and board[1] != ''):
            winnerFound = True
            game_over = True
            print('X wins')
            if (board[1] == 'X'):
                async_to_sync(self.send_results)(room, 'Player X')
            else:
                async_to_sync(self.send_results)(room, 'Player O')

        if (board[2] == board[5] and board[2] == board[8] and board[2] != ''):
            winnerFound = True
            game_over = True
            print('X wins')
            if (board[2] == 'X'):
                async_to_sync(self.send_results)(room, 'Player X')
            else:
                async_to_sync(self.send_results)(room, 'Player O')

        if(winnerFound == False and room.filledBox == 9):
            game_over = True
            async_to_sync(self.send_results)(room, 'Ничья')


        return game_over


    async def send_results(self, room, winner):
        players = await sync_to_async(list)(room.players.all())
        gamers = ['Player X', 'Player O']
        results = {
                'type': 'game_over',
                'winner': winner,
                'board': room.displayXO,
                'room_id': room.code,
            }

        for i in range(2):
            print('Player name: ', players[i].name)
            await self.channel_layer.group_send(
                players[i].name,
                {
                    'type': 'send_data',
                    'text_data': json.dumps(results),
                    'player_channel_name': players[i].player,
                }
            )

    async def send_changes(self, room, data):
        players = await sync_to_async(list)(room.players.all())
        gamers = ['Player X', 'Player O']
        new_data = [
            {
                'type': 'start_game',
                'board': room.displayXO,
                'you': gamers[0],
                'xTurn': data['xTurn'],
                'room_id': room.code,
            },
            {
                'type': 'start_game',
                'board': room.displayXO,
                'you': gamers[1],
                'xTurn': data['xTurn'],
                'room_id': room.code,
            }
        ]
        for i in range(2):
            print('Player name: ', players[i].name)
            await self.channel_layer.group_send(
                players[i].name,
                {
                    'type': 'send_data',
                    'text_data': json.dumps(new_data[i]),
                    'player_channel_name': players[i].player,
                }
            )

    async def start_game(self, room):
        players = await sync_to_async(list)(room.players.all())
        gamers = ['Player X', 'Player O']
        initial = [
            {
                'type': 'start_game',
                'board': ['', '', '', '', '', '', '', '', ''],
                'you': gamers[0],
                'xTurn': True,
                'room_id': room.code,
            },
            {
                'type': 'start_game',
                'board': ['', '', '', '', '', '', '', '', ''],
                'you': gamers[1],
                'xTurn': True,
                'room_id': room.code,
            }
        ]
        for i in range(2):
            print('Player name: ', players[i].name)
            await self.channel_layer.group_send(
                players[i].name,
                {
                    'type': 'send_data',
                    'text_data': json.dumps(initial[i]),
                    # 'player_channel_name': players[i].player,
                }
            )

    async def send_data(self, event):
        await self.send(text_data=event['text_data'], close=False)

    @sync_to_async
    def check_name(self, name):
        try:
            player = Player.objects.get(name=name)
            return player
        except Player.DoesNotExist:
            return None


    async def receive(self, text_data):
        data = json.loads(text_data)
        channel_layer = get_channel_layer()
        room_id = data['room_id']
        type = data['type']
        name = data['name']
        print(type)
        print(data)

        if data['type'] == 'create_room':
            player = await self.check_name(name)
            if player is not None:

                await self.send(text_data=json.dumps({
                    'type': 'player_exists',
                    'room_id': room_id,
                    'board': ['', '', '', '', '', '', '', '', ''],
                }))
            else:

                room = await self.create_room(room_id, self.channel_name, name)
                await sync_to_async(room.save)()
                players = await sync_to_async(list)(room.players.all())
                await self.channel_layer.group_add(players[0].name, self.channel_name)
                await self.send(text_data=json.dumps({
                    'type': 'room_created',
                    'room_id': room_id,
                    'board': ['', '', '', '', '', '', '', '', ''],
                }))



        elif data['type'] == 'join_room':
            player = await self.check_name(name)
            if player is not None:

                await self.send(text_data=json.dumps({
                    'type': 'player_exists',
                    'room_id': room_id,
                    'board': ['', '', '', '', '', '', '', '', ''],
                }))
            else:

                try:

                    room = await self.join_room(room_id, self.channel_name, name)
                    await sync_to_async(room.save)()
                    players = await sync_to_async(list)(room.players.all())
                    await self.channel_layer.group_add(players[1].name, self.channel_name)


                    if len(players) == 2:
                        await self.start_game(room)





                    playerX = 'Player X'
                    playerO = 'Player O'




                except Room.DoesNotExist:
                    await self.send(text_data=json.dumps({
                        'board': ['', '', '', '', '', '', '', '', ''],
                        'type': 'room_not_found',
                    }))

        elif data['type'] == 'exit':
            delete = await self.delete_room(room_id)
            if delete is True:
                print('Room ', room_id, ' has been deleted')
            else:
                print('Error')

        elif data['type'] == 'start_game':
            print('new: ', data)
            room = await self.get_room(room_id)
            board = await self.update_board(data['room_id'], data['index'], data['symbol'])
            new_room = await self.update_room(data['room_id'], board)
            await sync_to_async(new_room.save)()
            winner = await self.check_winner(room_id)
            if winner is False:
                await self.send_changes(new_room, data)

