from django.urls import path
from pharmacy import views


urlpatterns = [
    path('goods/', views.GoodsListAPIView.as_view(), name='goods_list'),
    path('goods/new/', views.GoodsViewSet.as_view({'post': 'create'}), name='goods_new'),
    path('goods/<slug:name>/', views.GoodsViewSet.as_view({'get': 'retrieve',
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

    path('loyaltycard/<slug:username>/', views.LoyaltyCardViewSet.as_view({'get': 'list',
                                                                           'put': 'update'}
                                                                          ), name='loyaltycard'),
    path('ban/loyaltycard/<slug:username>/', views.GoodsReviewViewSet.as_view({'patch': 'patch_ban_card'}
                                                                              ), name='loyaltycard_ban'),
    path('unban/loyaltycard/<slug:username>/', views.GoodsReviewViewSet.as_view({'patch': 'patch_unban_card'}
                                                                                ), name='loyaltycard_unban'),

    path('purchase/<slug:username>/', views.PurchaseViewSet.as_view({'get': 'list'}), name='purchase'),
    path('purchase/<slug:pk>/cancellation/', views.PurchaseViewSet.as_view({'delete': 'destroy'}
                                                                           ), name='purchase_cancellation'),
    path('purchase/<slug:pk>/', views.PurchaseViewSet.as_view({'patch': 'get'}), name='purchase_one'),
    path('purchase/<slug:pk>/received/', views.PurchaseViewSet.as_view({'post': 'post_received'}
                                                                       ), name='purchase_received'),
    path('purchase/<slug:pk>/buy/', views.PurchaseViewSet.as_view({'post': 'post_buy'}
                                                                  ), name='purchase_buy'),

    path('purchase/<slug:pk>/goods/', views.PurchaseGoodsViewSet.as_view({'get': 'list',
                                                                          'post': 'create'}), name='purchase_goods'),
    path('purchase/<slug:pk>/goods/<slug:goods>/', views.PurchaseGoodsViewSet.as_view({'put': 'update',
                                                                                       'delete': 'destroy'}
                                                                                      ), name='purchase_goods_action'),
]
