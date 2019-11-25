# Better Douban Movie (更好的豆瓣电影使用体验)

~~既然都在讨论豆瓣了，那么文档就用中文写吧。🙈~~

目标用户：

- 标记大量未上映作品，但是等到它们上映的时候自己不一定记得。（豆瓣对于不在中国大陆影院上映的作品没有上映提醒。豆瓣的「想看」列表不能按照作品上映时间排序。）
- 标记大量不在中国大陆上映的作品，有转去 IMDb 或其他国际服务的打算。

---

## 依赖

- requests
- beautifulsoup4
- fake-useragent

内置一个简单的 requests 封装，提供了基础的爬虫伪装能力。

---

## 功能

- 数据呈现
  - 高级排序
    - [x] 按照上映日期排序
  - 高级筛选
    - [ ] 按照 电影/剧集 类型筛选
    - [ ] 按照制片地区筛选
    - [ ] 按照上映地区筛选
    - [ ] 按照语言筛选
    - [ ] 按照豆瓣作品分类筛选
- 数据获取
  - [ ] 豆瓣星级
  - [ ] 作品评论
- 数据回写
  - [ ] 批量豆瓣星级管理
  - [ ] 导入到 IMDb

## 特性

- 数据获取
  - [ ] 多线程并发
  - [x] 从详情页面获取条目名称（列表页面对长名称有截断）
- 数据存储
  - [ ] 使用数据库存储到本地
  - [ ] 持续从本地数据库存取，不在内存中存储大量数据
- CLI 化？

## 使用方法

**使用前请先在 `sensitive_info.py` 中完善必要信息**  
**本脚本不存储任何敏感信息、不上传数据至任何私人服务器**

目前没有任何形式的用户界面，你可以选择在交互式环境中使用，如 IPython。
