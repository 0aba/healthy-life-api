from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics, viewsets, status
from blog import serializers, models, filters
from rest_framework.response import Response
from common import models as common_models
from django.db import models as dj_models
from user import models as user_models
from django.db import IntegrityError


class PostListAPIView(generics.ListAPIView):
    queryset = models.Post.published.all()
    serializer_class = serializers.PostListSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = filters.AnyPostFilter

    def list(self, request, *args, **kwargs):
        me = request.user
        queryset = self.get_queryset()

        if me.is_authenticated and not me.settings_fk.display_bloggers_in_blacklisted:
            blacklist_ids = user_models.BlackList.objects.filter(user_black_list=me).values('in_black_list')
            queryset = queryset.filter(~dj_models.Q(wrote__in=blacklist_ids))

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class BloggerViewSet(viewsets.ModelViewSet):
    queryset = models.Post.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = filters.BloggerPostFilter

    http_method_names = ('get', 'post', 'put', 'delete',)

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.PostListSerializer

        return serializers.PostSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return (permission() for permission in self.permission_classes)

        return (IsAuthenticated(),)

    @staticmethod
    def get_queryset_blogger(request, blogger_username=None):
        me_username = request.user.username

        if me_username == blogger_username:
            return models.Post.blogger.all()

        return models.Post.published.all()

    def list(self, request, *args, **kwargs):
        blogger_username = kwargs.get('username', None)

        try:
            blogger = user_models.User.objects.get(username=blogger_username)
        except ObjectDoesNotExist:
            return Response({'detail': 'blogger not found'}, status=status.HTTP_404_NOT_FOUND)

        queryset = self.get_queryset_blogger(request, blogger_username).filter(wrote=blogger)
        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        title_post = kwargs.get('title', None)
        me = request.user

        try:
            post = self.get_queryset().get(title=title_post)
        except ObjectDoesNotExist:
            return Response({'detail': 'post not found'}, status=status.HTTP_404_NOT_FOUND)

        if me != post.wrote and post.status == models.StatusRecord.DRAFT:
            return Response({'detail': 'you can\'t view someone else\'s post that is in draft'},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(post)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = serializers.PostSerializer(data=request.data)
        me = request.user

        if serializer.is_valid():
            serializer.validated_data['wrote'] = me
            post_status = serializer.validated_data['status']

            if user_models.BanCommunication.objects.filter(got_banned=me, active=True).exists():
                return Response({'detail': 'you can\'t create post if you are blocked'},
                                status=status.HTTP_403_FORBIDDEN)

            new_post = serializer.save()

            return Response({'message': f'post successfully created {new_post} as '
                                        f'{models.StatusRecord(post_status).label}'},
                            status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        title_post = kwargs.get('title', None)
        me = request.user

        try:
            post = self.get_queryset().get(title=title_post)
        except ObjectDoesNotExist:
            return Response({'detail': 'post not found'}, status=status.HTTP_404_NOT_FOUND)

        if me != post.wrote:
            return Response({'detail': 'you can\'t edit someone else\'s post'}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(post, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({'message': f'post successfully edit {post}'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        title_post = kwargs.get('title', None)
        me = request.user

        try:
            post = self.get_queryset().get(title=title_post)
        except ObjectDoesNotExist:
            return Response({'detail': 'post not found'}, status=status.HTTP_404_NOT_FOUND)

        if me != post.wrote and not me.is_superuser:
            return Response({'detail': 'you can\'t delete someone else\'s post'}, status=status.HTTP_403_FORBIDDEN)

        str_post = f'{post}'
        post.delete()

        return Response({'message': f'post successfully deleted {str_post}'}, status=status.HTTP_204_NO_CONTENT)


class GoodsPostViewSet(viewsets.ModelViewSet):
    queryset = models.PostGoods.objects.all()
    serializer_class = serializers.GoodsPostSerializer

    http_method_names = ('get', 'post', 'delete',)

    def list(self, request, *args, **kwargs):
        title_post = kwargs.get('title', None)
        me = request.user

        try:
            post = models.Post.blogger.get(title=title_post)
        except ObjectDoesNotExist:
            return Response({'detail': 'post not found'}, status=status.HTTP_404_NOT_FOUND)

        if post.status == models.StatusRecord.DRAFT and me != post.wrote:
            return Response({'detail': 'you can\'t see the product list of someone else\'s post in draft'},
                            status=status.HTTP_403_FORBIDDEN)

        goods_post = self.get_queryset().filter(post_with_goods=post)
        serializer = self.get_serializer(goods_post, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        title_post = kwargs.get('title', None)
        name_goods = kwargs.get('goods', None)
        me = request.user

        try:
            post = models.Post.objects.get(title=title_post)
        except ObjectDoesNotExist:
            return Response({'detail': 'post not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            add_goods = models.Goods.objects.get(name=name_goods)
        except ObjectDoesNotExist:
            return Response({'detail': f'goods not found'}, status=status.HTTP_404_NOT_FOUND)

        if me != post.wrote:
            return Response({'detail': 'you can\'t add a goods to someone else\'s post'},
                            status=status.HTTP_403_FORBIDDEN)

        try:
            self.get_queryset().create(goods_post=add_goods, post_with_goods=post)
        except IntegrityError:
            return Response({'detail': 'goods has already been added to the post'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': f'goods {add_goods} successfully added to post'}, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        title_post = kwargs.get('title', None)
        name_goods = kwargs.get('goods', None)
        me = request.user

        try:
            post = models.Post.objects.get(title=title_post)
        except ObjectDoesNotExist:
            return Response({'detail': 'post not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            delete_goods = models.Goods.objects.get(name=name_goods)
        except ObjectDoesNotExist:
            return Response({'detail': 'goods not found'}, status=status.HTTP_404_NOT_FOUND)

        if me != post.wrote:
            return Response({'detail': 'you can\'t delete a goods to someone else\'s post'},
                            status=status.HTTP_403_FORBIDDEN)

        try:
            models.PostGoods.objects.get(goods_post=delete_goods, post_with_goods=post).delete()
        except ObjectDoesNotExist:
            return Response({'detail': 'goods in post not found'}, status=status.HTTP_404_NOT_FOUND)

        return Response({'message': f'goods {delete_goods} successfully removed to post'},
                        status=status.HTTP_204_NO_CONTENT)


class PostCommentViewSet(viewsets.ModelViewSet):
    queryset = models.PostComment.displayed.all()
    serializer_class = serializers.PostCommentSerializer

    http_method_names = ('get', 'post', 'put', 'delete',)

    def list(self, request, *args, **kwargs):
        title_post = kwargs.get('title', None)
        me = request.user

        try:
            post = models.Post.blogger.get(title=title_post)
        except ObjectDoesNotExist:
            return Response({'detail': 'post not found'}, status=status.HTTP_404_NOT_FOUND)

        if me != post.wrote and post.status == models.StatusRecord.DRAFT:
            return Response({'detail': 'you can\'t see comments of someone else\'s post in draft'},
                            status=status.HTTP_403_FORBIDDEN)

        queryset = self.get_queryset().filter(comment_in_post=post)
        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get('pk', None)

        try:
            comment = models.PostComment.displayed.get(pk=pk)
        except ObjectDoesNotExist:
            return Response({'detail': 'comment not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(comment)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        title_post = kwargs.get('title', None)
        me = request.user

        try:
            post = models.Post.published.get(title=title_post)
        except ObjectDoesNotExist:
            return Response({'detail': 'post not found'}, status=status.HTTP_404_NOT_FOUND)

        who_create = post.wrote

        if user_models.BlackList.objects.filter(user_black_list=who_create, in_black_list=me).exists():
            return Response({'detail': f'you are blacklisted {who_create}'}, status=status.HTTP_403_FORBIDDEN)

        if user_models.BanCommunication.objects.filter(got_banned=me, active=True).exists():
            return Response({'detail': 'you can\'t send a comment if you are blocked'},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            serializer.validated_data['comment_in_post'] = post
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        pk = kwargs.get('pk', None)
        me = request.user

        try:
            comment = self.get_queryset().get(pk=pk)
        except ObjectDoesNotExist:
            return Response({'detail': 'comment not found'}, status=status.HTTP_404_NOT_FOUND)

        if comment.wrote != me:
            return Response({'detail': 'only the person who wrote the comment can change it'},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(comment, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        pk = kwargs.get('pk', None)
        me = request.user

        try:
            comment = self.get_queryset().get(pk=pk)
        except ObjectDoesNotExist:
            return Response({'detail': 'comment not found'}, status=status.HTTP_404_NOT_FOUND)

        if comment.wrote != me:
            return Response({'detail': 'only the person who wrote the comment can delete it'},
                            status=status.HTTP_403_FORBIDDEN)

        comment.status = common_models.StatusMessage.DELETED
        comment.save()

        return Response({'message': f'comment {comment} was successfully deleted'}, status=status.HTTP_204_NO_CONTENT)


class MySubscriptionsAPIView(generics.ListAPIView):
    queryset = models.SubscriberBlogUser.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.SubscriptionSerializer

    def list(self, request, *args, **kwargs):
        me = request.user

        queryset = self.get_queryset().filter(subscriber=me)
        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class SubscriberViewSet(viewsets.ModelViewSet):
    queryset = models.SubscriberBlogUser.objects.all()
    serializer_class = serializers.SubscriptionSerializer

    http_method_names = ('get', 'post', 'delete',)

    def list(self, request, *args, **kwargs):
        username_blogger = kwargs.get('username', None)

        try:
            blogger = user_models.User.objects.get(username=username_blogger)
        except ObjectDoesNotExist:
            return Response({'detail': 'blogger not found'}, status=status.HTTP_404_NOT_FOUND)

        queryset = (self.get_queryset().select_related('subscriber__settings_fk')
                    .filter(dj_models.Q(blogger=blogger) &
                            dj_models.Q(subscriber__settings_fk__hide_yourself_subscriptions=False)))
        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        username_blogger = kwargs.get('username', None)
        me = request.user

        try:
            blogger = user_models.User.objects.get(username=username_blogger)
        except ObjectDoesNotExist:
            return Response({'detail': 'blogger not found'}, status=status.HTTP_404_NOT_FOUND)

        if me == blogger:
            return Response({'detail': 'you can\'t subscribe to yourself'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            models.SubscriberBlogUser.objects.create(blogger=blogger, subscriber=me)
        except IntegrityError:
            return Response({'detail': f'you are already subscribed to {blogger}'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': f'you have successfully subscribed to {blogger}'}, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        username_blogger = kwargs.get('username', None)
        me = request.user

        try:
            blogger = user_models.User.objects.get(username=username_blogger)
        except ObjectDoesNotExist:
            return Response({'detail': 'blogger not found'}, status=status.HTTP_404_NOT_FOUND)

        if me == blogger:
            return Response({'detail': 'you can\'t be subscribed to yourself'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            models.SubscriberBlogUser.objects.get(blogger=blogger, subscriber=me).delete()
        except ObjectDoesNotExist:
            return Response({'detail': f'you are not subscribed to {blogger}'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': f'you have successfully unsubscribed from {blogger}'},
                        status=status.HTTP_204_NO_CONTENT)
