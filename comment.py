import requests
import json

kaiten_times_table_name = 'kaiten_times'

def add_comment(cards_data, api_key, kaiten_times_table_name):
    print("add_comment start")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    card_comments = {}  

    for card in cards_data:
        card_id = card["Card ID"]  
        description_url = f'https://web-regata.kaiten.ru/api/latest/cards/{card_id}/'
        description_response = requests.get(description_url, headers=headers)
        if description_response.status_code == 200:
            card_data = description_response.json()
            comment = card_data.get("description", "N/A")
        else:
            comment = ""
        
        card_comments[card_id] = comment
        
    with open("comments.json", "w", encoding="utf-8") as json_file:
        json.dump(card_comments, json_file, ensure_ascii=False, indent=2)
    print('comments.json создан')