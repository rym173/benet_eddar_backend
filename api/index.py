import json
from flask import Flask, request, jsonify
from supabase import create_client, Client
from flask_cors import CORS 

app = Flask(__name__)
CORS(app)

url = "https://hljaiwqvdchahyfsvpdh.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhsamFpd3F2ZGNoYWh5ZnN2cGRoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MDI0NjM1MzUsImV4cCI6MjAxODAzOTUzNX0.3CioZ51QSifNdWya5a_h4jhOxx_Qp4f79GhsuNNTCl0"

supabase: Client = create_client(url, key)

@app.route('/users.signup', methods=['POST', 'GET'])
def api_users_signup():
    try:

        Email = request.form.get('email')
        Name = request.form.get('name')
        Password = request.form.get('password')
        Location = request.form.get('location')
        Phone = request.form.get('phone')
        error =False

        
        if (not Email) or (len(Email) < 5):
            error = 'Email needs to be valid'

        if (not Name) or (len(Name) == 0):
            error = 'Name cannot be empty'

        if (not error) and ((not Password) or (len(Password) < 6)):
            error = 'Provide a password'

        if (not error):
            response = supabase.table('User').select("*").ilike('Email', Email).execute()
            if len(response.data) > 0:
                error = 'User already exists'

        if (not error):
            response = supabase.table('User').insert({
                "Email": Email,
                "Password": Password,
                "Name": Name,
                "Location": Location,
                "Phone": Phone
            }).execute()
            print(str(response.data))
            if len(response.data) == 0:
                error = 'Error creating the user'

        if error:
            return jsonify({'status': 500, 'message': error})

        return jsonify({'status': 200, 'message': '', 'data': response.data[0]})

    except Exception as e:
        return jsonify({'status': 500, 'message': f'Internal Server Error: {str(e)}'})


@app.route('/users.login', methods=['POST'])
def api_users_login():
        email = request.form.get('email')
        password = request.form.get('password')

        error = False

        if (not email) or (len(email) < 5):
            error = 'Email needs to be valid'

        if (not error) and ((not password) or (len(password) < 5)):
            error = 'Provide a password'

        if (not error):
            response = supabase.table('User').select("*").ilike('Email', email).eq('Password', password).execute()
            if len(response.data) > 0:
                return jsonify({'status': 200, 'message': '', 'data': response.data[0]})

        if not error:
            error = 'Invalid Email or password'

        if error:
            return json.dumps({'status': 500, 'message': error})
        return json.dumps({'status': 500, 'message': 'Invalid email or password'})
    
@app.route('/')
def about():
    return 'Welcome to benet eddar'



if __name__ == "__main__":
    app.run(debug=True)
