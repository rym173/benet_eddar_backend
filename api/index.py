from flask import Flask, request, jsonify
from supabase import create_client, Client

app = Flask(__name__)

url = "https://hljaiwqvdchahyfsvpdh.supabase.co"
key = "YOUR_SUPABASE_API_KEY"  # Replace with your actual Supabase API key
supabase: Client = create_client(url, key)

@app.route('/users.signup', methods=['POST', 'GET'])
def api_users_signup():
    try:
        Email = request.form.get('email')
        Name = request.form.get('name')
        Password = request.form.get('password')
        Location = request.form.get('location')
        Phone = request.form.get('phone')
        error = False

        # Debugging: Print received form data
        print(f"Received signup request with data: {request.form}")

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
            print(f"Supabase response for signup: {response}")
            if len(response.data) == 0:
                error = 'Error creating the user'

        if error:
            print(f"Signup error: {error}")
            return jsonify({'status': 500, 'message': error})

        return jsonify({'status': 200, 'message': '', 'data': response.data[0]})

    except Exception as e:
        print(f"Exception during signup: {str(e)}")
        return jsonify({'status': 500, 'message': f'Internal Server Error: {str(e)}'})


@app.route('/users.login', methods=['POST', 'GET'])
def api_users_login():
    try:
        email = request.form.get('email')
        password = request.form.get('password')
        error = False

        # Debugging: Print received form data
        print(f"Received login request with data: {request.form}")

        if (not email) or (len(email) < 5):
            error = 'Email needs to be valid'

        if (not error) and ((not password) or (len(password) < 5)):
            error = 'Provide a password'

        if (not error):
            response = supabase.table('User').select("*").ilike('Email', email).eq('Password', password).execute()
            print(f"Supabase response for login: {response}")
            if len(response.data) > 0:
                return jsonify({'status': 200, 'message': '', 'data': response.data[0]})

        if not error:
            error = 'Invalid Email or password'

        print(f"Login error: {error}")
        return jsonify({'status': 500, 'message': error})

    except Exception as e:
        print(f"Exception during login: {str(e)}")
        return jsonify({'status': 500, 'message': f'Internal Server Error: {str(e)}'})

if __name__ == "__main__":
    app.run(debug=True)
