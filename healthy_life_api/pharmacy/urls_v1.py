from django.urls import path
from pharmacy import views




urlpatterns = [
    path('goods/', views.GoodsListAPIView.as_view(), name='goods_list'),
    path('goods/new/', views.GoodsViewSet.as_view({'post': 'create'}), name='goods_new'),
    path('goods/<str:name>/', views.GoodsViewSet.as_view({'get': 'retrieve',
                                                          'put': 'update',
                                                          'delete': 'destroy'}), name='goods_action'),

    path('promotions/', views.PromotionViewSet.as_view({'get': 'list',
                                                        'post': 'create'}), name='promotions'),
    path('promotions/<int:pk>/', views.PromotionViewSet.as_view({'get': 'retrieve',
                                                                 'put': 'update',
                                                                 'delete': 'destroy'}
                                                                ), name='promotions_action'),

    path('goods/<slug:name>/review/', views.GoodsReviewViewSet.as_view({'get': 'list',
                                                                        'post': 'create'}), name='goods_review'),
    path('goods/review/<int:pk>/', views.GoodsReviewViewSet.as_view({'get': 'retrieve',
                                                                     'put': 'update',
                                                                     'delete': 'destroy'}
                                                                    ), name='goods_review_action'),

    path('loyaltycard/<slug:username>/', views.LoyaltyCardViewSet.as_view({'get': 'retrieve',
                                                                           'put': 'update'}
                                                                          ), name='loyaltycard'),
    path('ban/loyaltycard/<slug:username>/', views.LoyaltyCardViewSet.as_view({'patch': 'patch_ban_card'}
                                                                              ), name='loyaltycard_ban'),
    path('unban/loyaltycard/<slug:username>/', views.LoyaltyCardViewSet.as_view({'patch': 'patch_unban_card'}
                                                                                ), name='loyaltycard_unban'),

    path('purchase/<slug:username>/', views.PurchaseViewSet.as_view({'get': 'list'}), name='purchase'),
    path('purchase/', views.PurchaseViewSet.as_view({'post': 'create'}), name='purchase_new'),
    path('purchase/view/<int:pk>/', views.PurchaseViewSet.as_view({'get': 'retrieve',
                                                                   'delete': 'destroy'}), name='purchase_one'),
    path('purchase/<int:pk>/received/', views.PurchaseViewSet.as_view({'post': 'post_received'}
                                                                      ), name='purchase_received'),
    path('purchase/<int:pk>/buy/', views.PurchaseViewSet.as_view({'post': 'post_buy'}), name='purchase_buy'),

    path('purchase/<int:pk>/goods/', views.PurchaseGoodsViewSet.as_view({'get': 'list'}), name='purchase_goods'),
    path('purchase/<int:pk>/goods/<str:goods>/', views.PurchaseGoodsViewSet.as_view({'post': 'create',
                                                                                     'put': 'update',
                                                                                     'delete': 'destroy'}
                                                                                    ), name='purchase_goods_action'),
]
