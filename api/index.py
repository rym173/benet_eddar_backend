from flask import Flask, request, jsonify,json
from supabase import create_client, Client
import os
import xml.etree.ElementTree as ET


app = Flask(__name__)

url = "https://hljaiwqvdchahyfsvpdh.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhsamFpd3F2ZGNoYWh5ZnN2cGRoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MDI0NjM1MzUsImV4cCI6MjAxODAzOTUzNX0.3CioZ51QSifNdWya5a_h4jhOxx_Qp4f79GhsuNNTCl0"

supabase: Client = create_client(url, key)

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the full path to the XML file
xml_file_path = os.path.join(script_dir, 'commune.xml')

# Parse the XML file
tree = ET.parse(xml_file_path)
root = tree.getroot()


# Implement search logic
def search_communes(query):
    results = []
    for record in root.findall('.//record'):
        name = record.find('field[@name="name"]').text
        if name.lower().startswith(query.lower()):
            results.append(name)
    return results

@app.route('/enterLocation', methods=['GET'])
def search():
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'Invalid query'}), 400

    results = search_communes(query)
    return jsonify({'results': results})

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


@app.route('/users.login', methods=['POST', 'GET'])
def api_users_login():
    try:
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

        return jsonify({'status': 500, 'message': error})

    except Exception as e:
        return jsonify({'status': 500, 'message': f'Internal Server Error: {str(e)}'})
    
        
@app.route('/users.changePassword', methods=['PUT'])
def api_users_change_password():
    phone = request.form.get('phone')
    new_password = request.form.get('newPassword')
    error = False

    # Validate phone
    if (not phone) :
        error = 'Phone needs to be valid'
     # Convert phone to integer
    phone_as_int = int(phone) if phone.isdigit() else None       

    # Validate new password
    if (not error) and ((not new_password) or (len(new_password) < 5)):
        error = 'Provide a valid new password'

    # Update the password in the Supabase database
    if not error:
        response = supabase.table('User').update({"Password": new_password}).eq('Phone', phone_as_int).execute()
        if len(response.data) == 0:
            error = 'Error updating the password'

    if error:
        return json.dumps({'status': 400, 'message': error})

    return json.dumps({'status': 200, 'message': 'Password updated successfully'})

@app.route('/users.getMenusAndDishesForUser', methods=['GET'])
def get_all_cooks_menus():
    try:
        response = supabase.table('Menu').select("*").execute()
        menus = response.data
        if not menus:
            print('No menus found')
            return jsonify({'status': 404, 'message': 'No menus found'}), 404

        for menu in menus:
            response = supabase.table('Menus_Dishes').select('Dish_ID').filter('Menu_ID', 'eq', menu['Menu_ID']).execute()
            dishes = response.data
            dish_ids = [dish['Dish_ID'] for dish in dishes]

            menu['dishes'] = []

            for dish_id in dish_ids:
                response = supabase.table('Dish').select("*").filter('Dish_ID', 'eq', dish_id).execute()
                menu['dishes'].extend(response.data)

        return json.dumps(menus), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'status': 500, 'message': 'Internal Server Error'}), 500
    
@app.route('/cooks/<int:cook_id>', methods=['GET'])
def get_cook_info(cook_id):
    try:
        response = supabase.table('Cook').select("*").filter('Cook_ID', 'eq', cook_id).execute()
        cook_info = response.data
        print(cook_info)
        if not cook_info:
            return jsonify({'status': 404, 'message': 'No cook found with this ID'}), 404
        return jsonify({'status': 200, 'data': cook_info}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'status': 500, 'message': 'Internal Server Error'}), 500
    
@app.route('/registerLineOrder', methods=['POST'])
def register_line_order():
    try:
        # Récupérer les données du formulaire
        order_id=request.json.get('Order_ID')
        dish_name = request.json.get('Order_Descriptions')
        dish_quantity = request.json.get('Quantity')

        # Insérer les données dans la table Order_line
        response = supabase.table('Order_line').insert({
            'Order_ID':order_id,
            'Order_Descriptions': dish_name,
            'Quantity': dish_quantity
        }).execute()
        if hasattr(response, 'error') and response.error:
            raise Exception('Failed to register order: ' + response.error.message)

        return jsonify({'status': 200, 'message': '', 'data': response.data})

    except Exception as e:
        print('Error: ', e)
        return jsonify({'status': 500, 'message': str(e)}), 500
    
@app.route('/registerOrder', methods=['POST'])
def register_order():
    try:
        # Récupérer les données du formulaire
        cook_id=request.json.get('cookId')
        user_id=request.json.get('userId')
        special_inst = request.json.get('SpecialInst')
        order_status = request.json.get('OrderStatus')
        price = request.json.get('price')
        

        # Insérer les données dans la table FullOrder
        response = supabase.table('FullOrder').insert({
            'User_ID':user_id,
            'Special_Inst': special_inst,
            'OrderStatus': order_status,
            'TotalPrice': price,
            'Cook_ID':cook_id
        }).execute()

        if hasattr(response, 'error') and response.error:
            raise Exception('Failed to register order: ' + response.error.message)

        # Accéder au premier élément de la liste de données et récupérer 'Trans_ID'
        trans_id = response.data[0]['Trans_ID']

        # Retourner l'ID de la colonne Trans_ID
        return jsonify({'status': 200, 'message': '', 'data': trans_id})

    except Exception as e:
        print('Error: ', e)
        return jsonify({'status': 500, 'message': 'Failed to register order: ' + str(e), 'data': {}})
      
