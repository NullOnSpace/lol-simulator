from django.db import models
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from .tools import normalize


# Create your models here.
class ManaResource(models.Model):
    name = models.CharField(max_length=10, default='mana')
    mana = models.DecimalField(max_digits=6, decimal_places=2)
    mana_inc = models.DecimalField(max_digits=4, decimal_places=2)
    mana_regen = models.DecimalField(max_digits=4, decimal_places=2)
    mana_regen_inc = models.DecimalField(max_digits=4, decimal_places=2)


class EnergyResource(models.Model):
    name = models.CharField(max_length=10, default='energy')
    energy = models.DecimalField(max_digits=6, decimal_places=2)
    energy_inc = models.DecimalField(max_digits=4, decimal_places=2)
    energy_regen = models.DecimalField(max_digits=4, decimal_places=2)
    energy_regen_inc = models.DecimalField(max_digits=4, decimal_places=2)


class EmptyResource(models.Model):
    name = models.CharField(max_length=10, default='anguish')


class Champion(models.Model):
    name = models.CharField(max_length=20)
    title = models.CharField(max_length=40)
    health = models.DecimalField(max_digits=7, decimal_places=3)
    health_inc = models.DecimalField(max_digits=6, decimal_places=3)
    hp_regen = models.DecimalField(max_digits=5, decimal_places=3)
    hp_regen_inc = models.DecimalField(max_digits=5, decimal_places=3)
    res_ct = models.ForeignKey(ContentType, limit_choices_to={
                                     'model__in': ('energyresource',
                                                   'manaresource',
                                                   'emptyresource')},
                               on_delete=models.CASCADE)
    res_id = models.PositiveIntegerField(null=True, blank=True, db_index=True)
    resource = GenericForeignKey('res_ct', 'res_id')
    move_speed = models.PositiveSmallIntegerField()
    attack_damage = models.DecimalField(max_digits=8, decimal_places=3)
    attack_damage_inc = models.DecimalField(max_digits=5, decimal_places=3)
    attack_speed = models.DecimalField(max_digits=5, decimal_places=3)
    attack_speed_inc = models.DecimalField(max_digits=5, decimal_places=3)
    range = models.PositiveSmallIntegerField()
    armor = models.DecimalField(max_digits=7, decimal_places=3)
    armor_inc = models.DecimalField(max_digits=5, decimal_places=3)
    magic_resist = models.DecimalField(max_digits=7, decimal_places=3)
    magic_resist_inc = models.DecimalField(max_digits=5, decimal_places=3)
    patch_season = models.PositiveSmallIntegerField()
    patch_detail = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ('-patch_season', '-patch_detail')

    def __str__(self):
        return '{} in patch {}.{}'.format(
            self.name, self.patch_season, self.patch_detail)


class ItemStatistics(models.Model):
    ability_power = models.IntegerField(null=True)
    ap_min = models.IntegerField(null=True)
    ap_max = models.IntegerField(null=True)
    armor = models.IntegerField(null=True)
    attack_damage = models.IntegerField(null=True)
    attack_speed = models.IntegerField(null=True)
    cdr = models.IntegerField(null=True)
    critical_strike = models.IntegerField(null=True)
    golden_gen = models.IntegerField(null=True)
    hp_regen = models.IntegerField(null=True)
    health = models.IntegerField(null=True)
    life_steal = models.IntegerField(null=True)
    ls_monster = models.IntegerField(null=True)
    magic_resist = models.IntegerField(null=True)
    mana = models.IntegerField(null=True)
    mana_min = models.IntegerField(null=True)
    mana_max = models.IntegerField(null=True)
    mana_regen = models.IntegerField(null=True)
    move_speed = models.IntegerField(null=True)
    ms_percent = models.IntegerField(null=True)

    @classmethod
    def get_or_create(cls, **kwargs):
        qs = cls.objects.filter(**kwargs)
        if qs:
            fields = set(field.attname for field in cls._meta.get_fields())
            none_value_fields = fields.difference(set(kwargs.keys()))
            for obj in qs:
                for field in none_value_fields:
                    if getattr(obj, field) is not None:
                        break
                else:
                    return obj
        obj = cls(**kwargs)
        obj.save()
        return obj


