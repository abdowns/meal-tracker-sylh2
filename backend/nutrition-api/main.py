import requests, json, uvicorn, sys, sqlite3
from fastapi import FastAPI
from pydantic import BaseModel



app = FastAPI()
with open('foods.json', 'rt') as data:
    foods: list[dict] = json.load(data)

KEY = sys.argv[1]
ALL_FOOD_GROUPS = ['Gourds', 'Herbs and spices', 'Snack foods', 'Milk and milk products', 'Animal foods', 'Eggs', 'Confectioneries', 'Unclassified', 'Coffee and coffee products', 'Soy', 'Herbs and Spices', 'Beverages', 'Fruits', 'Cocoa and cocoa products', 'Aquatic foods', 'Baking goods', 'Teas', 'Vegetables', 'Nuts', 'Pulses', 'Cereals and cereal products', 'Dishes', 'Fats and oils', 'Baby foods']

@app.get("/")
async def root(food):
    url = "https://calorieninjas.p.rapidapi.com/v1/nutrition"

    querystring = {"query":food}

    headers = {
        "X-RapidAPI-Key": KEY,
        "X-RapidAPI-Host": "calorieninjas.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)

    info_obj = json.loads(response.text)
    item_info = info_obj["items"][0]
    more_info = search_foods(food)[0]
    f_dict = { # conversion to schema
        "name":item_info["name"],
        "info": more_info,
        "nutrition": {
          "calories": item_info["calories"],
          "total_fat_grams": item_info["fat_total_g"],
          "saturated_fat_grams": item_info["fat_saturated_g"],
          "cholesterol_milligrams": item_info["cholesterol_mg"],
          "sodium_milligrams":  item_info["sodium_mg"],
          "total_carb_grams": item_info["carbohydrates_total_g"],
          "dietary_fiber_grams": item_info["fiber_g"],
          "sugars_grams": item_info["sugar_g"],
          "proteins_grams": item_info["protein_g"],
          "potassium_milligrams": item_info["potassium_mg"],
        }
    }

    return f_dict

@app.get('/groups')
def get_food_groups():
    return ALL_FOOD_GROUPS

@app.get('/search')
def search_foods(query, groups=','.join(ALL_FOOD_GROUPS)):
    top_matches = []
    good_matches = []
    next_matches = []
    
    filter_groups = groups.split(',')

    for food in foods:
        food = {
            "name": food["name"],
            "group": food["food_group"],
            "subgroup": food["food_subgroup"],
            "description": food["description"],
            "image": f"https://foodb.ca/system/foods/pictures/{food['id']}/full/{food['id']}.png",
        }

        if not food['group'] in filter_groups:
            continue

        if food['name'].lower() == query.lower():
            top_matches.append(food)
        elif food['name'].lower().startswith(query.lower()):
            good_matches.append(food)
        elif query.lower() in food['name'].lower():
            next_matches.append(food)
        
        if len(top_matches) + len(good_matches) + len(next_matches) > 10:
            break
    
    all = []
    all.extend(top_matches)
    all.extend(good_matches)
    all.extend(next_matches)

    return all

uvicorn.run(app, reload=False)
