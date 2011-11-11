from flask import *
import redis
import json
import pprint

pp = pprint.PrettyPrinter()
r = redis.StrictRedis(host='localhost', port=6379, db=0)
app = Flask(__name__)

def returnError(message):
    return json.dumps({
        'ECODE': -1,
        'message': message
    })

def returnOK(message='OK'):
    return json.dumps({
        'ECODE': 0,
        'message': message
    })


@app.route("/register", methods=['POST'])
def register():
    if not 'username' in request.form and not 'password' in request.form:
        return returnError('Username or password not specified')

    if r.hexists('users', request.form['username']):
        return returnError('User already exists')

    r.hset('users', request.form['username'], request.form['password'])

    return returnOK()

@app.route("/login", methods=['POST'])
def login():
    if 'username' in session:
        return returnError('Already logged in')

    if not 'username' in request.form and not 'password' in request.form:
        return returnError('Username or password not specified')

    password = r.hget('users', request.form['username'])

    if password == request.form['password']:
        session['username'] = request.form['username']
        return returnOK()
    else:
        return returnError('Invalid username or password')

@app.route("/logout", methods=['POST'])
def logout():
    if 'username' not in session:
        return returnError('Not logged in')
    session.pop('username', None)
    return returnOK()

@app.route("/list", methods=['GET'])
def list():
    if 'username' not in session:
        return returnError('Not logged in')
    
    return json.dumps( r.hkeys('notes_%s' % session['username']) )

@app.route("/note/<path:name>", methods=['GET'])
def note(name=None):
    if 'username' not in session:
        return returnError('Not logged in')
    
    return json.dumps( r.hget('notes_%s' % session['username'], name) )

@app.route("/save", methods=['POST'])
def save():
    if 'username' not in session:
        return returnError('Not logged in')
        
    if not 'name' in request.form:
        return returnError('Invalid path')

    if not 'note' in request.form:
        return returnError('No note body')

    r.hset('notes_%s' % session['username'], request.form['name'], request.form['note'])
    
    return returnOK()

@app.route("/hello")
def hello():
    i = r.incr('asdf')
    return "Hello World!!! %i" % i

if __name__ == "__main__":
    app.secret_key = '@L.O^M|*aw82YD9w>S5"22bs228Nc!'
    app.debug = True
    app.run(host='0.0.0.0')
