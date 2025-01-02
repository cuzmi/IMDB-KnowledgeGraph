import requests
from bs4 import BeautifulSoup
import tqdm

class GenreFilmURL:
    def __init__(self):
        # base_url = 'https://www.imdb.com/'
        self.interest_url = 'https://www.imdb.com/interest/all/'
        self.headers = {
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
        }

    def getfilmurl(self):
        response = requests.get(self.interest_url, headers=self.headers)
        if response.status_code == 200:
            print('Request Successfully!')
        else:
            print('Try request again.')

        soup = BeautifulSoup(response.text, 'html.parser')

        genre_ = soup.find_all('a',class_= 'ipc-slate-card__title ipc-slate-card__title--clickable sc-c5922af5-2 fhgilD')

        # genre_links = []
        genre_links = {}
        for item in genre_:
            link = [self.interest_url[:-13] + item.get('href')]
            genre_name = item.find('div', class_ = "ipc-slate-card__title-text ipc-slate-card__title-text--clamp-1").text
            if genre_name in genre_links:
                # 判断如果网页内容相同，则不添加
                response1 = requests.get(*link, headers = self.headers)
                response2 = requests.get(*genre_links[genre_name], headers = self.headers)
                if response1.text == response2.text:
                    print(f'Two same pages:{genre_name}.')
                else:
                    genre_links[genre_name] = genre_links[genre_name] + link
            else:
                genre_links[genre_name] = link

        movies = {}
        for genre, links in genre_links.items():
            if 'TV' in genre:
                continue
            print(f'Scraping {genre}')
            for link in links:
                response = requests.get(link, headers=self.headers)
                soup = BeautifulSoup(response.text, 'html.parser')
                all_section = soup.find_all('section', class_='ipc-page-section ipc-page-section--baseAlt')[:2]
                movies_page = all_section[0].find_all('a',
                                                      class_='ipc-poster-card__title ipc-poster-card__title--clamp-2 ipc-poster-card__title--clickable')

                for movie in tqdm.tqdm((movies_page), desc='In progress of retrieving data:'):
                    movie_links = movie.get('href')
                    movie_name = movie.find('span', {'data-testid': 'title'}).text

                    movies[movie_name] = movie_links

        return movies # {movie_name: url}

