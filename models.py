from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


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
        ordering = ('-patch_season', '-patch_detail' )

    def __str__(self):
        return '{} in patch {}.{}'.format(
            self.name, self.patch_season, self.patch_detail)


class ItemStatistics:
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

