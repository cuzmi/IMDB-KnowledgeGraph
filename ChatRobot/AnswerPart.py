from py2neo import Graph


class Answer:
    def __init__(self):
        self.g = Graph("neo4j://localhost:7687", auth=("neo4j", "12345678"))
        self.num_limit = 5

    def search_main(self, sqls):  # 接收从it返回的sql_list
        final_answers = []
        # print(sqls)
        for sql_ in sqls:
            question_type = sql_['question_type']
            query = sql_['sql']

            answer = []
            # print(query, len(query))
            # for query in queries: # 多少条query 返回多少个list元素 // # 在这里sql一般不会出现两条，以防万一用列表记录下来
            res = self.g.run(query).data()
            answer += res
            # print(f'query语句为:{query}，查询到的res:{res},此时answer为:{answer},question_type为:{question_type}')
            final_answer = self.answer_(question_type, answer)
            if final_answer:
                final_answers.append(final_answer)

        return final_answers

    def answer_(self, question_type, answers):
        final_answer = []
        if not answers:
            return []

        # 组装答案 还是依照关系就行组装
        if question_type == 'movie_release':
            desc = [i['m.Released_date'] for i in answers]  # // [{A,B}{A,C}...]
            entity = answers[0]['m.name']
            final_answer = "电影 %r 的上映时间为 %s " % (entity, '、'.join(list(set(desc))[:self.num_limit]))

        if question_type == 'movie_langugae':
            desc = [i['m.Language'] for i in answers]  # // [{A,B}{A,C}...]
            entity = answers[0]['m.name']
            final_answer = "电影 %r 的语言有 %s " % (entity, '、'.join(list(set(desc))[:self.num_limit]))

        if question_type == 'movie_akas':
            desc = [i['m.Also_Know_as'] for i in answers]  # // [{A,B}{A,C}...]
            entity = answers[0]['m.name']
            final_answer = "电影 %r 的也被叫做 %s " % (entity, '、'.join(list(set(desc))[:self.num_limit]))

        if question_type == 'movie_runtime':
            desc = [i['m.Runtime'] for i in answers]  # // [{A,B}{A,C}...]
            entity = answers[0]['m.name']
            final_answer = "电影 %r 时长为 %s " % (entity, '、'.join(list(set(desc))[:self.num_limit]))

        if question_type == 'movie_plot':
            desc = [i['m.Plot'] for i in answers]  # // [{A,B}{A,C}...]
            entity = answers[0]['m.name']
            final_answer = "电影 %r 讲了 %s 的故事" % (entity, '、'.join(list(set(desc))[:self.num_limit]))

        if question_type == 'movie_rating':
            desc = [i['m.Rating'] for i in answers]  # // [{A,B}{A,C}...]
            entity = answers[0]['m.name']
            final_answer = "电影 %r 评分为 %s " % (entity, '、'.join(list(set(desc))[:self.num_limit]))

        if question_type == 'movie_director':
            desc = [i['m.name'] for i in answers]  # // [{A,B}{A,C}...]
            entity = answers[0]['n.name']
            final_answer = "电影 %r 的导演是 %s " % (entity, '、'.join(list(set(desc))[:self.num_limit]))

        if question_type == 'movie_pubilshing':
            desc = [i['n.name'] for i in answers]  # // [{A,B}{A,C}...]
            entity = answers[0]['m.name']
            final_answer = "电影 %r 由这些公司出品 %s " % (entity, '、'.join(list(set(desc))[:self.num_limit]))

        if question_type == 'movie_star':
            desc = [i['m.name'] for i in answers]  # // [{A,B}{A,C}...]
            entity = answers[0]['n.name']
            final_answer = "%r 主演了这部电影 %r " % ('、'.join(list(set(desc))[:self.num_limit], entity))

        if question_type == 'movie_writer':
            desc = [i['m.name'] for i in answers]  # // [{A,B}{A,C}...]
            entity = answers[0]['n.name']
            final_answer = "%r 写了了这部剧 %r " % ('、'.join(list(set(desc))[:self.num_limit], entity))

        if question_type == 'movie_actor':
            desc = [i['m.name'] for i in answers]  # // [{A,B}{A,C}...]
            entity = answers[0]['n.name']
            final_answer = "%r 出演了这部剧 %r " % ('、'.join(list(set(desc))[:self.num_limit], entity))

        if question_type == 'movie_genre':
            desc = [i['n.name'] for i in answers]  # // [{A,B}{A,C}...]
            entity = answers[0]['m.name']
            final_answer = "%r 是一部 %r 类型的电影 " % (entity, '、'.join(list(set(desc))[:self.num_limit]))

        if question_type == 'movie_country':
            desc = [i['n.name'] for i in answers]  # // [{A,B}{A,C}...]
            entity = answers[0]['m.name']
            final_answer = "电影 %r 由 %r 联合制作 " % (entity, '、'.join(list(set(desc))[:self.num_limit]))

        if question_type == 'director_movie':
            desc = [i['n.name'] for i in answers]  # // [{A,B}{A,C}...]
            entity = answers[0]['m.name']
            final_answer = "%r 导演的电影有 %r " % (entity, '、'.join(list(set(desc))[:self.num_limit]))

        if question_type == 'star_movie':
            desc = [i['n.name'] for i in answers]  # // [{A,B}{A,C}...]
            entity = answers[0]['m.name']
            final_answer = "%r 主演的电影有 %r " % (entity, '、'.join(list(set(desc))[:self.num_limit]))

        if question_type == 'actor_movie':
            desc = [i['n.name'] for i in answers]  # // [{A,B}{A,C}...]
            entity = answers[0]['m.name']
            final_answer = "%r 出演的电影有 %r " % (entity, '、'.join(list(set(desc))[:self.num_limit]))

        if question_type == 'country_movie':
            desc = [i['m.name'] for i in answers]  # // [{A,B}{A,C}...]
            entity = answers[0]['n.name']
            final_answer = "%r 制片的电影有 %r " % (entity, '、'.join(list(set(desc))[:self.num_limit]))

        if question_type == 'genre_movie':
            desc = [i['m.name'] for i in answers]  # // [{A,B}{A,C}...]
            entity = answers[0]['n.name']
            final_answer = "%r 类型的电影有 %r " % (entity, '、'.join(list(set(desc))[:self.num_limit]))

        if question_type == 'company_movie':
            desc = [i['m.name'] for i in answers]  # // [{A,B}{A,C}...]
            entity = answers[0]['n.name']
            final_answer = "%r 出品电影有 %r " % (entity, '、'.join(list(set(desc))[:self.num_limit]))

        return final_answer
