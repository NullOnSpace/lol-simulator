from .models import (Champion, EmptyResource, ManaResource, EnergyResource,
                     BasicItem, StarterItem, CompoundItem, AdvancedItem,
                     FinishedItem, Recipe, ItemStatistics)
from bs4 import BeautifulSoup as bs
import re
import pprint
import os
import json
import redis
from .tools import normalize


def parse_lol_file(content):
    soup = bs(content, 'html.parser')
    champion_tb = soup.select('#infoboxChampion')[0]
    name_tag = champion_tb.find(class_='infobox-title')
    name = str(name_tag.string)
    title_tag = champion_tb.find(string='Title').parent.next_sibling
    title = str(title_tag.string)
    pb_tag = champion_tb.find(string='Release Date').parent.next_sibling
    pb_date = str(pb_tag.string)
    health_tag = champion_tb.find(string='Health'
                                  ).parent.parent.parent.next_sibling
    health = str(health_tag.string)
    hp_regen_tag = champion_tb.find(string='HP Regen'
                                    ).parent.parent.parent.next_sibling
    hp_regen = str(hp_regen_tag.string)
    ms_tag = champion_tb.find(string='Movespeed'
                              ).parent.parent.parent.next_sibling
    ms = str(ms_tag.string)
    ad_tag = champion_tb.find(string='Attack Dmg'
                              ).parent.parent.parent.next_sibling
    ad = str(ad_tag.string)
    as_tag = champion_tb.find(string='Attack Spd'
                              ).parent.parent.parent.next_sibling
    asd = str(as_tag.string)
    range_tag = champion_tb.find(string='Range'
                                 ).parent.parent.parent.next_sibling
    rg = str(range_tag.string)
    armor_tag = champion_tb.find(string='Armor'
                                 ).parent.parent.parent.next_sibling
    armor = str(armor_tag.string)
    mr_tag = champion_tb.find(string='Magic Resist'
                              ).parent.parent.parent.next_sibling
    mr = str(mr_tag.string)
    patch_tag = soup.find(id='Patch_History').parent.next_sibling.next_sibling
    patch = patch_tag.find(title=re.compile(r'^(Patch|V\d)'))['title']
    resource_dict = {'mana': 'Mana Regen', 'energy': 'Energy Regen'}
    resource_tag = champion_tb.find(string=['Mana', 'Energy'])
    if resource_tag:
        resource_type = str(resource_tag.string).lower()
        resource = str(resource_tag.parent.parent.parent.next_sibling.string)
        resource_regen = str(
            champion_tb.find(string=resource_dict[resource_type]
                             ).parent.parent.parent.next_sibling.string)
    else:
        resource = None
    attr_list = ['name', 'title', 'pb_date', 'health', 'hp_regen', 'ms',
                 'ad', 'asd', 'rg', 'armor', 'mr', 'patch']
    local_dict = locals()
    try:
        attr_dict = {attr: local_dict[attr] for attr in attr_list}
    except KeyError:
        del patch_tag
        del content
        del soup
        del champion_tb
        print(type(locals()))
        print(locals()['name'])
        pprint.pprint(locals())
        raise
    if resource:
        rs_dict = {'type': resource_type, 'resource': resource,
                   'res_regen': resource_regen}
        attr_dict['resource'] = rs_dict
    return attr_dict


def temp_solve():
    r = redis.Redis(host="localhost", port=6379)
    fp = 'E://lol_champion'
    for fn in os.listdir(fp):
        with open(os.path.join(fp, fn), 'rb') as fd:
            dd = parse_lol_file(fd.read())
            r.hset('lol', 'champion:{}'.format(dd['name']), json.dumps(dd))


