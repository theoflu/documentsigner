from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import signer 
from Crypto.PublicKey import RSA
import base64
import datetime
import psycopg2

conn = psycopg2.connect(
    database="postgres",
    user="postgres",
    password="123",
    host="localhost",
    port="5432"
)
cur = conn.cursor()

# Kullanıcı için anahtar çifti oluşturma
def generate_keys():
    key = RSA.generate(2048)
    private_key = key.export_key()
    public_key = key.publickey().export_key()
    return private_key,public_key

app = Flask(__name__)

users = {}
#TODO 
@app.route('/register', methods=['POST'])
def register():
    username = request.json.get('username')
    password = request.json.get('password')
    
    if username in users:
        return jsonify({'error': 'User already exists'}), 400
    
    private_key, public_key = generate_keys()
    private_key_b64 = base64.b64encode(private_key).decode('utf-8')
    public_key_b64 = base64.b64encode(public_key).decode('utf-8')
    password_hash = generate_password_hash(password)
    users[username] = {'name':username,'password': password_hash,'priv_k':private_key_b64,'publ_k':public_key_b64,'date': datetime.datetime.now().strftime("%Y-%m-%d")}
    
    return jsonify({'message': 'User registered successfully',"user":users[username]}), 200

# @app.route('/login', methods=['POST'])
# def login():
#     username = request.json.get('username')
#     password = request.json.get('password')
    
#     user = users.get(username)
#     if not user or not check_password_hash(user['password'], password):
#         return jsonify({'error': 'Invalid credentials'}), 400
    
#     return jsonify({'message': 'Login successful'}), 200

@app.route('/signfile', methods=['POST'])
def login():
    try:
        username = request.json.get('username')
        filename = request.json.get('filename')

        cur.execute("select * from users where u_name =%s" , (username,))
        user = cur.fetchone()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        cur.execute("select * from keys where user_id =%s" , (user[0],))
        user1 = cur.fetchone()
        if not user1:
            private_key, public_key = generate_keys()
            private_key_b64 = base64.b64encode(private_key).decode('utf-8')
            public_key_b64 = base64.b64encode(public_key).decode('utf-8')
            cur.execute("INSERT INTO keys (private_key,public_key,user_id) values (%s,%s,%s)" , (private_key_b64,public_key_b64,int(user[0])))
            conn.commit()
        else:
            cur.execute("select * from keys where user_id =%s" , (user[0],))
            user1 = cur.fetchone()
            private_key=user1[1]
            public_key=user1[2]
        #    return jsonify({'message': 'successful'}), 200
        # return jsonify(user[4])
        signer.create_signed_pdf("C://Users//yusuf//OneDrive//Masaüstü//Document-Management//uploads//"+filename,"user_files/signed_output.pdf", "Dijital İmza",private_key, user)
        return jsonify({'message': 'success successful'}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
        
if __name__ == '__main__':
    app.run(debug=True)
