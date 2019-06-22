class ChampionUnit:
    default_zero_list = [
        'ability_power', 'cdr', 'critical_probability', 'life_steal',
        'armor_penetration_fixed', 'armor_penetration_percent',
        'magic_resist_penetration_fixed',
        'magic_resist_penetration_percent',
    ]
    base_initial_dict = {
        'health': 'health', 'health_regen': 'hp_regen',
        'move_speed': 'move_speed', 'attack_damage': 'attack_damage',
        'attack_speed': 'attack_speed', 'armor': 'armor',
        'magic_resist': 'magic_resist', 'range': 'range'
    }
    prop_set = False

    def __init__(self, champion, nickname='Anonymous'):
        if self.prop_set is False:
            self.set_properties()
        self.nickname = nickname
        self.name = champion.name
        resource = champion.resource
        self.resource_type = resource.name
        if self.resource_type in ['mana', 'energy']:
            suffixes = ['' , '_regen']
            for suffix in suffixes:
                setattr(self, 'base_resource'+suffix,
                        getattr(resource, resource.name+suffix))
                setattr(self, 'resource'+suffix+'_inc',
                        getattr(resource, resource.name+suffix+'_inc'))
                if self.resource_type == 'mana':
                    setattr(self, 'equipped_resource'+suffix, dict())
                    setattr(self, 'extra_resource'+suffix, dict())
            self.current_resource = self.total_resource
        else:
            self.base_resource = 0
            self.current_resource = 0

        inc_property_list = [
            'health', 'health_regen', 'attack_damage', 'attack_speed', 'armor',
            'magic_resist',
        ]
        for k, v in self.base_initial_dict.items():
            setattr(self, 'base_'+k, getattr(champion, v))
        for i in inc_property_list:
            setattr(self, 'base_'+i+'_inc',
                    getattr(champion, self.base_initial_dict[i]+'_inc'))

        for j in self.default_zero_list:
            setattr(self, 'base_'+j, 0)
        for p in self.default_zero_list + list(self.base_initial_dict.keys()):
            setattr(self, 'equipped_'+p, dict())
            setattr(self, 'extra_'+p, dict())
        self.level = 1
        self.ability_Q_lv = 0
        self.ability_W_lv = 0
        self.ability_E_lv = 0
        self.ability_R_lv = 0
        self.buff = dict()
        self.trigger = dict()
        self.current_health = self.total_health
        self.status = 'free'

    @property
    def total_resource(self):
        if self.resource_type in ['mana']:
            return (self.base_resource
                    + sum(self.equipped_resource.values())
                    + sum(self.extra_resource.values()))
        else:
            return self.base_resource

    @property
    def bonus_resource(self):
        if self.resource_type in ['mana']:
            return self.total_resource - self.base_resource
        else:
            return 0

    @classmethod
    def set_properties(cls):
        def wrapper(attr):
            def total_getter(self):
                base = getattr(self, 'base_'+attr)
                equipped = getattr(self, 'equipped_'+attr)
                extra = getattr(self, 'extra_'+attr)
                return base + sum(equipped.values()) + sum(extra.values())

            def bonus_getter(self):
                base = getattr(self, 'base_'+attr)
                equipped = getattr(self, 'equipped_'+attr)
                extra = getattr(self, 'extra_'+attr)
                return (getattr(self, 'total_'+attr)
                        - getattr(self, 'base_'+attr))
            return (total_getter, bonus_getter)
        for attr in cls.default_zero_list+list(cls.base_initial_dict.keys()):
            t_getter, b_getter = wrapper(attr)
            setattr(cls, 'total_'+attr, property(t_getter))
            setattr(cls, 'bonus_'+attr, property(b_getter))
        cls.prop_set = True

    def take_damage(self, dmg):
        if self.status == 'dead':
            dmg.state = 'already dead'
            return dmg
        diff = self.current_health - dmg.settled_amount
        if diff <= 0:
            self.status = 'dead'
            self.current_health = 0
            dmg.actual_amount = self.current_health
        else:
            self.current_health = diff
        dmg.state = 'success'
        return dmg

    def attack(self, target):
        projectile = Projectile(self, target,
                                'physical', 'attack', self.total_attack_damage)
        projectile.deal_damage()


class Damage:
    dmg_resist_dict = {
        'physical': 'armor', 'magic': 'magic_resist'
    }

    def __init__(self, source, target, cate, form, amount):
        self.source = source
        self.target = target
        self.cate = cate
        self.form = form
        self.amount = amount
        self.settled_amount = self.get_final_damage()
        self.actual_amount = 0

    def get_final_damage(self):
        resist = getattr(
            self.target,
            'total_' + self.dmg_resist_dict.get(self.cate, 'invalid'),
            0
        )
        return self.amount * (1 - resist/(100 + resist))

    def post_deal(self):
        pass


class Projectile:
    def __init__(self, source, target, cate, form, amount):
        self.source = source
        self.target = target
        self.cate = cate
        self.form = form
        self.amount = amount

    def deal_damage(self):
        dmg = Damage(self.source, self.target, self.cate,
                     self.form, self.amount)
        # in future version, there ought to be a method to get target list
        # other than to get target directly
        dealt_dmg = self.target.take_damage(dmg)
        if dealt_dmg.state == 'success':
            dealt_dmg.post_deal()


def basic_test():
    from .models import Champion
    ashe =Champion.objects.get(name='Ashe')
    ad_carry = ChampionUnit(ashe, nickname='player1')
    return ad_carry