def initialize_model():
    r = redis.Redis(host="localhost", port=6379)
    keys = r.hkeys('lol')
    for k in keys:
        champion = json.loads(r.hget('lol', k))
        obj = Champion()
        obj.name = champion['name']
        res = re.match(r'(Patch|V)\s*(?P<patch>[\d.]+)', champion['patch'])
        obj.patch_season, obj.patch_detail = res.group('patch').split('.')
        if Champion.objects.filter(
                name=obj.name,
                patch_season=obj.patch_season,
                patch_detail=obj.patch_detail).exists():
            continue
        obj.title = champion['title']
        res = re.match(r'(?P<hp>[\d.]+)\s*(?:/\s*\d+\s*)?\(\+\s+(?P<hpr>[\d.]+)',
                       champion['health'])
        obj.health = res.group('hp')
        obj.health_inc = res.group('hpr')
        res = re.match(r'(?P<hpre>[\d.]+)\s*\(\+\s+(?P<hprei>[\d.]+)\)',
                       champion['hp_regen'])
        obj.hp_regen = res.group('hpre')
        obj.hp_regen_inc = res.group('hprei')
        obj.move_speed = re.match(r'^(?P<ms>\d+)',
                                  champion['ms']).group('ms')
        res = re.match(r'(?P<ad>[\d.]+)\s*(?:/\s*\d+\s*)?\(\+\s+(?P<adr>[\d.]+)',
                       champion['ad'])
        obj.attack_damage = res.group('ad')
        obj.attack_damage_inc = res.group('adr')
        res = re.match(r'(?P<as>[\d.]+)\s*\(\+\s+(?P<asr>[\d.]+)%',
                       champion['asd'])
        if not res:
            res = re.match(
                r'(?P<as>[\d.]+)\s*\(\+\s*[\d.%]+\s*\(\+(?P<asr>[\d.]+)',
                champion['asd'])
        obj.attack_speed = res.group('as')
        obj.attack_speed_inc = res.group('asr')
        obj.range = re.match(r'\d+', champion['rg']).group(0)
        res = re.match(
            r'(?P<ar>[\d.]+)\s*(?:/\s*[\d.]+\s*)?\(\+\s+(?P<arr>[\d.]+)',
            champion['armor'])
        obj.armor = res.group('ar')
        obj.armor_inc = res.group('arr')
        res = re.match(
            r'(?P<mr>[\d.]+)\s*(?:/\s*[\d.]+\s*)?\(\+\s+(?P<mrr>[\d.]+)',
            champion['mr'])
        obj.magic_resist = res.group('mr')
        obj.magic_resist_inc = res.group('mrr')
        resource = champion.get('resource')
        if resource:
            res = re.match(r'(?P<rs>[\d.]+)\s*\(\+\s+(?P<rsr>[\d.]+)\)',
                           resource['resource'])
            rs_base = res.group('rs')
            rs_inc = res.group('rsr')
            res = re.match(r'(?P<rsr>[\d.]+)\s*\(\+\s+(?P<rsrr>[\d.]+)\)',
                           resource['res_regen'])
            rsr_base = res.group('rsr')
            rsr_inc = res.group('rsrr')
            if resource['type'] == 'mana':
                rs = ManaResource()
                rs.mana = rs_base
                rs.mana_inc = rs_inc
                rs.mana_regen = rsr_base
                rs.mana_regen_inc = rsr_inc
            elif resource['type'] == 'energy':
                rs = EnergyResource()
                rs.energy = rs_base
                rs.energy_inc = rs_inc
                rs.energy_regen = rsr_base
                rs.energy_regen_inc = rsr_inc
            rs.save()
        else:
            rs = EmptyResource()
            rs.save()
        obj.resource = rs
        obj.save()


def collect_item_info():
    item_cate = ['Basic', 'Starter', 'Advanced', 'Finished']
    fp_tmpl = 'E://lol_item/{} Items/'
    for cate in item_cate:
        fp = fp_tmpl.format(cate)
        for fn in os.listdir(fp):
            path = os.path.join(fp, fn)
            refine_item_file(path)


