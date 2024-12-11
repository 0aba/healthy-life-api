from rest_framework import serializers
from django.utils import timezone
from django.db.models import Avg
from common import validators
from pharmacy import models
import decimal


class GoodsListSerializer(serializers.ModelSerializer):
    in_stock = serializers.SerializerMethodField()
    price_with_promotion = serializers.SerializerMethodField()
    goods_rating = serializers.SerializerMethodField()

    class Meta:
        model = models.Goods
        fields = ('pk', 'name', 'photo', 'type_goods', 'price', 'in_stock', 'price_with_promotion', 'goods_rating',)
        read_only_fields = ('pk', 'name', 'photo', 'type_goods', 'price',
                            'in_stock', 'price_with_promotion', 'goods_rating',)

    def get_in_stock(self, obj):
        return True if obj.amount_in_stock != 0 else False

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if representation['price_with_promotion'] is None:
            representation.pop('price_with_promotion')

        return representation

    def get_price_with_promotion(self, obj):
        promotion = models.Promotion.objects.filter(promotion_goods=obj,
                                                    time_end_promotion__gt=timezone.now()
                                                    ).order_by('-time_end_promotion').first()

        return str(((obj.price * decimal.Decimal(100 - promotion.promotion_percentage) / 100)
                    .quantize(decimal.Decimal('0.01'), rounding=decimal.ROUND_HALF_UP))) if promotion else None

    def get_goods_rating(self, obj):
        rating = models.GoodsReview.objects.filter(goods_review=obj).aggregate(result_avg=Avg('grade'))['result_avg']

        return round(rating, 2) if rating else .00


class GoodsSerializer(serializers.ModelSerializer):
    photo = serializers.ImageField(validators=[lambda image: validators.validate_image(image,
                                                                                       3, 64,
                                                                                       1920, 1080)],
                                   required=False)
    type_goods = serializers.ChoiceField(
        choices=(
            models.TypeGoods.OTHER,
            models.TypeGoods.MEDICINE,
            models.TypeGoods.MEDICAL_PRODUCTS,
            models.TypeGoods.COSMETICS,
            models.TypeGoods.HYGIENE,
            models.TypeGoods.SUPPLEMENTS_VITAMINS,
        ),
        default=models.TypeGoods.OTHER
    )
    price_with_promotion = serializers.SerializerMethodField()
    goods_rating = serializers.SerializerMethodField()

    class Meta:
        model = models.Goods
        fields = ('pk', 'name', 'photo', 'type_goods', 'goods_info', 'price',
                  'amount_in_stock', 'price_with_promotion', 'goods_rating',)
        read_only_fields = ('pk', 'price_with_promotion', 'goods_rating',)

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if representation['price_with_promotion'] is None:
            representation.pop('price_with_promotion')

        return representation

    def get_price_with_promotion(self, obj):
        promotion = models.Promotion.objects.filter(promotion_goods=obj,
                                                    time_end_promotion__gt=timezone.now()
                                                    ).order_by('-time_end_promotion').first()

        return str(((obj.price * decimal.Decimal(100 - promotion.promotion_percentage) / 100)
                    .quantize(decimal.Decimal('0.01'), rounding=decimal.ROUND_HALF_UP))) if promotion else None

    def get_goods_rating(self, obj):
        rating = models.GoodsReview.objects.filter(goods_review=obj).aggregate(result_avg=Avg('grade'))['result_avg']

        return round(rating, 2) if rating else .00


class PromotionSerializer(serializers.ModelSerializer):
    promotion_percentage = serializers.IntegerField(validators=[
        lambda value: validators.number_between(value, 10, 90)
    ])

    class Meta:
        model = models.Promotion
        fields = ('pk', 'promotion_goods', 'time_end_promotion', 'promotion_percentage',)
        read_only_fields = ('pk',)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['promotion_goods'] = instance.promotion_goods.name

        return representation

    def update(self, instance, validated_data):
        validated_data.pop('promotion_goods', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class GoodsReviewSerializer(serializers.ModelSerializer):
    grade = serializers.DecimalField(validators=[
        lambda value: validators.number_between(value, 0.00, 5.00)
    ], max_digits=3, decimal_places=2)

    class Meta:
        model = models.GoodsReview
        fields = ('pk', 'goods_review', 'grade', 'wrote', 'message', 'date_create', 'date_change',)
        read_only_fields = ('pk', 'goods_review', 'wrote', 'date_create', 'date_change',)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['goods_review'] = instance.goods_review.name

        return representation

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['wrote'] = request.user

        return super().create(validated_data)


class LoyaltyCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.LoyaltyCard
        fields = ('uuid', 'user_card', 'card_status', 'bonuses',)
        read_only_fields = ('uuid', 'user_card', 'card_status',)


class PurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Purchase

        fields = ('pk', 'user_buy', 'date_buy', 'total_price', 'paid_with_bonuses', 'is_paid', 'goods_is_received',)
        read_only_fields = ('pk', 'user_buy', 'date_buy', 'total_price', 'paid_with_bonuses',
                            'is_paid', 'goods_is_received',)

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if not instance.is_paid:
            representation.pop('date_buy')
            representation.pop('total_price')
            representation.pop('paid_with_bonuses')

        return representation

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['user_buy'] = request.user

        return super().create(validated_data)


class PurchaseGoodsSerializer(serializers.ModelSerializer):
    amount = serializers.IntegerField(validators=[lambda value: validators.number_gte(value, 1)])

    class Meta:
        model = models.PurchaseGoods
        fields = ('purchase', 'goods_purchase', 'amount',)
        read_only_fields = ('purchase', 'goods_purchase',)
