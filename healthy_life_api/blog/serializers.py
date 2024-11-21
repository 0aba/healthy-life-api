from rest_framework import serializers
from blog import models


class PostListSerializer(serializers.ModelSerializer):
    short_text = serializers.SerializerMethodField()
    status = serializers.ChoiceField(
        choices=(
            models.StatusRecord.DRAFT, 'draft',
            models.StatusRecord.PUBLISHED, 'published',
        )
    )

    class Meta:
        model = models.Post
        fields = ('title', 'wrote', 'short_text', 'date_create', 'date_change', 'status',)
        read_only_fields = ('title', 'wrote', 'short_text', 'date_create', 'date_change', 'status',)

    def get_short_text(self, obj):
        limit_len = 64
        text = obj.text

        if len(text) > limit_len:
            return text[:limit_len - 3] + '...'

        return text


class PostSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(
        choices=(
            models.StatusRecord.DRAFT, 'draft',
            models.StatusRecord.PUBLISHED, 'published',
        )
    )

    class Meta:
        model = models.Post
        fields = ('title', 'wrote', 'text', 'date_create', 'date_change', 'status',)
        read_only_fields = ('wrote', 'date_create', 'date_change', 'status',)

    def validate_status(self, value):
        if self.instance and self.instance.status != value:
            if value not in (models.StatusRecord.DRAFT, models.StatusRecord.PUBLISHED,):
                raise serializers.ValidationError('you can only select status DRAFT as 0 or PUBLISHED as 1')
        return value


class GoodsPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PostGoods
        fields = ('goods_post', 'post_with_goods',)
        read_only_fields = ('post_with_goods',)


class PostCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PostComment
        fields = ('pk', 'comment_in_post', 'wrote', 'message', 'date_create', 'date_change',)
        read_only_fields = ('pk', 'comment_in_post', 'wrote', 'date_create', 'date_change',)

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['wrote'] = request.user

        return super().create(validated_data)


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SubscriberBlogUser
        fields = ('blogger', 'subscriber',)
        read_only_fields = ('blogger', 'subscriber',)