def refine_item_file(file_full_path):
    fn = os.path.basename(file_full_path)
    r = redis.Redis(host='localhost', port=6379)
    with open(file_full_path, 'rb') as fd:
        soup = bs(fd.read(), 'html.parser')
    tb = soup.find(id='infoboxItem')
    item_name = fn.replace(' ', '-')
    code_td = tb.find('td', string='Item Code')
    code = code_td.next_sibling.text
    r.hset('lol:item_code', item_name, code)
    map_td = tb.find('td', string='Map Availability')
    map_type = map_td.next_sibling.text
    r.hset('lol:item_map', item_name, map_type)
    tier_td = tb.find('td', string='Tier')
    tier = tier_td.next_sibling.text
    r.hset('lol:item_tier', item_name, tier)
    patch_tag = soup.find(id='Patch_History'
                          ).parent.next_sibling.next_sibling
    patch = patch_tag.find('a')['data-to-target-title']
    r.hset('lol:item_patch', item_name, patch)
    st_tr = soup.find('tr', string='Statistics')
    recipe_tr = tb.find('tr', string='Recipe')
    if recipe_tr:
        recipe_tr = recipe_tr.next_sibling
        a_tags = recipe_tr.find_all('a')
        cost_pattern = re.compile(r'\+\s*(?P<cost>\d+)')
        cost_tag = recipe_tr.find(string=cost_pattern)
        if cost_tag:
            cost = str(cost_tag.string)
            cost = cost_pattern.search(cost).group('cost')
        else:
            cost_tag = soup.find('b', string='Total Cost:')
            if not cost_tag:
                cost = 0
            else:
                cost_tag = cost_tag.next_sibling
                cost = str(cost_tag.string).strip()
        r.hset('lol:item_cost', item_name, cost)
        ingre_list = list()
        for a_tag in a_tags:
            ingre_name = re.match(
                r'(?P<n>[\w\s.\'\-]+)', a_tag['title']
            ).group('n').strip()
            ingre_list.append(ingre_name)
        else:
            if ingre_list:
                ingre_str = ':'.join(ingre_list)
                r.hset('lol:item_recipe', item_name, ingre_str)
    if not st_tr:
        return
    for tr_tag in st_tr.next_siblings:
        if tr_tag.find('th'):
            break
        td1 = tr_tag.find('td')
        td2 = td1.next_sibling
        st_name = td1.text
        st_value = td2.text
        r.hset('lol:item:{}'.format(item_name), st_name, st_value)
        r.sadd(st_name, st_value)
        r.sadd('lol:statistics', st_name)


def item_to_model():
    r = redis.Redis(host='localhost', port=6379)
    md_dict = {'Starter': StarterItem, 'Basic': BasicItem,
               'Advanced': AdvancedItem, 'Finished': FinishedItem}
    name_list = list(get_item_names())
    for name in name_list:
        name = name.decode()
        md = md_dict[r.hget('lol:item_tier', name).decode()]
        item = md()
        item.item_code = int(r.hget('lol:item_code', name))
        patch_list = r.hget('lol:item_patch', name).decode()[5:].split('.')
        patch_list = list(map(
            lambda x: re.sub(r'\D', '', x),
            patch_list
        ))
        item.patch_season = int(patch_list[0])
        item.patch_detail = int(patch_list[-1])
        if md.objects.filter(item_code=item.item_code,
                             patch_detail=item.patch_detail,
                             patch_season=item.patch_season):
            continue
        if CompoundItem in item.__class__.__bases__:
            recipe = get_recipe_obj(name)
            if recipe is None:
                name_list.append(name)
                print(name)
                continue
        item.map_availability = r.hget('lol:item_map', name).decode()
        item.name = name
        item.cost = int(r.hget('lol:item_cost', name))
        stat = get_item_stat_obj(name)
        item.statistics = stat
        item.save()


def get_item_names():
    r = redis.Redis(host='localhost', port=6379)
    black_list = [b'Remnant-of-the-Ascended', b'Remnant-of-the-Aspect',
                  b'Remnant-of-the-Watchers']
    name_set = set(r.hkeys('lol:item_code')).difference(black_list)
    return name_set


def get_recipe_obj(name):
    r = redis.Redis(host='localhost', port=6379)
    key = 'lol:item_recipe'
    assert r.hexists(key, name), 'recipe {} not exists'.format(name)
    recipe = r.hget(key, name).decode()
    ingre_list = list()
    for ingre in recipe.split(':'):
        norm_name = normalize(ingre)
        for Md in BasicItem, AdvancedItem, StarterItem, FinishedItem:
            qs = Md.objects.filter(normalize_name=norm_name)
            if qs:
                ingre_list.append(qs[0])
                break
        else:
            return None
    recipe = Recipe.get_or_create(ingre_list)
    return recipe


def get_item_stat_obj(name):
    r = redis.Redis(host='localhost', port=6379)
    key = 'lol:item:{}'.format(name)
    stat_dict = {
        'Ability Pwr': ap, 'Armor': armor, 'Attack Dmg': ad, 'Attack Spd': asd,
        'CDR': cdr, 'Crit Strike': cs, 'Golden Gen': gg, 'HP Regen': hpr,
        'Health': health, 'Life Steal': ls, 'Magic Resist': mr, 'Mana': mana,
        'Mana Regen': manag, 'Movespeed': ms,
    }
    model_dict = dict()
    for k in r.hkeys(key):
        k_str = k.decode()
        if k_str in stat_dict:
            model_dict.update(stat_dict[k_str](r.hget(key, k)))
    obj = ItemStatistics.get_or_create(**model_dict)
    return obj