@app.route('/cooks/<int:cook_id>/menus', methods=['GET'])
def get_cook_menus(cook_id):
    try:
        response = supabase.table('Menu').select("*").filter('Cook_ID', 'eq', cook_id).execute()
        menus = response.data
        if not menus:
            print('No menus found for this cook')
            return jsonify({'status': 404, 'message': 'No menus found for this cook'}), 404

        for menu in menus:
            response = supabase.table('Menus_Dishes').select('Dish_ID').filter('Menu_ID', 'eq', menu['Menu_ID']).execute()
            dishes = response.data
            dish_ids = [dish['Dish_ID'] for dish in dishes]

            menu['dishes'] = []

            for dish_id in dish_ids:
                response = supabase.table('Dish').select("*").filter('Dish_ID', 'eq', dish_id).execute()
                menu['dishes'].extend(response.data)

        return json.dumps(menus), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'status': 500, 'message': 'Internal Server Error'}), 500
    
@app.route('/users/<int:user_id>/orders', methods=['GET'])
def get_users_orders(user_id):
    try:
        # Fetch orders from FullOrder table
        response_full_order = supabase.table('FullOrder').select(
            'Trans_ID',
            'OrderStatus',
            'OrderDate',
            'Special_Inst',
            'TotalPrice'
        ).filter('User_ID', 'eq', user_id).filter('User_ID', 'eq', user_id).filter('OrderStatus', 'eq', 'En attente').execute()

        if 'error' in response_full_order:
            error_message = response_full_order['error']['message']
            print(f'Error: {error_message}')
            return jsonify({"error": error_message})

        orders = response_full_order.data

        formatted_orders = []
        for order in orders:
            order_id = order['Trans_ID']

            # Fetch order line details
            response_order_line = supabase.table('Order_line').select(
                'Order_Descriptions',
                'Quantity'
            ).filter('Order_ID', 'eq', order_id).execute()

            if 'error' in response_order_line:
                error_message = response_order_line['error']['message']
                print(f'Error: {error_message}')
                return jsonify({"error": error_message})

            order_line_data = response_order_line.data
            # Create a list of dishes
            dishes = []
            for dish in order_line_data:
                dishes.append({
                    "order_description": dish['Order_Descriptions'],
                    "quantity": dish['Quantity']
                })

            
            # Fetch user details
            response_user = supabase.table('User').select(
                'Location',
                'Name',
                'Phone'
            ).filter('UserID', 'eq', user_id).execute()

            if 'error' in response_user:
                error_message = response_user['error']['message']
                print(f'Error: {error_message}')
                return jsonify({"error": error_message})

            user_data = response_user.data[0]

            # Combine data into the desired format
            formatted_order = {
                "order_id": order_id,
                "dishes": dishes,
                "order_date": order['OrderDate'],
                "order_status": order['OrderStatus'],
                "special_instruction": order['Special_Inst'],
                "total_price": order['TotalPrice'],
                "user_location": user_data['Location'],
                "user_name": user_data['Name'],
                "user_phone": user_data['Phone']
            }

            formatted_orders.append(formatted_order)

        return jsonify({"orders": formatted_orders})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'status': 500, 'message': 'Internal Server Error'}), 500
    
@app.route('/users/<int:user_id>/treatedOrders', methods=['GET'])
def get_users_treatedOrders(user_id):
    try:
        # Fetch orders from FullOrder table
        response_full_order = supabase.table('FullOrder').select(
            'Trans_ID',
            'OrderStatus',
            'OrderDate',
            'Special_Inst',
            'TotalPrice'
        ).filter('User_ID', 'eq', user_id).filter('User_ID', 'eq', user_id).filter('OrderStatus', 'neq', 'En attente').execute()

        if 'error' in response_full_order:
            error_message = response_full_order['error']['message']
            print(f'Error: {error_message}')
            return jsonify({"error": error_message})

        orders = response_full_order.data

        formatted_orders = []
        for order in orders:
            order_id = order['Trans_ID']

            # Fetch order line details
            response_order_line = supabase.table('Order_line').select(
                'Order_Descriptions',
                'Quantity'
            ).filter('Order_ID', 'eq', order_id).execute()

            if 'error' in response_order_line:
                error_message = response_order_line['error']['message']
                print(f'Error: {error_message}')
                return jsonify({"error": error_message})

            order_line_data = response_order_line.data
            # Create a list of dishes
            dishes = []
            for dish in order_line_data:
                dishes.append({
                    "order_description": dish['Order_Descriptions'],
                    "quantity": dish['Quantity']
                })

            
            # Fetch user details
            response_user = supabase.table('User').select(
                'Location',
                'Name',
                'Phone'
            ).filter('UserID', 'eq', user_id).execute()

            if 'error' in response_user:
                error_message = response_user['error']['message']
                print(f'Error: {error_message}')
                return jsonify({"error": error_message})

            user_data = response_user.data[0]

            # Combine data into the desired format
            formatted_order = {
                "order_id": order_id,
                "dishes": dishes,
                "order_date": order['OrderDate'],
                "order_status": order['OrderStatus'],
                "special_instruction": order['Special_Inst'],
                "total_price": order['TotalPrice'],
                "user_location": user_data['Location'],
                "user_name": user_data['Name'],
                "user_phone": user_data['Phone']
            }

            formatted_orders.append(formatted_order)

        return jsonify({"orders": formatted_orders})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'status': 500, 'message': 'Internal Server Error'}), 500
    
@app.route('/cancel_order/<int:order_number>/finish', methods=['POST', 'GET'])
def cancel_order(order_number):
        
    response = supabase.table('FullOrder').delete().eq('Trans_ID', order_number).execute()
    if len(response.data) == 0:
        error = 'Error updating the order status'
    else:
            # Process any other logic related to accepting or rejecting the order
            return jsonify({'message': f'Order cancelled successfully'})

               
@app.route('/')
def about():
    return 'Welcome to benet eddar'


if __name__ == "__main__":
    app.run(debug=True,port=5000)
