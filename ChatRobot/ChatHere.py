from question_parser import *
from AnswerPart import *

class AnswerRobort:
    def __init__(self):
        self.classifier = QuestionClassify()
        self.trans = Question_trans()
        self.answer = Answer()

    def chat_main(self, question):
        # 切分问题
        res_classify = self.classifier.classify(question)

        if not res_classify:
            return "这个超出能力范畴了噢，请尝试其他问题。"

        # 问题 -> sql
        res_sql = self.trans.parser_main(res_classify)
        print(res_sql)

        # 查询答案
        final_answers = self.answer.search_main(res_sql)

        if not final_answers:
            return "抱歉，还没有收录这些信息呢。"
        else:
            return final_answers



if __name__ == '__main__':
    robot = AnswerRobort()
    question = input('请问您想问什么呢?（退出请直接输入"退出"）:\n')
    while question != '退出':
        answer = robot.chat_main(question)
        print('Ron:',answer)
        question = input('请问您想问什么呢?（退出请直接输入"退出"）')
    print('欢迎下次咨询！')