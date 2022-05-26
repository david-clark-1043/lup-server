"""View module for handling requests about games"""
from django.http import HttpResponseServerError
from django.core.exceptions import ValidationError
from rest_framework import permissions

# from rest_framework.permissions import DjangoModelPermissions

from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers, status
from levelupapi.models import Game, Gamer, GameType
from django.db.models import Count, Q

class EditGamePermission(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Instance must have an attribute named `owner`.
        return obj.gamer.id == request.user.id

class GameView(ViewSet):
    """Level up games view"""

    permission_classes = [ EditGamePermission ]
    queryset = Game.objects.none()

    def retrieve(self, request, pk):
        """Handle GET requests for single game

        Returns:
            Response -- JSON serialized game
        """
        try:
            game = Game.objects.get(pk=pk)
            serializer = GameSerializer(game)
            return Response(serializer.data)
        except Game.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

    def list(self, request):
        """Handle GET requests to get all games

        Returns:
            Response -- JSON serialized list of games
        """
        #games = Game.objects.all()
        gamer = Gamer.objects.get(user=request.auth.user)
        games = Game.objects.annotate(
            event_count=Count('events'),
            user_event_count=Count(
                'events',
                filter=Q(events__organizer=gamer)
            )
        )
        # Add in the next 3 lines
        game_type = request.query_params.get('type', None)
        if game_type is not None:
            games = games.filter(game_type_id=game_type)
            
        serializer = GameSerializer(games, many=True)
        return Response(serializer.data)
    
    def create(self, request):
        """Handle POST operations

        Returns
            Response -- JSON serialized game instance
        """
        gamer = Gamer.objects.get(user=request.auth.user)
        serializer = CreateGameSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(gamer=gamer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, pk):
        """Handle PUT requests for a game

        Returns:
            Response -- Empty body with 204 status code
        """
        game = Game.objects.get(pk=pk)
        serializer = CreateGameSerializer(game, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(None, status=status.HTTP_204_NO_CONTENT)
    
    def destroy(self, request, pk):
        game = Game.objects.get(pk=pk)
        self.check_object_permissions(request, game)
        game.delete()
        return Response(None, status=status.HTTP_204_NO_CONTENT)
        


class GameSerializer(serializers.ModelSerializer):
    """JSON serializer for games
    """
    event_count = serializers.IntegerField(default=None)
    user_event_count = serializers.IntegerField(default=None)
    
    class Meta:
        model = Game
        fields = ('id', 'game_type', 'title', 'maker',
                  'gamer', 'number_of_players', 'skill_level',
                  'event_count', 'user_event_count')
        depth = 1

class CreateGameSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Game
        fields = ['id', 'title', 'maker', 'number_of_players', 'skill_level', 'game_type']