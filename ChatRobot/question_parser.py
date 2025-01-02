import ahocorasick


class QuestionClassify:
    def __init__(self):
        # 给出实体词 方便进行关系匹配 应该返回 what，relati，
        self.companies_path = '../dict/companies.txt'
        self.countries_path = '../dict/countries.txt'
        self.genres_path = '../dict/genres.txt'
        self.movies_path = '../dict/movies.txt'
        self.persons_path = '../dict/persons.txt'
        # 提取实体词并且组合
        self.companies = [i.strip() for i in open(self.companies_path, 'r', encoding='utf-8') if i.strip()]
        self.countries = [i.strip() for i in open(self.countries_path, 'r', encoding='utf-8') if i.strip()]
        self.genres = [i.strip() for i in open(self.genres_path, 'r', encoding='utf-8') if i.strip()]
        self.movies = [i.strip() for i in open(self.movies_path, 'r', encoding='utf-8') if i.strip()]
        self.persons = [i.strip() for i in open(self.persons_path, 'r', encoding='utf-8') if i.strip()]
        self.words = set(self.companies + self.countries + self.genres + self.movies + self.persons)
        # 构建查找工具
        self.region_tree = self.build_actree(list(self.words))
        # 构建词典 里面包含了每个词的种类
        self.type_dict = self.build_type_dict()
        # 问句疑问词 - 用来确定关系
        self.comp_qw = ['公司', '制片', '出品', '发行商', '影业', '影视', '发行']

        # 这种包含关系我们可以通过严格限定+通用限定来写
        # 询问参与时是把所有人都包括了,因此type应该包含这下面四种关系
        self.person_qw = ['参与', '谁参与', '贡献']
        self.dir_qw = ['导演', '执导'] + self.person_qw
        self.write_qw = ['编剧', '剧本'] + self.person_qw
        # 询问演员时候,应该包含下面所有，type有下面两种关系
        self.act_qw = ['出演', '参演', '演的', '演员'] + self.person_qw
        self.star_qw = ['主演', '主要演员'] + self.act_qw  # 词列表应该更长
        self.country_qw = ['拍摄国家', '在哪', '拍摄地点', '制作国', '外景地', '拍摄地', '拍摄区域','哪里','取景']
        self.genre_qw = ['种类', '风格', '题材', '属于', '类型', '味道', '分类', '特色', '类别', '表现形式']

        # attributes = ['Released date','Language','Also known as','Runtime','Plot','Name','Rating']
        self.release_qw = ['时候', '时间', '上映', '日期', '何时', '放映', '公开', '发布']
        self.language_qw = ['语言', '哪国话', '什么话']
        self.akas_qw = ['别名', '叫啥', '名字', '名称']
        self.runtime_qw = ['多长', '多少', '多久', '时长', '长度']
        self.plot_qw = ['讲什么', '情节', '故事', '介绍', '简介', '梗概', '概括', '简单说', '剧情']
        self.rating_qw = ['评分', '口碑', '评价', '好看吗']

    def classify(self, question):
        data = {}
        movie_dict = self.check_movie(question)  # 返回的是 quesiton_entities {word1:[type1, type2,...],...}

        if not movie_dict:
            return {}

        data['args'] = movie_dict  # {'args':{word:[type1, type2,...]}}

        # 确定了实体，接下来就是确定关系了
        types = []
        for type_ in movie_dict.values():
            types += type_  # 把所有的type都列出来

        question_types = []

        # 问题都会以电影为引子因此一般将Movie用作评价就行 , 如果连Moive都没有出现，那么就会涉及到比较高级的语句类似统计信息现在做不出来 movie和其他是双向的关系 //
        # 以 主体 - (关系) -> 确定索引结果  || 如果出现多重主题 like 主体1persons 主体2 movies -(关系) -> 确认结果 person和关系组合 还是 movie和关系组合? 我这种单类方法不可行
        # 不然多于一条关系的连接都要重新构建关系

        # 以电影为主体 // 一个关系一条边 7个关系7条边
        if self.check_words(self.comp_qw, question) and ('Movie' in types):
            # 制片方和电影都出现,可以确定问题问的时电影的出版方
            question_type = 'movie_publishing'
            question_types.append(question_type)

        if self.check_words(self.dir_qw, question) and ('Movie' in types):
            # 导演
            question_type = 'movie_director'
            question_types.append(question_type)

        if self.check_words(self.star_qw, question) and ('Movie' in types):
            # 主演
            question_type = 'movie_star'
            question_types.append(question_type)

        if self.check_words(self.act_qw, question) and ('Movie' in types):
            # 出演
            question_type = 'movie_actor'
            question_types.append(question_type)

        if self.check_words(self.write_qw, question) and ('Movie' in types):
            # 编剧
            question_type = 'movie_writer'
            question_types.append(question_type)

        if self.check_words(self.country_qw, question) and ('Movie' in types):
            # 电影和国家同时出现,  问题有查询电影和国家的关系
            question_type = 'movie_country'
            question_types.append(question_type)

        if self.check_words(self.genre_qw, question) and ('Movie' in types):
            question_type = 'movie_genre'
            question_types.append(question_type)

        # 根据其他部分查询Movie
        # 根据人
        if self.check_words(self.dir_qw, question) and ('Person' in types):
            question_type = 'director_movie'
            question_types.append(question_type)

        if self.check_words(self.write_qw, question) and ('Person' in types):
            question_type = 'writer_movie'
            question_types.append(question_type)

        if self.check_words(self.star_qw, question) and ('Person' in types):
            question_type = 'star_movie'
            question_types.append(question_type)

        if self.check_words(self.act_qw, question) and ('Person' in types):
            question_type = 'actor_movie'
            question_types.append(question_type)

        # 根据公司
        if self.check_words(self.comp_qw, question) and ('Company' in types):
            question_type = 'company_movie'
            question_types.append(question_type)

        # 根据国家
        if self.check_words(self.country_qw, question) and ('Country' in types):
            question_type = 'country_movie'
            question_types.append(question_type)

        # 根据题材
        if self.check_words(self.genre_qw, question) and ('Genre' in types):
            question_type = 'genre_movie'
            question_types.append(question_type)

        # 如果问属性相关的问题
        """
        self.release_qw = ['时候','时间', '上映', '日期', '何时', '放映', '公开','发布']
        self.language_qw = ['语言','哪国话','什么话']
        self.akas_qw = ['别名','叫啥','名字','名称']
        self.runtime_wq = ['多长','多少','多久','时长','长度']
        self.plot_qw = ['讲什么','情节','故事','介绍','简介','梗概','概括','简单说','剧情']
        self.rating_qw = ['评分','口碑','评价','好看吗']
        """
        if self.check_words(self.release_qw, question) and ('Movie' in types):
            question_type = 'movie_release'
            question_types.append(question_type)

        if self.check_words(self.language_qw, question) and ('Movie' in types):
            question_type = 'movie_language'
            question_types.append(question_type)

        if self.check_words(self.akas_qw, question) and ('Movie' in types):
            question_type = 'movie_akas'
            question_types.append(question_type)

        if self.check_words(self.runtime_qw, question) and ('Movie' in types):
            question_type = 'movie_runtime'
            question_types.append(question_type)

        if self.check_words(self.plot_qw, question) and ('Movie' in types):
            question_type = 'movie_plot'
            question_types.append(question_type)

        if self.check_words(self.rating_qw, question) and ('Movie' in types):
            question_type = 'movie_rating'
            question_types.append(question_type)

        if not question_types:
            print('抱歉，我现在还无法回答这类问题.')
            return

        data['question_types'] = question_types

        return data

    def build_type_dict(self):
        dict_ = dict()
        for word in self.words:
            dict_[word] = []
            if word in self.companies:
                dict_[word].append('Company')
            if word in self.countries:
                dict_[word].append('Country')
            if word in self.genres:
                dict_[word].append('Genre')
            if word in self.persons:
                dict_[word].append('Person')
            if word in self.movies:
                dict_[word].append('Movie')

        return dict_  # {word1:[type1, type2,...],...} 返回所有及对应的type，不在读取时读入是因为存在多种type的word

    def build_actree(self, wordList):
        actree = ahocorasick.Automaton()
        for index, word in enumerate(wordList):
            actree.add_word(word, (index, word))
        actree.make_automaton()
        return actree

    def check_movie(self, question):
        question_entities = []
        for i in self.region_tree.iter(question):
            question_entities.append(i[1][1])

        # 精确化词语  ###### 论证的地方
        stop_words = []
        for wd1 in question_entities:
            for wd2 in question_entities:
                if wd1 in wd2 and wd1 != wd2:  # 1.电影名重叠 // 2.如果问句关键词顶替电影名
                    # wd1 比 wd2 短
                    if (wd1 in self.movies) and (wd2 not in self.movies):
                        continue
                    stop_words.append(wd1)

        final_words = [i for i in question_entities if i not in stop_words]

        final_dict = {i: self.type_dict.get(i) for i in final_words}

        return final_dict

    def check_words(self, wordList, question):
        for word in wordList:
            if word in question:
                return True
        return False