def ap(v):
    if type(v) is bytes:
        v = v.decode()
    m1 = re.fullmatch(r'\s*(?P<ap>\d+)\s*', v)
    if m1:
        return {'ability_power': m1.group('ap')}
    m2 = re.fullmatch(
        r'\s*(?P<apmin>\d+)\s*-\s*(?P<apmax>\d+)\s*\(based\s*on\s*level\)\s*',
        v
    )
    if m2:
        return {'ap_min': m2.group('apmin'), 'ap_max': m2.group('apmax')}
    return dict()


def armor(v):
    if type(v) is bytes:
        v = v.decode()
    m1 = re.fullmatch(r'\s*(?P<armor>\d+)\s*', v)
    if m1:
        return {'armor': m1.group('armor')}
    return dict()


def ad(v):
    if type(v) is bytes:
        v = v.decode()
    m1 = re.fullmatch(r'\s*(?P<ad>\d+)\s*', v)
    if m1:
        return {'attack_damage': m1.group('ad')}
    return dict()


def asd(v):
    if type(v) is bytes:
        v = v.decode()
    m1 = re.fullmatch(r'\s*(?P<asd>\d+)%\s*', v)
    if m1:
        return {'attack_speed': m1.group('asd')}
    return dict()


def cdr(v):
    if type(v) is bytes:
        v = v.decode()
    m1 = re.fullmatch(r'\s*(?P<cdr>\d+)%\s*', v)
    if m1:
        return {'cdr': m1.group('cdr')}
    return dict()


def cs(v):
    if type(v) is bytes:
        v = v.decode()
    m1 = re.fullmatch(r'\s*\+?(?P<cs>\d+)%\s*', v)
    if m1:
        return {'critical_strike': m1.group('cs')}
    return dict()


def gg(v):
    if type(v) is bytes:
        v = v.decode()
    m1 = re.fullmatch(r'\s*\+(?P<gg>\d+)\s*(?:Gold)?\s*per 10 seconds\s*', v)
    if m1:
        return {'golden_gen': m1.group('gg')}
    return dict()


def hpr(v):
    if type(v) is bytes:
        v = v.decode()
    m1 = re.fullmatch(r'\s*(?P<hpr>\d+)%\s*Base Health Regen\s*', v)
    if m1:
        return {'hp_regen': m1.group('hpr')}
    return dict()


def health(v):
    if type(v) is bytes:
        v = v.decode()
    m1 = re.fullmatch(r'\s*(?P<hp>\d+)\s*', v)
    if m1:
        return {'health': m1.group('hp')}
    return dict()


def ls(v):
    if type(v) is bytes:
        v = v.decode()
    m1 = re.fullmatch(r'\s*(?P<ls>\d+)%\s*', v)
    if m1:
        return {'life_steal': m1.group('ls')}
    m2 = re.fullmatch(r'\s*(?P<ls>\d+)%\s*vs Monsters\s*', v)
    if m2:
        return {'ls_monster': m2.group('ls')}
    return dict()


def mr(v):
    if type(v) is bytes:
        v = v.decode()
    m1 = re.fullmatch(r'\s*(?P<mr>\d+)\s*', v)
    if m1:
        return {'magic_resist': m1.group('mr')}
    return dict()


def mana(v):
    if type(v) is bytes:
        v = v.decode()
    m1 = re.fullmatch(r'\s*(?P<mana>\d+)\s*', v)
    if m1:
        return {'mana': m1.group('mana')}
    m2 = re.fullmatch(
        r'\s*(?P<mmin>\d+)\s*-\s*(?P<mmax>\d+)\s*\(based\s*on\s*level\)\s*',
        v
    )
    if m2:
        return {'mana_min': m2.group('mmin'), 'mana_max': m2.group('mmax')}
    return dict()


def manag(v):
    if type(v) is bytes:
        v = v.decode()
    m1 = re.fullmatch(r'\s*(?P<mnr>\d+)%\s*Base Mana\s*(?:Regen)?\s*', v)
    if m1:
        return {'mana_regen': m1.group('mnr')}
    return dict()


def ms(v):
    if type(v) is bytes:
        v = v.decode()
    m1 = re.fullmatch(r'\s*(?P<ms>\d+)\s*', v)
    if m1:
        return {'move_speed': m1.group('ms')}
    m2 = re.fullmatch(r'\s*(?P<msp>\d+)%\s*', v)
    if m2:
        return {'ms_percent': m2.group('msp')}
    return dict()
