from healthy_life_api.settings import AUTH_USER_MODEL
from common.models import IMessage
from django.db import models
import decimal
import uuid


class TypeGoods(models.IntegerChoices):
    OTHER = 0, 'other'
    MEDICINE = 1, 'medicine'
    MEDICAL_PRODUCTS = 2, 'medical products'
    COSMETICS = 3, 'cosmetics'
    HYGIENE = 4, 'hygiene'
    SUPPLEMENTS_VITAMINS = 5, 'supplements/vitamins'


class StatusCart(models.IntegerChoices):
    ACTIVE = 0, 'activated'
    BLOCKED = 1, 'blocked'


class Goods(models.Model):
    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(price__gte=0),
                name='price_goods_CK',
            ),
        ]
        verbose_name = 'goods'
        verbose_name_plural = 'goods'

    name = models.CharField(unique=True, db_index=True, max_length=1024, verbose_name='name goods')
    photo = models.ImageField(upload_to='goods/%Y/%m/%d/', default='default/goods.png',
                              verbose_name='photo of goods')
    type_goods = models.PositiveSmallIntegerField(choices=TypeGoods.choices, default=TypeGoods.OTHER,
                                                  verbose_name='type goods')
    goods_info = models.CharField(max_length=2048, verbose_name='info of goods')
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='price')
    amount_in_stock = models.PositiveSmallIntegerField(default=0, verbose_name='amount in stock')

    objects = models.Manager()

    def __str__(self):
        return f'@\'{self.name}\''


# info! может существать только одна действительная скидка на товар
class Promotion(models.Model):
    class Meta:
        constraints = [
            models.CheckConstraint(
                check=(models.Q(promotion_percentage__gte=10) &
                       models.Q(promotion_percentage__lte=90)),
                name='promotion_percentage_CK',
            ),
        ]
        verbose_name = 'promotion'
        verbose_name_plural = 'promotions'

    promotion_goods = models.ForeignKey(Goods,
                                        on_delete=models.CASCADE,
                                        related_name='promotion_goods_fk',
                                        verbose_name='promotion goods')
    time_end_promotion = models.DateTimeField(verbose_name='time end promotion')
    promotion_percentage = models.SmallIntegerField(verbose_name='percentage of promotion')

    objects = models.Manager()

    def __str__(self):
        return f'@\'{self.pk}\''


# info! отзыв может существать только один на человека, но его можно изменить и удалить
class GoodsReview(IMessage):
    class Meta:
        constraints = [
            models.CheckConstraint(
                check=(models.Q(grade__gte=0.00) &
                       models.Q(grade__lte=5.00)),
                name='grade_CK',
            ),
        ]
        unique_together = (('goods_review', 'wrote'),)
        verbose_name = 'review'
        verbose_name_plural = 'reviews'

    goods_review = models.ForeignKey(Goods,
                                     on_delete=models.CASCADE,
                                     related_name='goods_review_fk',
                                     verbose_name='review of goods')
    grade = models.DecimalField(max_digits=3, decimal_places=2, verbose_name='grade')

    status = None  # info! либо существует, либо нет


class LoyaltyCard(models.Model):
    BONUS_IN_CURRENCY = decimal.Decimal('0.01')

    class Meta:
        verbose_name = 'loyalty card'
        verbose_name_plural = 'loyalty cards'

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_card = models.OneToOneField(AUTH_USER_MODEL,
                                     on_delete=models.CASCADE,
                                     related_name='user_card_fk',
                                     verbose_name='card of user')
    card_status = models.PositiveSmallIntegerField(choices=StatusCart.choices, default=StatusCart.ACTIVE,
                                                   verbose_name='status of card')
    # info! (1 бонус = 0.0000001)
    bonuses = models.PositiveIntegerField(default=0, verbose_name='amount of bonuses')

    objects = models.Manager()

    def __str__(self):
        return f'@\'{self.uuid}\''


# info! препологается, что покупка забирается в аптеке после предоставления purchase_id или на стороне клиента
#  (приложения, либо сайта реализована, где интегрирована или реализована система доставки)
# info! пока покупка не совершилась поля date_buy и total_price это None
class Purchase(models.Model):
    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(total_price__gte=0),
                name='price_purchase_CK',
            ),
        ]
        verbose_name = 'purchase'
        verbose_name_plural = 'purchases'

    user_buy = models.ForeignKey(AUTH_USER_MODEL,
                                 on_delete=models.CASCADE,
                                 related_name='user_buy_fk',
                                 verbose_name='buyer')
    date_buy = models.DateField(null=True, verbose_name='timestamp of buy')
    total_price = models.DecimalField(null=True, max_digits=8, decimal_places=2,
                                      verbose_name='total price')
    # info! не более половины покупки можно оплатить 1бонусами
    paid_with_bonuses = models.PositiveSmallIntegerField(null=True, default=0, verbose_name='paid with bonuses')
    is_paid = models.BooleanField(default=False, verbose_name='paid')
    goods_is_received = models.BooleanField(default=False, verbose_name='goods received')

    objects = models.Manager()

    def __str__(self):
        return f'@\'{self.pk}\''


class PurchaseGoods(models.Model):
    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(amount__gte=1),
                name='purchase_amount_CK',
            ),
        ]
        unique_together = (('purchase', 'goods_purchase'),)
        verbose_name = 'goods in purchase'
        verbose_name_plural = 'goods in purchases'

    purchase = models.ForeignKey(Purchase,
                                 on_delete=models.CASCADE,
                                 related_name='purchase_fk',
                                 verbose_name='purchase')
    goods_purchase = models.ForeignKey(Goods,
                                       on_delete=models.CASCADE,
                                       related_name='goods_purchase_fk',
                                       verbose_name='goods in purchase')
    amount = models.PositiveSmallIntegerField(default=1, verbose_name='amount')

    objects = models.Manager()
