from django.shortcuts import render

from .models import Champion
from .extra_models import ChampionUnit


# Create your views here.
def champion_detail(request):
    champion = Champion.objects.get(name='Ashe')
    cu = ChampionUnit(champion, nickname='player1')
    return render(request, 'simulator/champion_sim.html', {'cu': cu})


def lab(request):
    champion = Champion.objects.get(name='Ashe')
    p1_init = ChampionUnit(champion, nickname='player1')
    p1_res = ChampionUnit(champion, nickname='player1')
    p2_init = ChampionUnit(champion, nickname='player2')
    p2_res = ChampionUnit(champion, nickname='player2')
    p1_res.attack(p2_res)
    return render(request, 'simulator/lab.html', {
        'p1_init': p1_init, 'p2_init': p2_init,
        'p1_res': p1_res, 'p2_res': p2_res,
    })
