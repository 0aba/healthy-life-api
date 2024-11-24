from django.urls import path
from user import views


urlpatterns = [
    path('profile/<slug:username>/', views.ProfileAPIView.as_view(), name='profile'),
    path('settings/<slug:username>/', views.SettingsAPIView.as_view(), name='settings'),
    path('group/<slug:username>/', views.GroupAPIView.as_view(), name='group'),
    path('friend/<slug:username>/', views.FriendAPIView.as_view(), name='friend'),
    path('blacklist/<slug:username>/', views.BlackListAPIView.as_view(), name='blacklist'),

    path('awards/', views.AwardViewSet.as_view({'get': 'list',
                                                'post': 'create'}), name='awards'),
    path('award/<int:pk>/', views.AwardViewSet.as_view({'get': 'retrieve',
                                                        'delete': 'destroy',
                                                        'put': 'update'}), name='award'),


    path('award/view/<slug:username>/', views.AwardUserViewSet.as_view({'get': 'list',
                                                                        'post': 'create'}), name='awards_user'),
    path('award/view/<slug:username>/<int:pk>/', views.AwardUserViewSet.as_view({'get': 'retrieve', 'delete': 'destroy'}
                                                                                ), name='award_user'),

    path('bans/', views.BanCommunicationViewSet.as_view({'get': 'list'}), name='bans'),
    path('ban/<int:pk>/', views.BanCommunicationViewSet.as_view({'get': 'retrieve'}), name='ban'),
    path('ban/<slug:username>/', views.BanCommunicationViewSet.as_view({'post': 'create',
                                                                        'delete': 'destroy'}), name='ban_action'),

    path('notification/view/<slug:username>/', views.NotificationViewSet.as_view({'get': 'list'}),
         name='notifications_user'),
    path('notification/<int:pk>/', views.NotificationViewSet.as_view({'get': 'retrieve',
                                                                      'patch': 'partial_update',
                                                                      'delete': 'destroy'}),
         name='notification'),
    path('chats/', views.ChatListAPIView.as_view(), name='chats'),
    path('chat/<slug:username>/', views.PrivateMessageViewSet.as_view({'get': 'list',
                                                                       'post': 'create'}), name='chat_messages'),
    path('message/<int:pk>/', views.PrivateMessageViewSet.as_view({'get': 'retrieve',
                                                                   'put': 'update',
                                                                   'patch': 'partial_update',
                                                                   'delete': 'destroy'}), name='message_action'),

    path('balance/', views.CryptoCloudViewAPI({'get': 'get_balance'}), name='balance'),
    path('balance/topup/', views.CryptoCloudViewAPI({'post': 'top_up_balance'}), name='balance_topup'),
    path('balance/topup/successful/', views.CryptoCloudViewAPI({'post': 'successful_payment'}
                                                               ), name='balance_topup_successful'),
]
