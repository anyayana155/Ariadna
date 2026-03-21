import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime

class CleanEventsParser:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        self.events = []
    
    def clean_title(self, title):
        """Избавление от мусора"""
        if not title:
            return ""
        
        # Удаляем мусорные символы
        title = re.sub(r'[\uE000-\uF8FF\uF000-\uFFFF-]', '', title)  # Unicode мусор
        title = re.sub(r'Р(еклама|еклами).*?(?=\.|$)', '', title, flags=re.I)  # Реклама
        title = re.sub(r'\\w{2,4}\d+', '', title)  # Код типа 7914
        title = re.sub(r'(Вход/Регистрация|Подтвердите|Логин).*', '', title, flags=re.I)
        title = re.sub(r'\s+', ' ', title).strip()
        
        return title
    
    def normalize_title(self, title):
        """Каноническое название для сравнения"""
        clean = self.clean_title(title)
        # Берём первую "нормальную" фразу
        sentences = re.split(r'[.!?]+', clean)
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20:
                return sentence[:100]
        return clean[:100]
    
    def is_real_event(self, title):
        clean = self.clean_title(title).lower()
        
        exclude = ['куда сходить', 'бесплатно', 'события', 'парки', 'логин', 'регистрация']
        if any(word in clean for word in exclude):
            return False
        
        include = ['концерт', 'спектакль', 'шоу', 'выставка', 'лекция', 'мастер', 'балет']
        if any(word in clean for word in include):
            return True
        
        return len(clean) > 40
    
    def classify_event(self, title):
        """Тип события"""
        clean = self.clean_title(title).lower()
        if any(w in clean for w in ['концерт']):
            return '🎵 Концерт'
        elif any(w in clean for w in ['театр', 'спектакль', 'балет']):
            return '🎭 Театр'
        elif any(w in clean for w in ['выставк', 'арт', 'экспози']):
            return '🖼️ Выставка'
        elif any(w in clean for w in ['шоу', 'рекордиум', 'темнота']):
            return '🎪 Шоу'
        return '🎉 Событие'
    
    def parse_kudago_clean(self):
        self.driver.get('https://kudago.com/msk/events/')
        time.sleep(8)
        
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        
        # Только карточки событий и заголовки
        event_elements = (soup.find_all(['h2','h3','a[href*="/event/"]', 'a[href*="/msk/event/"]']) +
                         soup.find_all('div', class_=re.compile('event|card|post')))
        
        print(f"Потенциальных событий: {len(event_elements)}")
        
        seen_normalized = set()
        real_count = 0
        
        for elem in event_elements[:50]: 
            raw_title = elem.get_text(strip=True)
            clean_title = self.clean_title(raw_title)
            norm_title = self.normalize_title(raw_title)
            
            if (len(clean_title) > 25 and self.is_real_event(clean_title) and 
                norm_title not in seen_normalized and '/event/' in str(elem)):
                
                # Ищем чистую ссылку
                link = (elem.find('a') or elem.find_parent('a'))
                url = link['href'] if link and link.get('href') else ''
                
                # Только ссылки на события
                if '/event/' in url and not url.startswith('http'):
                    url = 'https://kudago.com' + url
                
                if '/event/' in url:
                    self.events.append({
                        'site': 'KudaGo',
                        'title': clean_title[:140],
                        'url': url,
                        'type': self.classify_event(clean_title),
                        'datetime': datetime.now().strftime('%Y-%m-%d')
                    })
                    
                    seen_normalized.add(norm_title)
                    real_count += 1
                    print(f"  🎪 [{real_count}] {clean_title[:70]}...")
                    
                    if real_count >= 20:
                        break
        
        print(f"Событий: +{real_count}")
    
    def run(self):
        try:
            self.parse_kudago_clean()
            unique_events = []
            seen = set()
            for event in self.events:
                key = (event['url'], event['title'][:80])
                if key not in seen:
                    unique_events.append(event)
                    seen.add(key)
            
            # Сохраняем ЧИСТЫЙ результат
            with open('clean_events.json', 'w', encoding='utf-8') as f:
                json.dump(unique_events, f, ensure_ascii=False, indent=2)
            
            print(f"\nИТОГО: {len(unique_events)}")
            for i, event in enumerate(unique_events[:8], 1):
                print(f"{i:2d}. {event['type']} | {event['title']}")
                print(f"    📍 {event['url']}")
                print()
                
        except Exception as e:
            print(f"Ошибка: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.driver.quit()

if __name__ == "__main__":
    parser = CleanEventsParser()
    parser.run()
