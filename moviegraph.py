import json
from py2neo import Graph, Node


# 提取实体 导出实体 确定关系
class MovieGraph:
    def __init__(self):
        self.data_path = './dict/film_infos.json'
        self.g = Graph("neo4j://localhost:7687", auth=("neo4j", "12345678"))

    def read_node(self):
        # 读取节点
        movies = []  # 电影名称
        persons = []  # 人数
        genres = []  # 题材数
        companies = []  # 公司数
        countries = []  # 国家数

        # 电影信息
        film_infos = []

        # 节点实体关系
        rel_direct = []
        rel_write = []
        rel_star = []
        rel_act = []
        rel_genre = []
        rel_country = []
        rel_company = []

        with open(self.data_path, 'r') as f:
            data = f.read()
            data_json = json.loads(data)

        count = 0
        for data in data_json:
            # 对于每一部电影
            # print(data)
            film_dict = {}  # 中心点
            count += 1
            # print(count)
            #  提取 - 读入

            film_id = data['ID']  # id才是电影的唯一标识
            film_dict['ID'] = film_id

            # 添加电影的属性  ? 这些是否多此一举 看下面怎么说
            # 添加属性，去除掉data里面的实体
            # 就剩下上映时间\语言\别名\时长\情节\ID\评分
            attributes = ['Released date', 'Language', 'Also known as', 'Runtime', 'Plot', 'Name', 'Rating']
            for attr in attributes:
                film_dict[attr] = ''

            # 开始添加内容  - 为data里面的所有部分找个归宿
            if 'Directors' in data:
                persons += data['Directors']  # 实体添加
                for director in data['Directors']:
                    rel_direct.append((director, film_id))  # (电影id-导演) pair

            if 'Writers' in data:
                persons += data['Writers']
                for writer in data['Writers']:
                    rel_write.append((writer, film_id))

            if 'Stars' in data:
                persons += data['Stars']
                for star in data['Stars']:
                    rel_star.append((star, film_id))

            if 'Actors' in data:
                persons += data['Actors']
                for actor in data['Actors']:
                    rel_act.append((actor, film_id))

            if 'Rating' in data:
                film_dict['Rating'] = data['Rating']

            if 'Plot' in data:
                film_dict['Plot'] = data['Plot']

            if 'Genres' in data:
                genres += data['Genres']
                for genre in data['Genres']:
                    rel_genre.append((film_id, genre))

            if 'Released date' in data:
                film_dict['Released date'] = data['Released date']

            if 'Countries of origin' in data:
                countries += data['Countries of origin']
                for country in data['Countries of origin']:
                    rel_country.append((film_id, country))

            if 'Language' in data:
                film_dict['Language'] = data['Language']

            if 'Also known as' in data:
                film_dict['Also known as'] = data['Also known as']

            if 'Production companies' in data:
                companies += data['Production companies']
                for company in data['Production companies']:
                    rel_company.append((film_id, company))

            if 'Runtime' in data:
                film_dict['Runtime'] = data['Runtime']

            if 'Name' in data:
                film_dict['Name'] = data['Name']
                movies.append(data['Name'])

            film_infos.append(film_dict)  # 精简化的film 适合做entity的film信息
        return movies, set(persons), set(genres), set(companies), set(
            countries), film_infos, rel_direct, rel_write, rel_star, rel_act, rel_genre, rel_country, rel_company

    # 下面三类都是创建节点
    def create_graphnodes(self):
        movies, persons, genres, companies, countries, film_infos, *_ = self.read_node()
        self.create_movie_nodes(film_infos)  # 主要节点
        self.create_node('Person', persons)
        self.create_node('Genre', genres)
        self.create_node('Company', companies)
        self.create_node('Country', countries)
        print(
            f'movies: {len(movies)}, persons: {len(persons)}, genres: {len(genres)}, companies: {len(companies)}, countries: {len(countries)}')
        return

    def create_movie_nodes(self, film_infos):
        count = 0
        for film_info in film_infos:
            # 将主要节点的属性全部读入
            # attributes = ['Released date1','Language1','Also known as1','Runtime1','Plot','Name1','Rating1']
            node = Node('Movie', Released_date=film_info['Released date'], name=film_info['Name'],
                        Also_Know_as=film_info['Also known as'], Runtime=film_info['Runtime'],
                        Rating=film_info['Rating'], Language=film_info['Language'], Plot=film_info['Plot'],
                        ID=film_info['ID'])
            self.g.create(node)
            count += 1
        return

    def create_node(self, label, items):
        # 进来的都是list
        count = 0
        for item in items:
            node = Node(label, name=item)
            self.g.create(node)
            count += 1
        return

    # 创建关系
    def create_graphrels(self):
        _, _, _, _, _, _, rel_direct, rel_write, rel_star, rel_act, rel_genre, rel_country, rel_company = self.read_node()
        self.create_relationship('Person', 'Movie', rel_direct, 'direct', '导演')
        self.create_relationship('Person', 'Movie', rel_write, 'write', '编剧')
        self.create_relationship('Person', 'Movie', rel_star, 'star', '主演')
        self.create_relationship('Person', 'Movie', rel_act, 'act', '出演')
        self.create_relationship('Movie', 'Genre', rel_genre, 'belongs_to', '属于')
        self.create_relationship('Movie', 'Country', rel_country, 'filmed_in', '拍摄于')
        self.create_relationship('Movie', 'Company', rel_company, 'published_by', '出版')  # 指向关系一定要清楚
        return

    def create_relationship(self, start, end, edges, rel_type, rel_name):  # start, end是label 具体的在里面的 p q
        count = 0
        for edge in edges:  # 可能存在多重关系不用去重
            # edge = edge.split('##')
            p = edge[0]
            q = edge[1]
            # 通过name / 通过属性定位的都是查询 |
            # 都要满足前指向后 get 且后为film.id
            if start != 'Movie':
                query = "MATCH (p:%s), (q:%s) WHERE p.name = %r AND q.ID = %r CREATE (p)-[rel:%s {name:'%s'}]->(q)" % (
                start, end, p, q, rel_type, rel_name)
            else:
                query = "MATCH (p:%s), (q:%s) WHERE p.ID = %r AND q.name = %r CREATE (p)-[rel:%s {name:'%s'}]->(q)" % (
                start, end, p, q, rel_type, rel_name)

            try:
                # print(query)
                self.g.run(query)
                count += 1
            except Exception as e:
                print(e)
        return

    # 导出数据
    def export_data(self):
        movies, persons, genres, companies, countries, *_ = self.read_node()
        self.write_to_file('./dict/movies.txt', movies)
        self.write_to_file('./dict/persons.txt', persons)
        self.write_to_file('./dict/genres.txt', genres)
        self.write_to_file('./dict/companies.txt', companies)
        self.write_to_file('./dict/countries.txt', countries)

        return

    def write_to_file(self,filename, data):
        with open(filename, 'w+', encoding='utf-8') as f:
            f.write('\n'.join(list(data)))
        return

if __name__ == '__main__':
    ia = MovieGraph()
    # print('Node in')
    # ia.create_graphnodes()
    # print('Edge in')
    # ia.create_graphrels()
    ia.export_data()