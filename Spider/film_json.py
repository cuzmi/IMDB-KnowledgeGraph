from film_url_scraping import *
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

import re
import json
from imdb import IMDb
import time

class Film2Json():
    def __init__(self, movie_url):
        self.base_url = 'https://www.imdb.com/'
        self.headers = self.headers = {
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
        }
        self.movie_url = movie_url
        self.url = self.base_url + movie_url

    def getinfo(self):
        response = requests.get(self.url, headers=self.headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        movie_data = {}
        data_keys = ['Directors', 'Writers', 'Stars', 'Actors', 'Rating', 'Plot', 'Genres', 'Released date',
                     'Countries of origin',
                     'Language', 'Also known as', 'Production companies','Runtime']
        for key in data_keys:
            if key not in ['Rating', 'Plot', 'Released date']:
                movie_data[key] = []
            else:
                movie_data[key] = None

        # 从最初的界面提取  导演，编剧，主演 get
        try:
            persons = soup.find('div', class_='sc-70a366cc-2 bscNnP')
            all_person = [a.text for a in persons.select('li[data-testid="title-pc-principal-credit"] a')]


            target = 'Directors'
            for person in all_person:
                if person == '':
                    continue
                if person in ['Writers', 'Stars']:
                    target = person
                    continue
                movie_data[target] += [person]

            actors = soup.find_all('a', {'data-testid': 'title-cast-item__actor'})
            for actor in actors:
                if actor.text in movie_data['Stars']:
                    continue
                movie_data['Actors'] += [actor.text]

        except Exception:
            pass

        rating = soup.find_all('span', class_='sc-d541859f-1 imUuxf')
        movie_data['Rating'] = rating[0].text

        try:
            # Detail部分
            release_date_section = soup.find('li', {'data-testid': 'title-details-releasedate'})
            if release_date_section:
                release_date = release_date_section.find('a',
                                                         class_='ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link').text.strip()
            else:
                release_date = "Not found"
            movie_data['Released date'] = release_date
        except Exception:
            pass


        try:
            # 提取 "Countries of origin"
            countries_of_origin_section = soup.find('li', {'data-testid': 'title-details-origin'})
            if countries_of_origin_section:
                countries_of_origin = [a.text.strip() for a in countries_of_origin_section.find_all('a')]
            else:
                countries_of_origin = []

            movie_data['Countries of origin'] += countries_of_origin
        except Exception:
            pass

        try:
            # 提取 "Language"
            language_section = soup.find('li', {'data-testid': 'title-details-languages'})
            if language_section:
                language = [a.text.strip() for a in language_section.find_all('a')]
            else:
                language = []
            movie_data['Language'] += language
        except Exception:
            pass

        try:
            # 提取 "Also known as"
            akas_section = soup.find('li', {'data-testid': 'title-details-akas'})
            if akas_section:
                akas = [span.text.strip() for span in
                        akas_section.find_all('span', class_='ipc-metadata-list-item__list-content-item')]
            else:
                akas = []

            movie_data['Also known as'] += akas
        except Exception:
            pass

        try:
            # 提取 "Production companies"
            production_companies_section = soup.find('li', {'data-testid': 'title-details-companies'})
            if production_companies_section:
                production_companies = [a.text.strip() for a in production_companies_section.find_all('a') if
                                        a.text.strip()]
            else:
                production_companies = []

            movie_data['Production companies'] += production_companies
        except Exception:
            pass

        try:
            runtime_section = soup.find('li', {'data-testid': 'title-techspec_runtime'})
            runtime = runtime_section.find('div', class_='ipc-metadata-list-item__content-container').text
            movie_data['Runtime'] = runtime
        except Exception:
            pass

        extra_data = self.getpg()
        movie_data.update(extra_data)

        return movie_data




    # def getjs(self, movie_data):
    #     # 初始化 WebDriver
    #     service = Service('./chromedriver.exe')
    #     driver = webdriver.Chrome(service=service)
    #
    #     # 打开目标页面
    #     driver.get(self.url)
    #
    #     # 设置等待时间（单位：秒）
    #     wait_time = 6
    #
    #     # 滚动并等待加载完storyline部分和genre
    #     def gradual_scroll():
    #         for _ in range(5):
    #
    #             driver.execute_script("window.scrollBy(0, 1200);")  # 滚动1000px
    #             try:
    #                 WebDriverWait(driver, 3).until(
    #                     EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="storyline-plot-summary"]'))
    #                     # 等待 storyline 部分
    #                 )
    #                 print("Plot loaded!")
    #             except Exception as e:
    #                 pass
    #
    #             # 继续等待 genre 部分加载
    #             try:
    #                 WebDriverWait(driver, 3).until(
    #                     EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="storyline-genres"]'))
    #                     # 等待 genre 部分
    #                 )
    #                 print("Genre loaded!")
    #             except Exception as e:
    #                 pass
    #
    #     # 执行逐步滑动，直到页面加载完
    #     gradual_scroll()
    #
    #
    #     # 提取数据或进行其他操作
    #     # 例如，获取剧情内容
    #     storyline_element = driver.find_element(By.CSS_SELECTOR, '[data-testid="storyline-plot-summary"]')
    #     storyline = storyline_element.text.strip()
    #     movie_data['Plot'] = storyline
    #
    #     # genre部分还需要处理
    #     genres_element = driver.find_element(By.CSS_SELECTOR, '[data-testid="storyline-genres"]')
    #     text = re.sub(r'-(\w)', lambda match: '-' + match.group(1).lower(), genres_element.text)
    #     genres = re.findall(r'[A-Z][a-z]*(?:-[a-z]+)*', text)
    #     movie_data['Genres'] = genres
    #
    #     driver.quit()
    #
    #     return movie_data

    def getpg(self):
        # 获取电影的id
        movie_id = re.search(r'tt(\d+)', self.movie_url).group(1)

        # genre & plot
        ia = IMDb()
        movie = ia.get_movie(movie_id)
        movie_plot = movie.get('plot')
        movie_genres = movie.get('genres')
        movie_name = movie.get('title','No found')
        full_plot = ''.join(movie_plot)

        dicts = {'ID': movie_id, 'Plot': full_plot, 'Genres': movie_genres,'Name': movie_name}

        return dicts



if __name__ == '__main__':
    # film_url = GenreFilmURL()
    # film_urls = film_url.getfilmurl()
    #
    #
    # with open("../dict/film_url.json", "w") as json_file:
    #     json.dump(film_urls, json_file, indent=4)

    with open('../dict/film_url.json', 'r') as file: # test
        film_urls = json.load(file)

    start_time = time.time()
    with open('../dict/film_infos.json', 'a') as json_file:
        # 判断文件是否为空，如果为空则写入开始的 "[" （JSON 数组开始）
        json_file.seek(0, 2)  # 文件指针移动到文件末尾
        if json_file.tell() == 0:
            json_file.write('[\n')  # 如果文件为空，写入开始的 '['

        for idx, (film, url) in tqdm.tqdm(enumerate(list(film_urls.items())[:], start=0), desc='In progress of retrieving data:'): # 从a+b开始
            try:
                f2j = Film2Json(url)
                movie_data = f2j.getinfo()

                # 每100条数据刷新一次文件
                json.dump(movie_data, json_file, indent=4)
                json_file.write(',\n' if idx < len(film_urls) - 1 else '\n')  # 不是最后一条时添加逗号

                time.sleep(0.1) # 使用太快容易报错
            except Exception:
                continue
            # 每100个对象保存一次
            if idx % 100 == 0:
                json_file.flush()

        # 文件结束时关闭 JSON 数组（加上 ']'）
        json_file.write(']')

    end_time = time.time()
    print(
        f'Used {(end_time - start_time) // 3600} hours {((end_time - start_time) % 3600) // 60} mins {(end_time - start_time) % 60} sec')


