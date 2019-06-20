import redis
from tools import normalize

r = redis.Redis(host='localhost',port=6379)

def recipe_check():
    code_dict = r.hgetall('lol:item_code')
    recipe_dict = r.hgetall('lol:item_recipe')
    recipe_str_dict = {normalize(k.decode()): v.decode()
                       for k, v in recipe_dict.items()}
    items = list(map(lambda x: normalize(x.decode()), code_dict.keys()))
    for item in items:
        recipe = recipe_str_dict.get(item, None)
        if recipe is None:
            continue
        ingres = list(map(normalize, recipe.split(':')))
        for ingre in ingres:
            if ingre not in items:
                print(item, ingre)


if __name__ == '__main__':
    recipe_check()
    print('done')
