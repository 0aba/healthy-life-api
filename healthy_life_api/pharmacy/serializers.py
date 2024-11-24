from rest_framework import serializers
from common import validators
from pharmacy import models


class GoodsListSerializer(serializers.ModelSerializer):
    photo = serializers.ImageField(validators=[lambda image: validators.validate_image(image,
                                                                                       3, 64,
                                                                                       1920, 1080)])
    type_goods = serializers.ChoiceField(
        choices=(
            models.TypeGoods.OTHER, 'Другое',
            models.TypeGoods.MEDICINE, 'Лекарство',
            models.TypeGoods.MEDICAL_PRODUCTS, 'Медицинские изделия',
            models.TypeGoods.COSMETICS, 'Косметика',
            models.TypeGoods.HYGIENE, 'Гигиена',
            models.TypeGoods.SUPPLEMENTS_VITAMINS, 'Добавки/Витамины',
        )
    )
    in_stock = serializers.SerializerMethodField()

    class Meta:
        model = models.Goods
        fields = ('name', 'photo', 'type_goods', 'price', 'in_stock',)
        read_only_fields = ('name', 'photo', 'type_goods', 'price', 'in_stock',)

    def get_in_stock(self, obj):
        return True if obj.amount_in_stock != 0 else False


class GoodsSerializer(serializers.ModelSerializer):
    photo = serializers.ImageField(validators=[lambda image: validators.validate_image(image,
                                                                                       3, 64,
                                                                                       1920, 1080)])
    type_goods = serializers.ChoiceField(
        choices=(
            models.TypeGoods.OTHER, 'Другое',
            models.TypeGoods.MEDICINE, 'Лекарство',
            models.TypeGoods.MEDICAL_PRODUCTS, 'Медицинские изделия',
            models.TypeGoods.COSMETICS, 'Косметика',
            models.TypeGoods.HYGIENE, 'Гигиена',
            models.TypeGoods.SUPPLEMENTS_VITAMINS, 'Добавки/Витамины',
        )
    )

    class Meta:
        model = models.Goods
        fields = ('name', 'photo', 'type_goods', 'goods_info', 'price', 'amount_in_stock',)

    def validate_status(self, value):
        if self.instance and self.instance.type_goods != value:
            if value not in (type_goods[0] for type_goods in models.TypeGoods.choices):
                raise serializers.ValidationError(f'You can only select '
                                                  f'the following goods types: {models.TypeGoods.choices}')
        return value


class PromotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Promotion
        fields = ('promotion_goods', 'time_end_promotion', 'promotion_percentage',)


class GoodsReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.GoodsReview
        fields = ('pk', 'goods_review', 'grade', 'wrote', 'message', 'date_create', 'date_change',)
        read_only_fields = ('pk', 'goods_review', 'wrote', 'date_create', 'date_change',)

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['wrote'] = request.user

        return super().create(validated_data)


class LoyaltyCardSerializer(serializers.ModelSerializer):
    card_status = serializers.ChoiceField(
        choices=(
            models.StatusCart.ACTIVE, 'Активирована',
            models.StatusCart.BLOCKED, 'Заблокирована',
        )
    )

    class Meta:
        model = models.GoodsReview
        fields = ('uuid', 'user_card', 'card_status', 'bonuses',)
        read_only_fields = ('uuid', 'user_card', 'card_status',)

    def validate_status(self, value):
        if self.instance and self.instance.type_goods != value:
            if value not in (type_cart[0] for type_cart in models.StatusCart.choices):
                raise serializers.ValidationError(f'You can only select '
                                                  f'the following cart status: {models.StatusCart.choices}')
        return value


class PurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Purchase

        fields = ('user_buy', 'date_buy', 'transaction_execution', 'for_money', 'paid_with_bonuses',
                  'purchase_id', 'is_paid', 'goods_is_received',)
        read_only_fields = ('user_buy', 'date_buy', 'transaction_execution', 'for_money', 'paid_with_bonuses',
                            'purchase_id', 'is_paid', 'goods_is_received',)

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if not instance.is_paid:
            representation.pop('for_money')
            representation.pop('date_buy')

        return representation

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['user_buy'] = request.user

        return super().create(validated_data)


class PurchaseGoodsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PurchaseGoods
        fields = ('purchase', 'goods_purchase', 'amount',)
        read_only_fields = ('purchase', 'goods_purchase',)