class Recipe(models.Model):
    item1_ct = models.ForeignKey(ContentType, null=True,
                                 related_name='ingre1',
                                 on_delete=models.CASCADE)
    item1_id = models.PositiveIntegerField(null=True)
    item1 = GenericForeignKey('item1_ct', 'item1_id')
    item2_ct = models.ForeignKey(ContentType, null=True,
                                 related_name='ingre2',
                                 on_delete=models.CASCADE)
    item2_id = models.PositiveIntegerField(null=True)
    item2 = GenericForeignKey('item2_ct', 'item2_id')
    item3_ct = models.ForeignKey(ContentType, null=True,
                                 related_name='ingre3',
                                 on_delete=models.CASCADE)
    item3_id = models.PositiveIntegerField(null=True)
    item3 = GenericForeignKey('item3_ct', 'item3_id')
    item4_ct = models.ForeignKey(ContentType, null=True,
                                 related_name='ingre4',
                                 on_delete=models.CASCADE)
    item4_id = models.PositiveIntegerField(null=True)
    item4 = GenericForeignKey('item4_ct', 'item4_id')

    @property
    def item_number(self):
        return len(self.recipe_list)

    @property
    def recipe_list(self):
        max_num = 4
        res = list()
        for i in range(1, max_num+1):
            item = getattr(self, 'item{}'.format(i))
            if item is not None:
                res.append(item)
            else:
                break
        return res

    @property
    def ingre_cost(self):
        cost = sum(item.total_cost for item in self.recipe_list)
        return cost

    @classmethod
    def get_or_create(cls, items):
        qss = set()
        for item in set(items):
            qs = Recipe.objects.filter(Q(item1=item) | Q(item2=item)
                                       | Q(item3=item) | Q(item4=item))
            if not qs:
                break
            else:
                if qss:
                    qss.intersection_update(qs)
                    if not qss:
                        break
                else:
                    qss = set(qs)
        else:
            for obj in qss:
                recipe_list = obj.recipe_list
                for item in items:
                    if item in recipe_list:
                        recipe_list.remove(item)
                    else:
                        break
                else:
                    if not recipe_list:
                        return obj
        obj = Recipe()
        for n, item in enumerate(items):
            setattr(obj, 'item{}'.format(n), item)
        obj.save()
        return obj

    def __str__(self):
        return ' + '.join(self.recipe_list)


class BaseItem(models.Model):
    item_code = models.IntegerField()
    tier = models.CharField(max_length=15)
    map_availability = models.CharField(max_length=16)
    name = models.CharField(max_length=50)
    normalize_name = models.CharField(max_length=50)
    patch_season = models.IntegerField()
    patch_detail = models.IntegerField()
    cost = models.IntegerField()
    statistics = models.ForeignKey(ItemStatistics, on_delete=models.CASCADE,
                                   related_name='%(class)s_set',
                                   related_query_name='%(class)ss')

    class Meta:
        abstract = True

    @property
    def patch(self):
        return '{}.{}'.format(self.patch_season, self.patch_detail)

    @property
    def total_cost(self):
        return self.cost

    def __str__(self):
        return '{} in {}'.format(self.name, self.patch)

    def save(self, *args, **kwargs):
        self.normalize_name = normalize(self.name)
        return super().save(*args, **kwargs)


class CompoundItem(BaseItem):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='%(class)s_set',
                               related_query_name='%(class)ss')

    class Meta:
        abstract = True

    @property
    def total_cost(self):
        return self.recipe.ingre_cost + self.cost


class BasicItem(BaseItem):

    def save(self, *args, **kwargs):
        self.tier = 'basic'
        return super().save(*args, **kwargs)


class StarterItem(BaseItem):

    def save(self, *args, **kwargs):
        self.tier = 'starter'
        return super().save(*args, **kwargs)


class AdvancedItem(CompoundItem):

    def save(self, *args, **kwargs):
        self.tier = 'advanced'
        return super().save(*args, **kwargs)


class FinishedItem(CompoundItem):

    def save(self, *args, **kwargs):
        self.tier = 'finished'
        return super().save(*args, **kwargs)
