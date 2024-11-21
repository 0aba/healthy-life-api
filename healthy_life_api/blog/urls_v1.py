from django.urls import path
from blog import views


urlpatterns = [
    path('posts/', views.PostListAPIView.as_view(), name='post_list'),

    path('blogger/<slug:username>/', views.BloggerViewSet.as_view({'get': 'list'}), name='blogger_post_list'),
    path('post/<slug:title>/', views.BloggerViewSet.as_view({'get': 'retrieve',
                                                             'put': 'update',
                                                             'delete': 'destroy'}), name='post_action'),
    path('blogger/', views.BloggerViewSet.as_view({'post': 'create'}), name='new_post'),

    path('post/<slug:title>/goods/', views.GoodsPostViewSet.as_view({'get': 'list',
                                                                     'post': 'create'}), name='post_action'),
    path('post/<slug:title>/goods/goods/<slug:goods>/', views.GoodsPostViewSet.as_view({'delete': 'destroy'}
                                                                                       ), name='post_del'),

    path('post/<slug:title>/comments/', views.PostCommentViewSet.as_view({'get': 'list',
                                                                          'post': 'create'}), name='comment_post'),
    path('post/comments/<int:pk>/', views.PostCommentViewSet.as_view({'get': 'retrieve',
                                                                      'put': 'update',
                                                                      'delete': 'destroy'}
                                                                     ), name='comment_post_action'),

    path('subscriptions/my/', views.MySubscriptionsAPIView.as_view(), name='subscriptions'),

    path('subscriptions/<slug:username>/', views.SubscriberViewSet.as_view({'get': 'list',
                                                                            'post': 'create',
                                                                            'delete': 'destroy'}
                                                                           ), name='subscriptions_blogger'),
]
