from flask import Flask , render_template , flash , session, logging,request, url_for,redirect
from data import Articles
from flask_mysqldb import MySQL
from wtforms import Form,StringField,TextAreaField,PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps
app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'ankitp'
app.config['MYSQL_DB'] = 'myflaskapp' 
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap
@app.route('/')
def index():
    return render_template('home.html')

@app.route('/about')
def home():
    return render_template('about.html')

@app.route('/articles')
def articles():

    cur = mysql.connection.cursor() 
    result = cur.execute("SELECT * FROM article")
    articles  = cur.fetchall()
    if result > 0 :
        return render_template('articles.html', articles=articles)
    else:
        msg = 'no found result'
        return render_template('articles.html', msg=msg)

@app.route('/article/<string:id>/')
def article(id):
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM article WHERE id =%s", [id])
    article  = cur.fetchone()


    return render_template('article.html' ,article = article)

@app.route('/edit_article/<string:id>/' , methods=['GET','POST'])
# @is_logged_in
def edit_article(id):
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM article WHERE id =%s", [id])
    article  = cur.fetchone()
    form = ArticleForm(request.form)
    form.title.data = article['title']
    form.body.data = article['body']
    print request.method
    if request.method == 'POST' and form.validate():
        title = request.form['title']
        body = request.form['body']
        cur = mysql.connection.cursor() 
        print title ,body
        cur.execute("UPDATE article SET title=%s , body=%s , author=%s WHERE id=%s ",(title, body, 'apexankitpatidar' , id))
        cur.connection.commit()
        cur.close()
        flash('article UPDATE', 'success')
        return redirect(url_for('dashboard'))
    return render_template('edit_article.html', form=form)

@app.route('/delete_article/<string:id>/' , methods=['GET','POST'])
# @is_logged_in
def delete_article(id):
    cur = mysql.connection.cursor()
    result = cur.execute("DELETE  FROM article WHERE id =%s", [id])
    cur.connection.commit()
    cur.close()
    flash('article DELETE', 'success')
    return redirect(url_for('dashboard'))



class RegistrationForm(Form):
    username     = StringField('Username', [validators.Length(min=4, max=25)])
    email        = StringField('Email Address', [validators.Length(min=6, max=35)])
    password    = PasswordField('password', [validators.DataRequired(),
                                         validators.EqualTo('confirm', message='not match')])
    name        = StringField('Email Address', [validators.Length(min=6, max=35)])
    confirm = PasswordField('confirm password')

class ArticleForm(Form):
    title     = StringField('title', [validators.Length(min=1, max=50)])
    body     = TextAreaField('body', [validators.Length(min=30)])


@app.route('/add_article', methods=['GET','POST'])
@is_logged_in
def add_article():
    form = ArticleForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data
        body = form.body.data
        cur = mysql.connection.cursor() 
        cur.execute("INSERT INTO article(title, body, author) VALUES(%s, %s, %s)",(title, body, 'apexankitpatidar'))
        cur.connection.commit()
        cur.close()
        flash('article created', 'success')
        return redirect(url_for('dashboard'))
    return render_template('add_article.html', form=form)

@app.route('/dashboard')
@is_logged_in
def dashboard():
    cur = mysql.connection.cursor() 
    result = cur.execute("SELECT * FROM article")
    articles  = cur.fetchall()
    if result > 0 :
        return render_template('dashboard.html', articles=articles)
    else:
        msg = 'no found result'
        return render_template('dashboard.html', msg=msg)

@app.route('/logout')
def logout():
    session.clear()
    flash('you are now logged out', 'success')
    return redirect(url_for('login'))

@app.route('/login' ,methods=['GET','POST'])
def login():
    if request.method =='POST':
        username = request.form['username']
        password_condidate = request.form['password']
        cur = mysql.connection.cursor()
        result = cur.execute("SELECT * FROM users WHERE username=%s",[username])
        if result :
            data = cur.fetchone()
            password = data['password']
            if sha256_crypt.verify(password_condidate,password):
                session['logged_in'] = True
                session['username'] = username
                flash('you are now logged in ','success')
                return redirect(url_for('dashboard'))
            else:
                error = 'PASSWORD NOT MATCHED'
                app.logger.info('PASSWORD NOT MATCHED')
                return render_template('login.html' , error=error)
        else:
            error = 'NO USER'
            app.logger.info('NO USER')
            return render_template('login.html',error=error)
    return render_template('login.html')
@app.route('/register' ,methods=['GET','POST'])
def register():   
    form =  RegistrationForm(request.form)
    if request.method =='POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))
        cur = mysql.connection.cursor() 
        cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)", (name, email, username, password))
        mysql.connection.commit()
        cur.close()
        flash('You are now registered and can log in', 'success')
        # app.secret_key='secret123'
        return redirect(url_for('index'))
    return render_template('register.html',form=form)
if __name__ == '__main__':
    app.secret_key='secret123'
    app.run(debug=True)
