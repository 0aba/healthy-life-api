from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import Group
from django.db import models as dj_models
from rest_framework import serializers
from common.utils import Role
from common import validators
from user import models


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ('username',)
        read_only_fields = ('username',)


class ProfileSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(validators=[lambda image: validators.validate_image(image,
                                                                                        1, 64,
                                                                                        200, 200)])
    background = serializers.ImageField(validators=[lambda image: validators.validate_image(image,
                                                                                            5, 64,
                                                                                            1920, 1080)])

    class Meta:
        model = models.User
        fields = ('username', 'first_name', 'last_name', 'about', 'avatar', 'background', 'date_joined',)
        read_only_fields = ('username', 'date_joined',)


class BalanceSerializer(serializers.ModelSerializer):
    balance = serializers.SerializerMethodField(method_name='get_balance')

    class Meta:
        model = models.User
        fields = ('pk', 'balance',)
        read_only_fields = ('pk', 'balance',)

    def get_balance(self, obj):
        return f'{obj.balance} USDT'


class SettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Settings
        fields = (
            'display_bloggers_in_blacklisted',
            'hide_yourself_subscriptions',
            'messages_from_friends_only',
            'receive_notifications_about_discounts',
        )


class SettingsUserSerializer(serializers.ModelSerializer):
    settings = SettingsSerializer(source='settings_fk')

    class Meta:
        model = models.User
        fields = ('username', 'email', 'settings',)
        read_only_fields = ('username',)

    def update(self, instance, validated_data):
        settings_data = validated_data.pop('settings_fk', None)
        instance.email = validated_data.get('email', instance.email)

        if settings_data is not None:
            settings_instance = instance.settings_fk
            settings_instance.display_bloggers_in_blacklisted = settings_data.get(
                'display_bloggers_in_blacklisted', settings_instance.display_bloggers_in_blacklisted
            )
            settings_instance.hide_yourself_subscriptions = settings_data.get(
                'hide_yourself_subscriptions', settings_instance.hide_yourself_subscriptions
            )
            settings_instance.messages_from_friends_only = settings_data.get(
                'messages_from_friends_only', settings_instance.messages_from_friends_only
            )
            settings_instance.receive_notifications_about_discounts = settings_data.get(
                'receive_notifications_about_discounts', settings_instance.receive_notifications_about_discounts
            )

            settings_instance.save()

        instance.save()

        return instance


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('name',)


class UserGroupSerializer(serializers.ModelSerializer):
    group = serializers.ChoiceField(choices=(Role.MODERATOR.value, Role.PHARMACIST.value,))

    class Meta:
        model = models.User
        fields = ('group',)


class FriendSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Friend
        fields = ('user_friend',)
        read_only_fields = ('user_friend',)


class BlackListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.BlackList
        fields = ('in_black_list',)
        read_only_fields = ('in_black_list',)


class AwardSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(validators=[lambda image: validators.validate_image(image,
                                                                                       1, 64,
                                                                                       200, 200)])

    class Meta:
        model = models.Awards
        fields = ('pk', 'image', 'description',)
        read_only_fields = ('pk',)


class AwardUserListSerializer(serializers.ModelSerializer):
    award = AwardSerializer()

    class Meta:
        model = models.AwardsUser
        fields = ('pk', 'time_awarded', 'award',)
        read_only_fields = ('pk', 'time_awarded',)


class AwardUserCreateSerializer(serializers.ModelSerializer):
    award_user = serializers.HiddenField(default=0)
    award = serializers.PrimaryKeyRelatedField(queryset=models.Awards.objects.all())

    class Meta:
        model = models.AwardsUser
        fields = ('pk', 'time_awarded', 'award', 'award_user',)
        read_only_fields = ('pk', 'time_awarded',)


class BanCommunicationSerializer(serializers.ModelSerializer):
    who_banned = serializers.HiddenField(default=serializers.CurrentUserDefault())
    active = serializers.BooleanField(default=True, read_only=True)

    class Meta:
        model = models.BanCommunication
        fields = ('pk', 'who_banned', 'got_banned', 'banned_date', 'ban_time', 'active',)
        read_only_fields = ('pk', 'got_banned', 'banned_date', 'active',)


class ChatSerializer(serializers.Serializer):
    user_with = serializers.PKOnlyObject(pk=serializers.IntegerField())
    last_message = serializers.CharField()
    amount_not_read = serializers.IntegerField(default=0)

    def to_representation(self, id_user_with_chat):
        me = self.context['request'].user

        other_user = models.User.objects.get(pk=id_user_with_chat)

        last_message = models.PrivateMessage.displayed.filter(
            (dj_models.Q(wrote=me) & dj_models.Q(received=other_user)) |
            (dj_models.Q(wrote=other_user) & dj_models.Q(received=me))
        ).order_by('-date_create').first()

        unread_count = models.PrivateMessage.displayed.filter(
            received=me,
            wrote=other_user,
            it_read=False
        ).count()
        return {
            'user_with': id_user_with_chat,
            'last_message_text': last_message.message,
            'amount_not_read': unread_count,
        }


class PrivateMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PrivateMessage
        fields = ('pk', 'received', 'wrote', 'message', 'date_create', 'date_change', 'it_read',)
        read_only_fields = ('pk', 'received', 'wrote', 'date_create', 'date_change', 'it_read',)

    def create(self, validated_data):
        request = self.context.get('request')
        username = request.resolver_match.kwargs.get('username')

        try:
            user = models.User.objects.get(username=username)
        except ObjectDoesNotExist:
            raise serializers.ValidationError({'error': 'user not found'})

        validated_data['wrote'] = request.user
        validated_data['received'] = user

        return super().create(validated_data)


class NotifySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Notifications
        fields = ('pk', 'message', 'date_notify', 'viewed',)
        read_only_fields = ('pk', 'message', 'date_notify', 'viewed',)
