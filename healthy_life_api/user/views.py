from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from common import models as common_models, permissions
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics, viewsets, status
from rest_framework.response import Response
from django.contrib.auth.models import Group
from django.db import models as dj_models
from user import serializers, models
import requests
import jwt
import os


class ProfileAPIView(generics.RetrieveUpdateAPIView):
    queryset = models.User.objects.all()
    serializer_class = serializers.ProfileSerializer
    lookup_field = 'username'

    http_method_names = ('get', 'put',)

    def get(self, request, *args, **kwargs):
        username = kwargs.get('username', None)

        try:
            user = models.User.objects.get(username=username)
        except ObjectDoesNotExist:
            return Response({'error': 'user not found'}, status=status.HTTP_404_NOT_FOUND)

        serialize = self.get_serializer(user)

        return Response(serialize.data, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        username = kwargs.get('username', None)

        try:
            user = models.User.objects.get(username=username)
        except ObjectDoesNotExist:
            return Response({'error': 'user not found'}, status=status.HTTP_404_NOT_FOUND)

        if request.user != user:
            return Response({'error': 'you can\'t change someone else\'s profile'},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SettingsAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = models.User.objects.all()
    serializer_class = serializers.SettingsUserSerializer
    lookup_field = 'username'

    http_method_names = ('get', 'put',)

    def get(self, request, *args, **kwargs):
        username = kwargs.get('username', None)

        try:
            user = models.User.objects.select_related('settings_fk').get(username=username)
        except ObjectDoesNotExist:
            return Response({'error': 'not found user'}, status=status.HTTP_404_NOT_FOUND)

        if request.user != user and not request.user.is_superuser:
            return Response({'error': 'you can\'t see other people\'s settings'},
                            status=status.HTTP_403_FORBIDDEN)

        return super().get(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        username = kwargs.get('username', None)

        try:
            user = models.User.objects.get(username=username)
        except ObjectDoesNotExist:
            return Response({'error': 'not found user'}, status=status.HTTP_404_NOT_FOUND)

        if request.user != user:
            return Response({'error': 'you can\'t change other people\'s settings'},
                            status=status.HTTP_403_FORBIDDEN)

        return super().put(request, *args, **kwargs)


class GroupAPIView(generics.ListAPIView,
                   generics.DestroyAPIView,
                   generics.CreateAPIView):
    serializer_class = serializers.UserGroupSerializer
    permission_classes = (IsAdminUser,)

    http_method_names = ('get', 'post', 'delete',)

    def get_queryset(self):
        return models.User.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return serializers.GroupSerializer
        return serializers.UserGroupSerializer

    def get(self, request, *args, **kwargs):
        username = kwargs.get('username', None)

        try:
            user = models.User.objects.prefetch_related('groups').get(username=username)
        except ObjectDoesNotExist:
            return Response({'error': 'not found user'}, status=status.HTTP_404_NOT_FOUND)

        group_user = user.groups.all()
        serializer = self.get_serializer(group_user, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        username = kwargs.get('username', None)

        try:
            user = models.User.objects.get(username=username)
        except ObjectDoesNotExist:
            return Response({'error': 'not found user'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        group_name = serializer.validated_data['group']

        if group_name not in ('Модератор', 'Фармацевт',):
            return Response({'error': f'group does not exist "{group_name}"'}, status=status.HTTP_400_BAD_REQUEST)

        group = Group.objects.get(name=group_name)
        user.groups.add(group)

        return Response({'message': f'successfully added to the group "{group_name}"'}, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        username = kwargs.get('username', None)

        try:
            user = models.User.objects.get(username=username)
        except ObjectDoesNotExist:
            return Response({'error': 'not found user'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        group_name = serializer.validated_data['group']

        if group_name not in ('Модератор', 'Фармацевт',):
            return Response({'error': f'group does not exist "{group_name}"'}, status=status.HTTP_400_BAD_REQUEST)

        group = Group.objects.get(name=group_name)
        user.groups.remove(group)

        return Response({'message': f'successfully removed from group "{group}"'}, status=status.HTTP_204_NO_CONTENT)


class FriendAPIView(generics.ListAPIView,
                    generics.DestroyAPIView,
                    generics.CreateAPIView):
    serializer_class = serializers.FriendSerializer
    permission_classes = (IsAuthenticated,)

    http_method_names = ('get', 'post', 'delete',)

    def get_queryset(self):
        return models.Friend.objects.all()

    def get_permissions(self):
        if self.request.method == 'GET':
            return (AllowAny(),)

        return (permission() for permission in self.permission_classes)

    def get(self, request, *args, **kwargs):
        username = kwargs.get('username', None)

        try:
            user = models.User.objects.get(username=username)
        except ObjectDoesNotExist:
            return Response({'error': 'not found user'}, status=status.HTTP_404_NOT_FOUND)

        # info! полноценно друзь только если оба добавили друг друга
        friends_user = models.Friend.objects.filter(friends_user=user).all()
        serializer = self.get_serializer(friends_user, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        username = kwargs.get('username', None)
        me = request.user

        try:
            new_friend = models.User.objects.get(username=username)
        except ObjectDoesNotExist:
            return Response({'error': 'not found user'}, status=status.HTTP_404_NOT_FOUND)

        if me == new_friend:
            return Response({'error': 'you can\'t add yourself as a friend'}, status=status.HTTP_400_BAD_REQUEST)

        if models.BlackList.objects.filter(user_black_list=new_friend, in_black_list=me).exists():
            return Response({'error': f'you are blacklisted {new_friend}'}, status=status.HTTP_403_FORBIDDEN)

        if models.Friend.objects.filter(friends_user=me, user_friend=new_friend).exists():
            return Response({'message': f'you have already sent a friend request {new_friend}'},
                            status=status.HTTP_400_BAD_REQUEST)

        models.Friend.objects.create(friends_user=me, user_friend=new_friend)

        return Response({'message': f'you sent a friend request to a user {new_friend}'},
                        status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        username = kwargs.get('username', None)

        try:
            del_friend = models.User.objects.get(username=username)
        except ObjectDoesNotExist:
            return Response({'error': 'not found user'}, status=status.HTTP_404_NOT_FOUND)

        me = request.user

        if me == del_friend:
            return Response({'error': 'you can\'t be your own friend'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            models.Friend.objects.get(friends_user=me, user_friend=del_friend).delete()
        except ObjectDoesNotExist:
            return Response({'error': f'you are not friends with {del_friend}'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': f'you have successfully removed from friends {del_friend}'},
                        status=status.HTTP_200_OK)


class BlackListAPIView(generics.ListAPIView,
                       generics.DestroyAPIView,
                       generics.CreateAPIView):
    serializer_class = serializers.BlackListSerializer
    permission_classes = (IsAuthenticated,)

    http_method_names = ('get', 'post', 'delete',)

    def get_queryset(self):
        return models.BlackList.objects.all()

    def get(self, request, *args, **kwargs):
        username = kwargs.get('username', None)

        try:
            user = models.User.objects.get(username=username)
        except ObjectDoesNotExist:
            return Response({'error': 'user not found'}, status=status.HTTP_404_NOT_FOUND)

        me = request.user

        if me != user and not me.is_superuser:
            return Response({'error': 'You can\'t see someone else\'s blacklist'}, status=status.HTTP_403_FORBIDDEN)

        blacklist_user = models.BlackList.objects.filter(user_black_list=user).all()
        serializer = self.get_serializer(blacklist_user, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        username = kwargs.get('username', None)

        try:
            new_user_bl = models.User.objects.get(username=username)
        except ObjectDoesNotExist:
            return Response({'error': 'user not found'}, status=status.HTTP_404_NOT_FOUND)

        me = request.user

        if me == new_user_bl:
            return Response({'error': 'you can\'t add yourself to your blacklist'}, status=status.HTTP_400_BAD_REQUEST)

        if models.BlackList.objects.filter(user_black_list=me, in_black_list=new_user_bl).exists():
            return Response({'error': f'you have already added to the blacklist {new_user_bl}'},
                            status=status.HTTP_400_BAD_REQUEST)

        models.BlackList.objects.create(user_black_list=me, in_black_list=new_user_bl)

        return Response({'message': f'you have successfully added {new_user_bl} to the blacklist'},
                        status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        username = kwargs.get('username', None)

        try:
            del_user_bl = models.User.objects.get(username=username)
        except ObjectDoesNotExist:
            return Response({'error': 'user not found'}, status=status.HTTP_404_NOT_FOUND)

        me = request.user

        if me == del_user_bl:
            return Response({'error': 'you can\'t be on your blacklist'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            models.BlackList.objects.get(user_black_list=me, in_black_list=del_user_bl).delete()
        except ObjectDoesNotExist:
            return Response({'error': f'not in the blacklist {del_user_bl}'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': f'you have successfully removed from the blacklist {del_user_bl}'},
                        status=status.HTTP_200_OK)


class AwardViewSet(viewsets.ModelViewSet):
    queryset = models.Awards.objects.all()
    serializer_class = serializers.AwardSerializer
    permission_classes = (IsAdminUser,)
    lookup_field = 'pk'

    http_method_names = ('get', 'post', 'put', 'delete',)

    def get_permissions(self):
        if self.request.method == 'GET':
            return (permissions.IsModeratorOrSuperUser(),)

        return (permission() for permission in self.permission_classes)

    def get_queryset(self):
        return models.Awards.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get('pk', None)

        try:
            award = models.Awards.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return Response({'error': 'not found award'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(award)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_award = serializer.save()

        return Response({'message': f'reward successfully created {new_award}'}, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except ObjectDoesNotExist:
            return Response({'error': 'not found award'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        updated_award = serializer.save()

        return Response({'message': f'reward successfully created {updated_award}'}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        pk = kwargs.get('pk', None)

        try:
            models.Awards.objects.get(pk=pk).delete()
        except ObjectDoesNotExist:
            return Response({'error': 'not found award'}, status=status.HTTP_404_NOT_FOUND)

        return Response({'message': f'reward @\'{pk}\' was successfully removed'}, status=status.HTTP_204_NO_CONTENT)


class AwardUserViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsModeratorOrSuperUser,)
    serializer_class = serializers.AwardUserListSerializer

    http_method_names = ('get', 'post', 'delete',)

    def get_queryset(self):
        return models.AwardsUser.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return serializers.AwardUserListSerializer
        elif self.request.method == 'POST':
            return serializers.AwardUserCreateSerializer
        return serializers.AwardUserListSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return (AllowAny(),)

        return (permission() for permission in self.permission_classes)

    def list(self, request, *args, **kwargs):
        username = kwargs.get('username', None)

        try:
            user = models.User.objects.get(username=username)
        except ObjectDoesNotExist:
            return Response({'error': 'user not found'}, status=status.HTTP_404_NOT_FOUND)

        award_user = models.AwardsUser.objects.filter(award_user=user).all()

        serializer = self.serializer_class(award_user, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        username = kwargs.get('username', None)
        pk = kwargs.get('pk', None)

        try:
            user = models.User.objects.get(username=username)
        except ObjectDoesNotExist:
            return Response({'error': 'user not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            award = models.AwardsUser.objects.get(award_user=user, pk=pk)
        except ObjectDoesNotExist:
            return Response({'error': 'award user not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(award)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        username = kwargs.get('username', None)

        try:
            user = models.User.objects.get(username=username)
        except ObjectDoesNotExist:
            return Response({'error': 'user not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data['award_user'] = user

        award_user = serializer.save()

        return Response({'message': f'user {user} received an award {award_user.award}'},
                        status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        username = kwargs.get('username', None)
        pk = kwargs.get('pk', None)

        try:
            user = models.User.objects.get(username=username)
        except ObjectDoesNotExist:
            return Response({'error': 'user not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            models.AwardsUser.objects.get(award_user=user, pk=pk).delete()
        except ObjectDoesNotExist:
            return Response({'error': f'User {user} does not have such award'}, status=status.HTTP_404_NOT_FOUND)

        return Response({'message': f'the award was successfully removed from {user}'},
                        status=status.HTTP_204_NO_CONTENT)


class BanCommunicationViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsModeratorOrSuperUser,)
    serializer_class = serializers.BanCommunicationSerializer
    lookup_field = 'pk'

    http_method_names = ('get', 'post', 'delete',)

    def get_queryset(self):
        return models.BanCommunication.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = serializers.BanCommunicationSerializer(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get('pk', None)

        try:
            ban = models.BanCommunication.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return Response({'error': 'not found ban'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(ban)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        username = kwargs.get('username', None)

        try:
            user = models.User.objects.get(username=username)
        except ObjectDoesNotExist:
            return Response({'error': 'user not found'}, status=status.HTTP_404_NOT_FOUND)

        me = request.user

        if me == user:
            return Response({'error': 'you can\'t block yourself'}, status=status.HTTP_400_BAD_REQUEST)

        if (user.groups.filter(dj_models.Q(name='Модератор') | dj_models.Q(name='Фармацевт')).exists() or
                user.is_superuser):
            return Response({'error': 'you can\'t block staff'}, status=status.HTTP_400_BAD_REQUEST)

        if models.BanCommunication.objects.filter(got_banned=user, active=True).exists():
            return Response({'error': 'user is already banned'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data['who_banned'] = me
        serializer.validated_data['got_banned'] = user

        serializer.save()

        return Response({'message': f'user {user} has been blocked'}, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        username = kwargs.get('username', None)

        try:
            unbanned = models.User.objects.get(username=username)
        except ObjectDoesNotExist:
            return Response({'error': 'user not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            ban = models.BanCommunication.objects.get(got_banned=unbanned, active=True)
        except ObjectDoesNotExist:
            return Response({'error': 'the user has no blocked'}, status=status.HTTP_404_NOT_FOUND)

        ban.active = False
        ban.save()

        return Response({'message': f'user {unbanned} unblocked'}, status=status.HTTP_204_NO_CONTENT)


class ChatListAPIView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = models.PrivateMessage.objects.all()
    serializer_class = serializers.ChatSerializer

    def list(self, request, *args, **kwargs):
        wrote = models.PrivateMessage.objects.filter(received=request.user).values_list('wrote', flat=True)
        receive = models.PrivateMessage.objects.filter(wrote=request.user).values_list('received', flat=True)
        chat_with = wrote.union(receive)

        chat_data = []
        for user in chat_with:
            chat_data.append(serializers.ChatSerializer(user, context={'request': request}).data)

        return Response(chat_data, status=status.HTTP_200_OK)


class PrivateMessageViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = models.PrivateMessage.displayed.all()
    serializer_class = serializers.PrivateMessageSerializer

    http_method_names = ('get', 'post', 'put', 'patch', 'delete',)

    def get_queryset(self):
        return models.PrivateMessage.displayed.all()

    def list(self, request, *args, **kwargs):
        username = kwargs.get('username', None)

        try:
            other_user = models.User.objects.get(username=username)
        except ObjectDoesNotExist:
            return Response({'error': 'not found user'}, status=status.HTTP_404_NOT_FOUND)

        me = request.user

        messages = models.PrivateMessage.displayed.filter(
            (dj_models.Q(wrote=other_user) & dj_models.Q(received=me)) |
            (dj_models.Q(wrote=me) & dj_models.Q(received=other_user))
        ).order_by('date_create')

        serializer = serializers.PrivateMessageSerializer(messages, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        username = kwargs.get('username', None)
        me = request.user

        try:
            other_user = models.User.objects.select_related('settings_fk').get(username=username)
        except ObjectDoesNotExist:
            return Response({'error': 'not found user'}, status=status.HTTP_404_NOT_FOUND)

        if models.BlackList.objects.filter(user_black_list=other_user, in_black_list=me).exists():
            return Response({'error': f'you are blacklisted {other_user}'}, status=status.HTTP_403_FORBIDDEN)

        if models.BanCommunication.objects.filter(got_banned=me, active=True).exists():
            return Response({'error': 'you can\'t send a message if you are blocked'}, status=status.HTTP_403_FORBIDDEN)

        if (other_user.settings_fk.messages_from_friends_only and not (
                models.Friend.objects.filter(friends_user=other_user, user_friend=me).exists() and
                models.Friend.objects.filter(friends_user=me, user_friend=other_user).exists())):
            return Response({'error': 'user accepts messages only from friends'}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(wrote=me, received=other_user)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get('pk', None)
        user = request.user

        try:
            message = models.PrivateMessage.displayed.get(pk=pk)
        except ObjectDoesNotExist:
            return Response({'error': 'message not found'}, status=status.HTTP_404_NOT_FOUND)

        if message.received != user and message.wrote != user:
            return Response({'error': 'you don\'t have rights to other people\'s messages'},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(message)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        pk = kwargs.get('pk', None)
        me = request.user

        try:
            message = self.get_queryset().get(pk=pk)
        except ObjectDoesNotExist:
            return Response({'error': 'message not found'}, status=status.HTTP_404_NOT_FOUND)

        if message.wrote != me:
            return Response({'error': 'only the person who wrote the message can change it'},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(message, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        pk = kwargs.get('pk', None)
        me = request.user

        try:
            message = self.get_queryset().get(pk=pk)
        except ObjectDoesNotExist:
            return Response({'error': 'message not found'}, status=status.HTTP_404_NOT_FOUND)

        if message.received != me:
            return Response({'error': 'you can\'t mark a message as read by a recipient who is someone else'},
                            status=status.HTTP_403_FORBIDDEN)

        message.it_read = True
        message.save()

        serializer = self.get_serializer(message, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        pk = kwargs.get('pk', None)
        me = request.user

        try:
            message = self.get_queryset().get(pk=pk)
        except ObjectDoesNotExist:
            return Response({'error': 'message not found'}, status=status.HTTP_404_NOT_FOUND)

        if message.wrote != me:
            return Response({'error': 'only the one who created it can delete their message'},
                            status=status.HTTP_403_FORBIDDEN)

        message.status = common_models.StatusMessage.DELETED
        message.save()

        return Response({'message': f'message {message} was successfully deleted'}, status=status.HTTP_204_NO_CONTENT)


class NotificationViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = models.Notifications.objects.all()
    serializer_class = serializers.NotifySerializer

    http_method_names = ('get', 'patch', 'delete',)

    def get_queryset(self):
        return models.Notifications.objects.all()

    def list(self, request, *args, **kwargs):
        username = kwargs.get('username', None)

        try:
            user = models.User.objects.get(username=username)
        except ObjectDoesNotExist:
            return Response({'error': 'not found user'}, status=status.HTTP_404_NOT_FOUND)

        if request.user != user and not request.user.is_superuser:
            return Response({'error': 'you can\'t see other people\'s notifications'},
                            status=status.HTTP_403_FORBIDDEN)

        queryset = self.get_queryset().filter(user_notify=user)
        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get('pk', None)

        try:
            notify = self.get_queryset().get(user_notify=request.user, pk=pk)
        except ObjectDoesNotExist:
            return Response({'error': 'not found notify'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(notify)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        pk = kwargs.get('pk', None)

        try:
            notify = models.Notifications.objects.get(user_notify=request.user, pk=pk)
        except ObjectDoesNotExist:
            return Response({'error': 'not found notify'}, status=status.HTTP_404_NOT_FOUND)

        notify.viewed = True
        notify.save()

        return Response({'message': f'now read {notify}'}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        pk = kwargs.get('pk', None)

        try:
            notify = models.Notifications.objects.get(user_notify=request.user, pk=pk)
        except ObjectDoesNotExist:
            return Response({'error': 'not found notify'}, status=status.HTTP_404_NOT_FOUND)

        str_notify = f'{notify}'
        notify.delete()

        return Response({'error': f'{str_notify} notification successfully removed'}, status=status.HTTP_204_NO_CONTENT)


class CryptoCloudViewAPI(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)

    def get_balance(self, request, *args, **kwargs):
        me = request.user
        serializer = serializers.BalanceSerializer(me)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def top_up_balance(self, request, *args, **kwargs):
        replenishment_amount = request.data.get('replenishment_amount', None)
        me = request.user

        if replenishment_amount is None:
            return Response({'error': 'replenishment amount is missing'}, status=status.HTTP_400_BAD_REQUEST)

        if replenishment_amount <= 0:
            return Response({'error': 'replenishment amount is negative'}, status=status.HTTP_400_BAD_REQUEST)

        if not (models.User.MINIMUM_REPLENISHMENT_AT_ONE_TIME <=
                replenishment_amount <= models.User.MAXIMUM_REPLENISHMENT_AT_ONE_TIME):
            return Response({'error': f'the replenishment amount must be between '
                                      f'{models.User.MINIMUM_REPLENISHMENT_AT_ONE_TIME} and '
                                      f'{models.User.MAXIMUM_REPLENISHMENT_AT_ONE_TIME}'},
                            status=status.HTTP_400_BAD_REQUEST)

        new_cryptocloud_invoice = self.cryptocloud_create_invoice(me, replenishment_amount)

        return Response(new_cryptocloud_invoice[0], status=new_cryptocloud_invoice[1])

    @staticmethod
    def cryptocloud_create_invoice(user, replenishment_amount):
        url = 'https://api.cryptocloud.plus/v2/invoice/create'
        headers = {
            'Authorization': f'Token {os.getenv('API_KEY_CRYPTO_CLOUD')}',
            'Content-Type': 'application/json'
        }
        data = {
            'amount': replenishment_amount,
            'shop_id': os.getenv('SHOP_ID'),
            'order_id': f'{user}'
        }

        response = requests.post(url, headers=headers, json=data)
        response_json = response.json()

        if response.status_code == 200:
            return response_json['result']['link'], status.HTTP_201_CREATED
        return response_json, response.status_code

    def successful_payment(self, request, *args, **kwargs):
        status_payment = request.data.get('status')
        invoice_id = request.data.get('invoice_id')
        amount_crypto = request.data.get('amount_crypto')
        order_id = request.data.get('order_id')
        token = request.data.get('token')

        username = order_id.strip('@\'')

        try:
            user = models.User.objects.get(username=username)
        except ObjectDoesNotExist:
            return Response({'error': 'not found user'}, status=status.HTTP_404_NOT_FOUND)

        if status_payment == 'success':
            try:
                payload: dict = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=('HS256',))
                if payload['id'] == invoice_id:
                    return Response({'error': 'invoice error'}, status=status.HTTP_400_BAD_REQUEST)
            except jwt.ExpiredSignatureError:
                return Response({'error': 'token is expired'}, status=status.HTTP_400_BAD_REQUEST)
            except jwt.InvalidTokenError:
                return Response({'error': 'token is invalid'}, status=status.HTTP_400_BAD_REQUEST)

            user.balance += amount_crypto
            user.save()
            return Response({'message': 'payment successful'}, status=status.HTTP_201_CREATED)

        return Response({'error': 'payment failed'}, status=status.HTTP_400_BAD_REQUEST)
