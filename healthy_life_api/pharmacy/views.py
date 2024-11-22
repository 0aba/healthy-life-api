import decimal

from rest_framework.permissions import AllowAny, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics, viewsets, status
from django.db import IntegrityError, DatabaseError
from pharmacy import serializers, models, filters
from rest_framework.response import Response
from django.db import models as dj_model
from user import models as user_models
from common import permissions
import datetime


class GoodsListAPIView(generics.ListAPIView):
    queryset = models.Goods.objects.all()
    serializer_class = serializers.GoodsListSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = filters.GoodsListFilter

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class GoodsViewSet(viewsets.ModelViewSet):
    queryset = models.Goods.objects.all()
    serializer_class = serializers.GoodsSerializer
    permission_classes = (permissions.IsPharmacistOrSuperUser,)
    lookup_field = 'name'

    http_method_names = ('get', 'post', 'put', 'delete',)

    def get_permissions(self):
        if self.request.method == 'GET':
            return (AllowAny(),)

        return (permission() for permission in self.permission_classes)

    def retrieve(self, request, *args, **kwargs):
        name_goods = kwargs.get('name', None)

        try:
            goods = self.get_queryset().get(name=name_goods)
        except ObjectDoesNotExist:
            return Response({'error': 'goods not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(goods)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        name = serializer.validated_data.get('name')
        price = serializer.validated_data.get('price')
        amount_in_stock = serializer.validated_data.get('amount_in_stock')

        if self.get_queryset().filter(name=name).exists():
            return Response({'error': 'goods with this name already exists'}, status=status.HTTP_400_BAD_REQUEST)

        if price < 0:
            return Response({'error': 'price is negative'}, status=status.HTTP_400_BAD_REQUEST)

        if amount_in_stock < 0:
            return Response({'error': 'amount in stock is negative'}, status=status.HTTP_400_BAD_REQUEST)

        new_goods = serializer.save()

        return Response({'message': f'goods successfully created {new_goods}'}, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        name_goods = kwargs.get('name', None)

        try:
            goods = self.get_queryset().get(name=name_goods)
        except ObjectDoesNotExist:
            return Response({'error': 'goods not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(goods, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        name = serializer.validated_data.get('name')
        price = serializer.validated_data.get('price')
        amount_in_stock = serializer.validated_data.get('amount_in_stock')

        if self.get_queryset().filter(name=name).exists():
            return Response({'error': 'goods with this name already exists'}, status=status.HTTP_400_BAD_REQUEST)

        if price < 0:
            return Response({'error': 'price is negative'}, status=status.HTTP_400_BAD_REQUEST)

        if amount_in_stock < 0:
            return Response({'error': 'amount in stock is negative'}, status=status.HTTP_400_BAD_REQUEST)

        updated_goods = serializer.save()

        return Response({'message': f'goods successfully edit {updated_goods}'}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        name_goods = kwargs.get('name', None)

        try:
            goods = self.get_queryset().get(name=name_goods)
        except ObjectDoesNotExist:
            return Response({'error': 'goods not found'}, status=status.HTTP_404_NOT_FOUND)

        str_goods = f'{goods}'
        goods.delete()

        return Response({'message': f'goods successfully deleted {str_goods}'}, status=status.HTTP_204_NO_CONTENT)


class PromotionViewSet(viewsets.ModelViewSet):
    queryset = models.Promotion.objects.all()
    serializer_class = serializers.PurchaseSerializer
    permission_classes = (permissions.IsPharmacistOrSuperUser,)
    lookup_field = 'pk'

    http_method_names = ('get', 'post', 'put', 'delete',)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        pk_promotion = kwargs.get('pk', None)

        try:
            promotion = self.get_queryset().get(pk=pk_promotion)
        except ObjectDoesNotExist:
            return Response({'error': 'promotion not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(promotion)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        promotion_goods = serializer.validated_data.get('promotion_goods')
        promotion_percentage = serializer.validated_data.get('promotion_percentage')

        if self.get_queryset().filter(promotion_goods=promotion_goods,
                                      time_end_promotion__gt=datetime.datetime.now()).exists():
            return Response({'error': 'promotion goods already exists'}, status=status.HTTP_400_BAD_REQUEST)

        if not (10 <= promotion_percentage <= 90):
            return Response({'error': 'promotion should be between 10 and 90 percent'},
                            status=status.HTTP_400_BAD_REQUEST)

        new_goods = serializer.save()

        return Response({'message': f'promotion successfully created {new_goods}'}, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        pk_promotion = kwargs.get('pk', None)

        try:
            promotion = self.get_queryset().get(pk=pk_promotion)
        except ObjectDoesNotExist:
            return Response({'error': 'promotion not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(promotion, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        promotion_percentage = serializer.validated_data.get('promotion_percentage')

        if not (10 <= promotion_percentage <= 90):
            return Response({'error': 'promotion should be between 10 and 90 percent'},
                            status=status.HTTP_400_BAD_REQUEST)

        updated_goods = serializer.save()

        return Response({'message': f'promotion successfully edit {updated_goods}'}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        pk_promotion = kwargs.get('pk', None)

        try:
            promotion = self.get_queryset().get(pk=pk_promotion)
        except ObjectDoesNotExist:
            return Response({'error': 'promotion not found'}, status=status.HTTP_404_NOT_FOUND)

        str_promotion = f'{promotion}'
        promotion.delete()

        return Response({'message': f'promotion successfully deleted {str_promotion}'}, status=status.HTTP_204_NO_CONTENT)


class GoodsReviewViewSet(viewsets.ModelViewSet):
    queryset = models.GoodsReview.objects.all()
    serializer_class = serializers.GoodsReviewSerializer

    http_method_names = ('get', 'post', 'put', 'delete',)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        pk_review = kwargs.get('pk', None)

        try:
            review = self.get_queryset().get(pk=pk_review)
        except ObjectDoesNotExist:
            return Response({'error': 'review not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(review)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        name_goods = kwargs.get('name', None)

        try:
            goods = models.Goods.objects.get(name=name_goods)
        except ObjectDoesNotExist:
            return Response({'error': 'goods not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            new_review = serializer.save(goods_review=goods, wrote=request.user)
        except IntegrityError:
            return Response({'error': 'review already exists'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': f'review successfully created {new_review}'}, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        pk_review = kwargs.get('pk', None)

        try:
            review = self.get_queryset().get(pk=pk_review)
        except ObjectDoesNotExist:
            return Response({'error': 'review not found'}, status=status.HTTP_404_NOT_FOUND)

        if review.wrote != request.user:
            return Response({'error': 'you can\'t change someone else\'s review'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(review, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        updated_review = serializer.save()

        return Response({'message': f'review successfully edit {updated_review}'}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        pk_review = kwargs.get('pk', None)

        try:
            review = self.get_queryset().get(pk=pk_review)
        except ObjectDoesNotExist:
            return Response({'error': 'review not found'}, status=status.HTTP_404_NOT_FOUND)

        if review.wrote != request.user:
            return Response({'error': 'you can\'t delete someone else\'s review'}, status=status.HTTP_400_BAD_REQUEST)

        str_review = f'{review}'
        review.delete()

        return Response({'message': f'review successfully deleted {str_review}'}, status=status.HTTP_204_NO_CONTENT)


class LoyaltyCardViewSet(viewsets.ModelViewSet):
    queryset = models.LoyaltyCard.objects.all()
    serializer_class = serializers.LoyaltyCardSerializer
    permission_classes = (permissions.IsAdminUserOrReadOnly,)
    lookup_field = 'username'

    http_method_names = ('get', 'put', 'patch',)

    def retrieve(self, request, *args, **kwargs):
        username_owner_card = kwargs.get('username', None)
        me = request.me

        try:
            owner_card = user_models.User.objects.get(username=username_owner_card)
            card_user = self.get_queryset().get(user_card=owner_card)
        except ObjectDoesNotExist:
            return Response({'error': 'user not found'}, status=status.HTTP_404_NOT_FOUND)

        if me != card_user.user_card and not me.is_superuser:
            return Response({'error': 'you can\'t see someone else\'s loyalty card'}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(card_user)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        username_owner_card = kwargs.get('username', None)

        try:
            owner_card = user_models.User.objects.get(username=username_owner_card)
            card_user = self.get_queryset().get(user_card=owner_card)
        except ObjectDoesNotExist:
            return Response({'error': 'user not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(card_user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        updated_card = serializer.save()

        return Response({'message': f'successfully changed the amount of bonuses in {updated_card}'},
                        status=status.HTTP_200_OK)

    def patch_ban_card(self, request, *args, **kwargs):
        username_owner_card = kwargs.get('username', None)

        try:
            owner_card = user_models.User.objects.get(username=username_owner_card)
            card_user = self.get_queryset().get(user_card=owner_card)
        except ObjectDoesNotExist:
            return Response({'error': 'user not found'}, status=status.HTTP_404_NOT_FOUND)

        card_user.card_status = models.StatusCart.BLOCKED
        card_user.save()

        return Response({'message': f'successfully unblocked card {card_user}'}, status=status.HTTP_200_OK)

    def patch_unban_card(self, request, *args, **kwargs):
        username_owner_card = kwargs.get('username', None)

        try:
            owner_card = user_models.User.objects.get(username=username_owner_card)
            card_user = self.get_queryset().get(user_card=owner_card)
        except ObjectDoesNotExist:
            return Response({'error': 'user not found'}, status=status.HTTP_404_NOT_FOUND)

        card_user.card_status = models.StatusCart.ACTIVE
        card_user.save()

        return Response({'message': f'successfully blocked card {card_user}'}, status=status.HTTP_200_OK)


class PurchaseViewSet(viewsets.ModelViewSet):
    queryset = models.Purchase.objects.all()
    serializer_class = serializers.PurchaseSerializer
    permission_classes = (IsAuthenticated,)

    http_method_names = ('get', 'post', 'put', 'patch', 'delete',)

    def list(self, request, *args, **kwargs):
        purchase_user_username = kwargs.get('username', None)

        try:
            purchase_user = user_models.User.objects.get(username=purchase_user_username)
        except ObjectDoesNotExist:
            return Response({'error': 'user not found'}, status=status.HTTP_404_NOT_FOUND)

        queryset = self.get_queryset().filter(user_buy=purchase_user)
        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        purchase_pk = kwargs.get('pk', None)

        try:
            purchase = self.get_queryset().get(pk=purchase_pk)
        except ObjectDoesNotExist:
            return Response({'error': 'purchase not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(purchase)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_purchase = serializer.save()

        return Response({'message': f'purchase successfully created {new_purchase}'}, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        purchase_pk = kwargs.get('pk', None)
        me = request.user

        try:
            purchase = self.get_queryset().get(pk=purchase_pk)
        except ObjectDoesNotExist:
            return Response({'error': 'purchase not found'}, status=status.HTTP_404_NOT_FOUND)

        if me != purchase.user_buy:
            return Response({'error': 'you can\'t delete someone else\'s purchase'},
                            status=status.HTTP_403_FORBIDDEN)

        if purchase.is_paid:
            return Response({'error': 'You cannot delete completed purchases'},
                            status=status.HTTP_400_BAD_REQUEST)

        str_purchase = f'{purchase}'
        purchase.delete()

        return Response({'message': f'purchase successfully deleted {str_purchase}'}, status=status.HTTP_204_NO_CONTENT)

    def post_buy(self, request, *args, **kwargs):
        purchase_pk = kwargs.get('pk', None)
        me = request.user

        try:
            purchase = self.get_queryset().get(pk=purchase_pk)
        except ObjectDoesNotExist:
            return Response({'error': 'purchase not found'}, status=status.HTTP_404_NOT_FOUND)

        if me != purchase.user_buy:
            return Response({'error': 'you can\'t pay for someone else\'s purchase'},
                            status=status.HTTP_403_FORBIDDEN)

        if purchase.is_paid:
            return Response({'error': 'the purchase has already been paid for'},
                            status=status.HTTP_400_BAD_REQUEST)

        current_total_price = decimal.Decimal(models.PurchaseGoods.objects.filter(purchase=purchase)
                                              .annotate(current_total_price=(dj_model.F('amount') *
                                                                             dj_model.F('goods_purchase__price')))
                                              .aggregate(total=dj_model.Sum('current_total_price')))

        paid_with_bonuses = request.data.get('paid_with_bonuses', 0)

        if models.LoyaltyCard.objects.get(user_card=me).bonuses < paid_with_bonuses:
            return Response({'ошибка': 'у вас нет столько бонусов'})

        if paid_with_bonuses < 0:
            return Response({'error': 'bonuses is negative number'}, status=status.HTTP_400_BAD_REQUEST)

        # info только 25% покупки можно оплатить бонусами
        if current_total_price * decimal.Decimal('0.75') < paid_with_bonuses * models.LoyaltyCard.BONUS_IN_CURRENCY:
            return Response({'ошибка': 'только 25% покупки можно оплатить бонусами'},
                            status=status.HTTP_400_BAD_REQUEST)

        balance = me.balance

        if balance < current_total_price - paid_with_bonuses * models.LoyaltyCard.BONUS_IN_CURRENCY:
            return Response({'ошибка': 'недостаточно средств'}, status=status.HTTP_400_BAD_REQUEST)

        not_available = models.PurchaseGoods.objects.filter(purchase=purchase,
                                                            goods_purchase__amount_in_stock__lt=dj_model.F('amount')
                                                            ).values_list('pk', flat=True)

        if len(not_available) != 0:
            return Response({'ошибка': f'нет в наличии в таком объеме следующих товаров в покупке: {not_available}'})

        purchase_goods = models.PurchaseGoods.objects.filter(purchase=purchase)

        try:
            purchase_goods.update(
                goods_purchase__amount_in_stock=(dj_model.F('goods_purchase__amount_in_stock') -
                                                 dj_model.F('amount'))
            )
        except DatabaseError:
            return Response({'ошибка': 'ошибка при резервации товара для покупки'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        me.balance -= current_total_price - paid_with_bonuses * models.LoyaltyCard.BONUS_IN_CURRENCY
        models.LoyaltyCard.objects.filter(user_card=me).update(bonuses=dj_model.F('bonuses') - paid_with_bonuses)

        purchase.is_paid = True
        purchase.save()

        return Response({'message': f'purchase {purchase} is successfully paid'}, status=status.HTTP_201_CREATED)

    def post_received(self, request, *args, **kwargs):
        purchase_pk = kwargs.get('pk', None)
        me = request.user

        try:
            purchase = self.get_queryset().get(pk=purchase_pk)
        except ObjectDoesNotExist:
            return Response({'error': 'purchase not found'}, status=status.HTTP_404_NOT_FOUND)

        if not me.groups.filter(name='Фармацевт').exists() and not me.is_superuser:
            return Response({'error': 'only pharmacy staff can mark the purchase as delivered'},)

        if not purchase.is_paid:
            return Response({'error': 'cannot mark an unpaid purchase as delivered'}, status=status.HTTP_403_FORBIDDEN)

        if purchase.transaction_execution:
            return Response({'error': 'payment pending'}, status=status.HTTP_400_BAD_REQUEST)

        if purchase.goods_is_received:
            return Response({'error': 'the goods have already been delivered'}, status=status.HTTP_400_BAD_REQUEST)

        purchase.goods_is_received = True
        purchase.save()

        return Response({'message': f'purchase successfully delivered {purchase}'},)


class PurchaseGoodsViewSet(viewsets.ModelViewSet):
    queryset = models.PurchaseGoods.objects.all()
    serializer_class = serializers.PurchaseGoodsSerializer
    permission_classes = (IsAuthenticated,)

    http_method_names = ('get', 'post', 'delete',)

    def list(self, request, *args, **kwargs):
        purchase_pk = kwargs.get('pk', None)

        try:
            purchase = models.Purchase.objects.get(pk=purchase_pk)
        except ObjectDoesNotExist:
            return Response({'error': 'purchase not found'}, status=status.HTTP_404_NOT_FOUND)

        queryset = self.get_queryset().filter(purchase=purchase)
        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        purchase_pk = kwargs.get('pk', None)
        me = request.user

        try:
            purchase = models.Purchase.objects.get(pk=purchase_pk)
        except ObjectDoesNotExist:
            return Response({'error': 'purchase not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        amount_in_stock = serializer.validated_data.get('amount_in_stock')

        if purchase.is_paid:
            return Response({'error': 'a paid purchase cannot be supplemented'}, status=status.HTTP_400_BAD_REQUEST)

        if purchase.user_buy != me:
            return Response({'error': 'You cannot change the quantity of an item in someone else\'s purchase.'},
                            status=status.HTTP_403_FORBIDDEN)

        if amount_in_stock == 0:
            return Response({'error': 'select at least one goods'}, status=status.HTTP_400_BAD_REQUEST)

        if models.Goods.objects.get(pk=purchase.goods_purchase).amount_in_stock < amount_in_stock:
            return Response({'error': 'there is not enough product in stock'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            new_purchase_goods = serializer.save(purchase=purchase)
        except IntegrityError:
            return Response({'error': 'purchase already has goods'},  status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': f'goods {new_purchase_goods.goods_purchase} '
                                    f'successfully add in purchase {purchase}'},
                        status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        purchase_pk = kwargs.get('pk', None)
        goods_name = kwargs.get('goods', None)
        me = request.user

        try:
            purchase = models.Purchase.objects.get(pk=purchase_pk)
        except ObjectDoesNotExist:
            return Response({'error': 'purchase not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            goods = models.Goods.objects.get(name=goods_name)
        except ObjectDoesNotExist:
            return Response({'error': 'goods not found'}, status=status.HTTP_404_NOT_FOUND)

        new_amount = request.data.get('new_amount')

        if purchase.is_paid:
            return Response({'error': 'a paid purchase cannot be supplemented'}, status=status.HTTP_400_BAD_REQUEST)

        if purchase.user_buy != me:
            return Response({'error': 'You cannot change the quantity of an item in someone else\'s purchase.'},
                            status=status.HTTP_403_FORBIDDEN)

        if new_amount == 0:
            return Response({'error': 'select at least one goods'}, status=status.HTTP_400_BAD_REQUEST)

        if purchase.amount_in_stock < new_amount:
            return Response({'error': 'there is not enough product in stock'}, status=status.HTTP_400_BAD_REQUEST)

        self.get_queryset().filter(purchase=purchase, goods_purchase=goods).update(amount_in_stock=new_amount)

        return Response({'message': f'successfully changed the amount of goods {new_amount}'},
                        status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        purchase_pk = kwargs.get('pk', None)
        goods_name = kwargs.get('goods', None)
        me = request.user

        try:
            purchase = models.Purchase.objects.get(pk=purchase_pk)
        except ObjectDoesNotExist:
            return Response({'error': 'purchase not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            goods = models.Goods.objects.get(name=goods_name)
        except ObjectDoesNotExist:
            return Response({'error': 'goods not found'}, status=status.HTTP_404_NOT_FOUND)

        if purchase.is_paid:
            return Response({'error': 'a paid purchase cannot be supplemented'}, status=status.HTTP_400_BAD_REQUEST)

        if purchase.user_buy != me:
            return Response({'error': 'You cannot change the quantity of an item in someone else\'s purchase.'},
                            status=status.HTTP_403_FORBIDDEN)

        try:
            self.get_queryset().get(purchase=purchase, goods_purchase=goods).delete()
        except ObjectDoesNotExist:
            return Response({'error': 'goods in purchase not found'}, status=status.HTTP_404_NOT_FOUND)

        return Response({'message': f'successfully delete goods in {purchase}'}, status=status.HTTP_200_OK)
