# 导包部分
from flask import Flask # 导入 Flask 类：创建程序对象 app
from flask import url_for # 导入 url_for() 函数：生成 URL
from flask import render_template # 导入 render_template() 函数：渲染模板
from markupsafe import escape # 导入 escape() 函数：对 HTML 标签进行转义
from faker import Faker # 导入 Faker 类：生成假数据
import random # 导入 random 模块：生成随机数
from flask_sqlalchemy import SQLAlchemy # 导入 SQLAlchemy 类：操作数据库
import os # 导入 os 模块：获取当前目录
import click # 导入 click 模块：命令行工具



# 从 flask 包导入 Flask 类，通过实例化这个类，创建一个程序对象 app
app = Flask(__name__)

# 配置部分
prefix = 'sqlite:///' # 数据库前缀
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db')# 配置数据库文件路径
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭对模型修改的监控

# 数据库实例
db = SQLAlchemy(app)

# 创建数据库模型
class User(db.Model):  # 表名将会是 user（自动生成，小写处理）
    id = db.Column(db.Integer, primary_key=True)  # 主键
    name = db.Column(db.String(20))  # 名字


class Movie(db.Model):  # 表名将会是 movie
    id = db.Column(db.Integer, primary_key=True)  # 主键
    title = db.Column(db.String(60))  # 电影标题
    year = db.Column(db.String(4))  # 电影年份


# 命令行工具部分
# 自定义命令 initdb
@app.cli.command()  # 注册为命令，可以传入 name 参数来自定义命令
@click.option('--drop', is_flag=True, help='Create after drop.')  # 设置选项
def initdb(drop):
    """Initialize the database."""
    if drop:  # 判断是否输入了选项
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')  # 输出提示信息

@app.cli.command()
def forge():
    """Generate fake data."""
    db.create_all()

    # 全局的两个变量移动到这个函数内
    name = 'Tuoyuan'

    # 创建 Faker 对象，用于生成假数据
    fake = Faker()

    # 生成电影列表
    movies = []
    for _ in range(20):
        movie = {
            # title 属性使用 fake.sentence() 方法生成假数据, 参数 nb_words=3 表示生成三个单词的假数据,rstrip('.') 表示去掉句号
            "title": fake.sentence(nb_words=3).rstrip('.'),
            "year": random.randint(1950, 2023)  # 假设电影年份在1950到2023之间
        }
        movies.append(movie)

    user = User(name=name)
    db.session.add(user)
    for m in movies:
        movie = Movie(title=m['title'], year=m['year'])
        db.session.add(movie)

    db.session.commit()
    click.echo('Done.')

# 数据部分
name = 'Tuoyuan'

# 创建 Faker 对象，用于生成假数据
fake = Faker()

# 生成电影列表
movies_list = []
for _ in range(20):
    movie = {
        # title 属性使用 fake.sentence() 方法生成假数据, 参数 nb_words=3 表示生成三个单词的假数据,rstrip('.') 表示去掉句号
        "title": fake.sentence(nb_words=3).rstrip('.'),
        "year": random.randint(1950, 2023)  # 假设电影年份在1950到2023之间
    }
    movies_list.append(movie)

# 路由部分
@app.route('/')
def index():
    user = User.query.first()  # 读取用户记录
    movies = Movie.query.all()  # 读取所有电影记录
    return render_template('index.html', user=user, movies=movies)

@app.route('/2')
def index2():
    # 渲染模板并传递参数：name 和 movies
    return render_template('index.html', name=name, movies=movies_list)

@app.route('/1')
def hello():
    # 返回一个字符串，包含HTML的h1标签和img标签
    return '<h1>Hello Totoro!</h1><img src="http://helloflask.com/totoro.gif">'

@app.route('/index')
@app.route('/home')
def hello2():
    # 返回欢迎信息
    return 'Welcome to My Watchlist!'

@app.route('/user/<name>')
def user_page(name):
    # 将name进行转义，避免特殊字符引起的错误
    name = escape(name)
    # 返回格式化字符串，将转义后的name插入到字符串中
    return f'User: {name}'

@app.route('/test')
def test_url_for():
    # 下面是一些调用示例（请访问 http://localhost:5000/test 后在命令行窗口查看输出的 URL）：
    print(url_for('hello'))  # 生成 hello 视图函数对应的 URL，将会输出：/
    # 注意下面两个调用是如何生成包含 URL 变量的 URL 的
    print(url_for('user_page', name='greyli'))  # 输出：/user/greyli
    print(url_for('user_page', name='peter'))  # 输出：/user/peter
    print(url_for('test_url_for'))  # 输出：/test
    # 下面这个调用传入了多余的关键字参数，它们会被作为查询字符串附加到 URL 后面。
    print(url_for('test_url_for', num=2))  # 输出：/test?num=2
    return 'Test page'