# 接受从问题识别传来的具体分类 {'args': {word:[type1, type2,...], 'question_type':[type1, type2]}
class Question_trans:
    def build_entitydict(self, args):
        # 为了确定图谱中的点, 之前知识确定了实体和他的许许多多类型但是现在要确定这些类型中的具体点了
        entity_dict = {}
        for arg, types in args.items():
            for type_ in types:
                if type_ not in entity_dict:
                    entity_dict[type_] = [arg]
                else:
                    entity_dict[type_].append(arg)
        return entity_dict  # 其实就是点set

    def parser_main(self, data):
        args = data['args']
        entity_dict = self.build_entitydict(args)
        question_types = data['question_types']
        sqls = []  # 确定具体的查询语句
        for question_type in question_types:  # 可能有多种 type / 一种type只确定一种关系
            sql_ = {}
            sql_['question_type'] = question_type

            # 实体关系 20种问法

            if question_type == 'movie_pubilshing':  # 问句中必然包含 Movie
                sql = self.sql_trans(question_type, entity_dict.get('Movie'))

            # person要拆开为4种
            # elif question_type == 'movie_person':
            #     sql = self.sql_trans(question_type, entity_dict.get('Movie'))
            elif question_type == 'movie_director':
                sql = self.sql_trans(question_type, entity_dict.get('Movie'))
            elif question_type == 'movie_star':
                sql = self.sql_trans(question_type, entity_dict.get('Movie'))
            elif question_type == 'movie_actor':
                sql = self.sql_trans(question_type, entity_dict.get('Movie'))
            elif question_type == 'movie_writer':
                sql = self.sql_trans(question_type, entity_dict.get('Movie'))

            elif question_type == 'movie_country':
                sql = self.sql_trans(question_type, entity_dict.get('Movie'))
            elif question_type == 'movie_genre':
                sql = self.sql_trans(question_type, entity_dict.get('Movie'))

            # person要拆开为4种
            # elif question_type == 'person_movie':
            #     sql = self.sql_trans(question_type, entity_dict.get('Movie'))
            elif question_type == 'director_movie':
                sql = self.sql_trans(question_type, entity_dict.get('Person'))
            elif question_type == 'writer_movie':
                sql = self.sql_trans(question_type, entity_dict.get('Person'))
            elif question_type == 'star_movie':
                sql = self.sql_trans(question_type, entity_dict.get('Person'))
            elif question_type == 'actor_movie':
                sql = self.sql_trans(question_type, entity_dict.get('Person'))

            elif question_type == 'country_movie':
                sql = self.sql_trans(question_type, entity_dict.get('Country'))
            elif question_type == 'genre_movie':
                sql = self.sql_trans(question_type, entity_dict.get('Genre'))
            elif question_type == 'company_movie':
                sql = self.sql_trans(question_type, entity_dict.get('Company'))

            # movie属性
            elif question_type == 'movie_release':
                sql = self.sql_trans(question_type, entity_dict.get('Movie'))
            elif question_type == 'movie_language':
                sql = self.sql_trans(question_type, entity_dict.get('Movie'))
            elif question_type == 'movie_akas':
                sql = self.sql_trans(question_type, entity_dict.get('Movie'))
            elif question_type == 'movie_runtime':
                sql = self.sql_trans(question_type, entity_dict.get('Movie'))
            elif question_type == 'movie_plot':
                sql = self.sql_trans(question_type, entity_dict.get('Movie'))
            elif question_type == 'movie_rating':
                sql = self.sql_trans(question_type, entity_dict.get('Movie'))

            if sql:
                sql_['sql'] = sql  # {'question_type':question_type ,'sql': 'MATCH...'}

                sqls.append(sql_)  # for one entity [{'question_type':question_type ,'sql': 'MATCH...'}]

        return sqls

    def sql_trans(self, question_type, entity):  # entity只有一个
        if not entity:
            return None

        if len(entity) == 1:
            entity = entity[0]

        if question_type == 'movie_release':
            sql = "MATCH (m:Movie) where m.name = %r return m.name, m.Release_date" % entity
        elif question_type == 'movie_language':
            sql = "MATCH (m:Movie) where m.name = %r return m.name, m.Language" % entity
        elif question_type == 'movie_akas':
            sql = "MATCH (m:Movie) where m.name = %r return m.name, m.Also_Know_as" % entity
        elif question_type == 'movie_runtime':
            sql = "MATCH (m:Movie) where m.name = %r return m.name, m.Runtime" % entity
        elif question_type == 'movie_plot':
            sql = "MATCH (m:Movie) where m.name = %r return m.name, m.Plot" % entity
        elif question_type == 'movie_rating':
            sql = "MATCH (m:Movie) where m.name = %r return m.name, m.Rating" % entity

        # 实体部分 'movie_director','movie_star','movie_actor','movie_writer','movie_country','movie_genre' // Movie 出现
        elif question_type == 'movie_pubilshing':
            sql = "MATCH (m:Movie)-[r:published_by]->(n:Company) where m.name = %r return m.name, r.name, n.name" % entity
        elif question_type == 'movie_director':
            sql = "MATCH (m:Person)-[r:direct]->(n:Movie) where n.name = %r return m.name, r.name, n.name" % entity
        elif question_type == 'movie_star':
            sql = "MATCH (m:Person)-[r:star]->(n:Movie) where n.name = %r return m.name, r.name, n.name" % entity
        elif question_type == 'movie_writer':
            sql = "MATCH (m:Person)-[r:write]->(n:Movie) where n.name = %r return m.name, r.name, n.name" % entity
        elif question_type == 'movie_actor':
            sql = "MATCH (m:Person)-[r:act]->(n:Movie) where n.name = %r return m.name, r.name, n.name" % entity

        elif question_type == 'movie_genre':
            sql = "MATCH (m:Movie)-[r:belongs_to]->(n:Genre) where m.name = %r return m.name, r.name, n.name" % entity
        elif question_type == 'movie_country':
            sql = "MATCH (m:Movie)-[r:filmed_in]->(n:Country) where m.name = %r return m.name, r.name, n.name" % entity

        elif question_type == 'director_movie':
            sql = "MATCH (m:Person)-[r:direct]->(n:Movie) where m.name = %r return m.name, r.name, n.name LIMIT 25" % entity
        elif question_type == 'writer_movie':
            sql = "MATCH (m:Person)-[r:write]->(n:Movie) where m.name = %r return m.name, r.name, n.name LIMIT 25" % entity
        elif question_type == 'star_movie':
            sql = "MATCH (m:Person)-[r:star]->(n:Movie) where m.name = %r return m.name, r.name, n.name LIMIT 25" % entity
        elif question_type == 'actor_movie':
            sql = "MATCH (m:Person)-[r:act]->(n:Movie) where m.name = %r return m.name, r.name, n.name LIMIT 25" % entity

        elif question_type == 'country_movie':
            sql = "MATCH (m:Movie)-[r:filmed_in]->(n:Country) where n.name = %r return m.name, r.name, n.name LIMIT 25" % entity
        elif question_type == 'genre_movie':
            sql = "MATCH (m:Movie)-[r:belongs_to]->(n:Genre) where n.name = %r return m.name, r.name, n.name LIMIT 25" % entity
        elif question_type == 'company_movie':
            sql = "MATCH (m:Movie)-[r:published_by]->(n:Company) where n.name = %r return m.name, r.name, n.name LIMIT 25" % entity

        return sql

