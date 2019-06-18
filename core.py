from .models import Champion, EmptyResource, ManaResource, EnergyResource
import requests
from bs4 import BeautifulSoup as bs
import re
import pprint
import os
import json
import redis


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
