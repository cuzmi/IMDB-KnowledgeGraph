# IMDB-KnowledgeGraph

#### 如果想头开始，请删除dict里面的所有文件

Spider 为爬虫部分，负责从IMDB上爬取电影信息，同时生成格式化的json文件保存到dict中

(以下请保持neo4j console开启)
MovieGraph则是读取movie的json信息并存入neo4j，同时生成实体数据保存到dict中
ChatRobot是问答系统，直接运行ChatHere即可
