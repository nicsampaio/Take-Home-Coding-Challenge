import requests
from bs4 import BeautifulSoup
import json

def parse_price(text):
    if text:
        return float(text.replace("R$", "").replace(".", "").replace(",", ".").strip())
    return None

url = 'https://infosimples.com/vagas/desafio/commercia/product.html'
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

resposta_final = {}

resposta_final['title'] = soup.select_one('h2#product_title').get_text(strip=True)

resposta_final['brand'] = soup.select_one('.brand').get_text(strip=True)

resposta_final['categories'] = [a.get_text(strip=True) for a in soup.select('nav.current-category a')]

paragrafos = [p.get_text(strip=True) for p in soup.select('.proddet p')]
resposta_final['description'] = "\n\n".join(paragrafos)

resposta_final['skus'] = []
for card in soup.select('.skus-area .card'):
    name = card.select_one('.prod-nome').get_text(strip=True)
    sku = card.select_one('meta[itemprop="sku"]')
    sku_code = sku['content'] if sku else None
    
    current_price_tag = card.select_one('.prod-pnow')
    old_price_tag = card.select_one('.prod-pold')
    
    current_price = parse_price(current_price_tag.get_text()) if current_price_tag else None
    old_price = parse_price(old_price_tag.get_text()) if old_price_tag else None
    
    available = 'Out of stock' not in card.get_text()
    
    resposta_final['skus'].append({
        "sku": sku_code,
        "name": name,
        "current_price": current_price,
        "old_price": old_price,
        "available": available
    })

resposta_final['properties'] = []
for row in soup.select('.pure-table tbody tr'):
    label = row.select_one('td b').get_text(strip=True) if row.select_one('td b') else None
    value = row.select('td')[-1].get_text(strip=True) if len(row.select('td')) > 1 else None
    if label and value:
        resposta_final['properties'].append({
            "label": label,
            "value": value
        })

resposta_final['reviews'] = []
for review in soup.select('.analisebox'):
    username = review.select_one('.analiseusername').get_text(strip=True)
    date = review.select_one('.analisedate').get_text(strip=True)
    stars = review.select_one('.analisestars').get_text(strip=True)
    score = stars.count('★') 
    text = review.select_one('p').get_text(strip=True)

    resposta_final['reviews'].append({
        "name": username,
        "date": date,
        "score": score,
        "text": text
    })

media = soup.select_one('#comments h4')
resposta_final['reviews_average_score'] = float(media.get_text(strip=True).split()[2].split('/')[0]) if media else None

resposta_final['url'] = url

with open('produto.json', 'w', encoding='utf-8') as f:
    json.dump(resposta_final, f, ensure_ascii=False, indent=2)
