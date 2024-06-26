from flask import Flask, render_template, redirect, url_for, request, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user
import json
import time
import requests
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mail import Mail, Message
import secrets

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SECRET_KEY'] = 'your_secret_key_here'  # Replace with a secure secret key
app.config['MAIL_SERVER'] = 'imap.gmail.com'  # Example: 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587  # Use your mail server's port for SMTP
app.config['MAIL_USE_TLS'] = True  # Enable TLS encryption
app.config['MAIL_USERNAME'] = 'luisereyes03@gmail.com'  # Your email address
app.config['MAIL_PASSWORD'] = 'jisx kews kfev cdto'  # Your email password







ngrok_url = "https://ea37-2600-1700-3680-6120-201f-74cc-9707-ca9a.ngrok-free.app/"







mail = Mail(app)
# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

# Example User class (replace with your User class)
class User(UserMixin):
    def __init__(self, username, password, email, full_name, balance=0, ps="roblox.com"):
        self.username = username
        self.password = password
        self.email = email
        self.full_name = full_name
        self.balance = balance
        self.ps = ps

    def get_id(self):
        return str(self.username)
    



















# Function to load user data from JSON file
def load_users_data():
    with open('data/data.json', 'r') as f:
        return json.load(f)

# Function to save updated user data to JSON file
def save_users_data(users_data):
    with open('data/data.json', 'w') as f:
        json.dump(users_data, f, indent=4)






def load_users():
    try:
        with open('data/data.json', 'r') as f:
            data = json.load(f)
            return data.get('users', {})
    except FileNotFoundError:
        return {}

@login_manager.user_loader
def load_user(username):
    users = load_users()
    if username in users:
        user_data = users[username]
        user = User(username, user_data['password'], user_data['email'], user_data['full_name'], user_data.get('balance', 0), user_data['ps'])
        return user
    return None

@app.route('/')
def index():
    return redirect(url_for('dhc'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = load_users()

        if username in users and users[username]['password'] == password:
            user = load_user(username)
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            error = 'Invalid username or password. Please try again.'

    return render_template('login.html', error=error)

# Payments route
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)



@app.route('/dahoodcash')
def dhc():
    return render_template('dahoodcash.html', user=current_user)




@app.route('/signup')
def signupdash():
    return render_template('signup.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        email = request.form['email']
        full_name = request.form['full_name']

        users = load_users()

        if username in users:
            return 'Username already exists. Please choose a different username.'
        
        if password != confirm_password:
            return 'Passwords do not match. Please re-enter your password.'

        new_user = {
            'password': password,
            'email': email,
            'full_name': full_name,
            'balance': 0,
            'ps': ""
        }

        users[username] = new_user

        with open('data/data.json', 'w') as f:
            json.dump({'users': users}, f, indent=4)

        return redirect(url_for('login'))

    return render_template('signup.html')

# Payments route
@app.route('/payments')
@login_required
def payments():
    return render_template('payments.html', user=current_user)


# Payments route
@app.route('/dropping')
@login_required
def dropping():
    return render_template('dropping.html', user=current_user)




@app.route('/pickupdhc')
@login_required
def pickupdhc():
    return render_template('pickupdhc.html', user=current_user)


# Route to check for balance updates
@app.route('/check_balance_updates')
@login_required
def check_balance_updates():
    initial_balance = current_user.balance
    while True:
        time.sleep(5)  # Check every 5 seconds
        current_balance = get_user_balance(current_user.username)
        if current_balance != initial_balance:
            return jsonify({'username': current_user.username, 'new_balance': current_balance})
    return jsonify({})  # In case of no updates

# Route to handle Sellix webhook
@app.route('/sellix-webhook', methods=['POST'])
def sellix_webhook():
    payload = request.json

    product_data = payload.get('data', {}).get('product', {})
    product_title = product_data.get('title')

    if product_title:
        amount = product_title.split(" ")[0]

        custom_fields = payload.get('data', {}).get('custom_fields', {})
        custom_reference = custom_fields.get('reference')

        if custom_reference:
            # Update user balance
            users = load_users()
            if custom_reference in users:
                users[custom_reference]['balance'] += float(amount)
                with open('data/data.json', 'w') as f:
                    json.dump({'users': users}, f, indent=4)
                return jsonify({'message': 'Balance updated successfully'}), 200
            else:
                return jsonify({'error': f"User '{custom_reference}' not found"}), 400
        else:
            return jsonify({'error': 'Custom reference not found in the webhook payload'}), 400
    else:
        return jsonify({'error': 'Product title not found in the webhook payload'}), 400



@app.route('/process_orders2/<username>/<user>', methods=['POST'])
@login_required
def process_orders(username, user):
    try:
        print(username)
        check = process_orders2(username)
        print("check", check)
        if check:  # Check if process_orders2 returned a valid amount
            # Update user balance in data.json
            with open('data/data.json', 'r+') as file:
                data = json.load(file)
                users = data.get('users', {})

                if user in users:
                    users[user]['balance'] += check
                    file.seek(0)
                    json.dump(data, file, indent=4)
                    file.truncate()

            # Log order in config.json
            user_id = current_user.get_id()
            line = f"{user_id} {check} {username}"
            with open('config.json', 'r') as file:
                config = json.load(file)
                config["Orders"].append(line)
            with open('config.json', 'w') as file:
                json.dump(config, file, indent=4)

            return jsonify({'success': True}), 200
        else:
            return jsonify({'success': False, 'message': 'Failed to process order.'}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/get_robux_options', methods=['GET'])
def get_robux_options():
    try:
        with open('config.json', 'r') as file:
            config = json.load(file)
            robux_options = config.get('Roblox_shirt_names', {})
            return jsonify(robux_options), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
def update_balance(username):
    file_path = 'data/data.json'

    # Open and read the JSON file
    with open(file_path, 'r') as file:
        data = json.load(file)

    # Check if the user exists
    if username in data['users']:
        # Set the balance of the user to 0
        data['users'][username]['balance'] = 0
        print(f"Successfully updated balance of {username} to 0.")
    else:
        print(f"User '{username}' not found.")

    # Write the updated JSON back to the file
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)


def get_balance(username):
    file_path = 'data/data.json'

    # Open and read the JSON file
    with open(file_path, 'r') as file:
        data = json.load(file)

    # Check if the user exists
    if username in data['users']:
        # Retrieve and return the balance of the user
        balance = data['users'][username]['balance']
        return balance
    else:
        print(f"User '{username}' not found.")
        return None

@app.route('/drop', methods=['POST'])
def drop_dahoodcash():
    try:
        # Assuming you want to make a request to an external URL
        url = ngrok_url + 'drop'
        
        # Retrieve data sent in the POST request from frontend
        data = request.get_json()
        
        # Assuming you want to pass the action to the external API
        action = data.get('action')
        amount = get_balance(action)
        payload = {'action': amount}  # Adjust payload as needed
        print(action)
        print(amount)


        # Make a POST request to the external URL
        response = requests.post(url, json=payload)
        print(response.json())
        # Check response status code from the external API
        if response.status_code == 200:
            response_data = response.json()
            print("updaing bal")
            update_balance(action)
            print("fin bal")
            return jsonify(response_data), 200
        else:
            return jsonify({'error': 'Failed to fetch data from external API'}), 500

    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500

@app.route('/check_status', methods=['GET'])
def check_status():
    try:
        # Make a GET request to the external URL
        url = ngrok_url + 'check_status'
        response = requests.get(url)

        # Check if request was successful (status code 200)
        if response.status_code == 200:
            response_data = response.json()  # Parse JSON response
            return jsonify(response_data), 200
        else:
            return jsonify({'error': 'Failed to fetch data'}), 500

    except requests.exceptions.RequestException as e:
        # Handle exception if request fails
        return jsonify({'error': str(e)}), 500

# Endpoint to fetch popup_timer from config.json
@app.route('/get_popup_timer', methods=['GET'])
def get_popup_timer():
    try:
        with open('config.json', 'r') as data_file:
            data = json.load(data_file)
            popup_timer = data.get('popup_timer')
        return jsonify({"popup_timer": popup_timer}), 200
    except FileNotFoundError:
        return jsonify({"error": "Config file not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500





@app.route('/is-farming', methods=['GET'])
def is_farming():
    try:
        # Make a GET request to the external URL
        external_url = ngrok_url + 'is-farming'
        response = requests.get(external_url)

        if response.status_code == 200:
            
            external_data = response.json()
            print("external_data",external_data)
            # Prepare the response based on the external data
            farming_data = {
                'isFarming': external_data.get('isFarming', False)  # Assuming the external data has 'isFarming' field
            }
        else:
            # Handle the case where the external request fails
            farming_data = {
                'isFarming': False  # Default to False if external request fails
            }

    except Exception as e:
        # Handle any exceptions that might occur during the request
        print(f"Error fetching external data: {e}")
        farming_data = {
            'isFarming': False  # Default to False if there's an error
        }

    return jsonify(farming_data)


# Renamed endpoint to verify status
@app.route('/verify_status', methods=['GET'])
def verify_status():
    try:
        # Fetch popup_timer from /get_popup_timer endpoint
        popup_response = json.loads(get_popup_timer().get_data(as_text=True))
        popup_timer = popup_response.get('popup_timer')

        if not popup_timer:
            return jsonify({"error": "Popup timer not set"}), 400

        # Parse popup_timer to datetime object
        popup_time = datetime.fromisoformat(popup_timer)

        # Get current time
        current_time = datetime.now()

        # Check if current time is after popup_time
        if current_time >= popup_time:
            # Make a GET request to the external URL
            url = ngrok_url + 'check_status'
            response = requests.get(url)

            # Check if request was successful (status code 200)
            if response.status_code == 200:
                response_data = response.json()  # Parse JSON response
                return jsonify(response_data), 200
            else:
                return jsonify({'error': 'Failed to fetch data'}), 500
        else:
            return jsonify({
                "error": "Someone",
                "currentlyat": "Someone has recently clicked this. Please try again in once the time passes."
            }), 400

    except requests.exceptions.RequestException as e:
        # Handle exception if request to external URL fails
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500



def process_orders2(username):
    print("ok proc")
    # Load the configuration from config.json
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)
        roblox_shirt_names = config['Roblox_shirt_names']
        Roblox_Cookie = config['Roblox_Cookie']

    data = get_group_sales_data2()

    username_lower = username.lower()
    try:
    # Retrieve all orders for the user
        orders_for_user = [order for order in data if order[1].lower() == username_lower]
    except:
        print("ERRRORRR")
 
    # Initialize a dictionary to store processed orders
    processed_orders = {}

    # Extract processed orders from the config
    for line in config["Processed_robux_orders"]:
        order_info = line.split()
        processed_orders[(order_info[0].lower(), order_info[1])] = True

    # Set to keep track of processed usernames in this run
    processed_usernames = set()

    # Process new orders
    for order in orders_for_user:
        amount = order[0]
        username = order[1]
        time_stamp = order[2]

        # Check if the order has already been processed or if the username has been processed in this run
        if processed_orders.get((username_lower, time_stamp)) or username_lower in processed_usernames:
            continue  # Skip to the next order

        # Check if the amount matches any shirt names
        if amount in roblox_shirt_names:
            line = f"{username} {time_stamp} {amount}"
            with open('config.json', 'r') as file:
                config = json.load(file)
                config["Processed_robux_orders"].append(line)
                file.close()
            # Write the updated JSON back to the file
            with open('config.json', 'w') as file:
                json.dump(config, file, indent=4)
                file.close()
            processed_usernames.add(username_lower)  # Add username to the set of processed usernames
            return roblox_shirt_names[amount][0]

    return False  # Return False if no matching order was processed




def get_group_sales_data2():
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)
        Roblox_Group_ID = "15432278"
        Roblox_Cookie = config["Roblox_Cookie"]
    url2 = "https://economy.roblox.com/v2/groups/{}/transactions?cursor=&limit=10&transactionType=Sale".format(Roblox_Group_ID)
    headers = {
        '.ROBLOSECURITY': Roblox_Cookie,
    }
    try:
        response = requests.get(url2, cookies=headers)
        if response.status_code == 200:
            data = response.json()
            result_list = []

            # Extract and append values for each transaction
            for transaction in data['data']:
                transaction_values = [
                transaction['details']['name'],
                transaction['agent']['name'],
                transaction['created']
                ]
                result_list.append(transaction_values)
            print(result_list)
            return result_list
    except Exception as e:
        print(f"Error: {e}")
        return "False"





@app.route('/add-friend', methods=['POST'])
def add_friend():
    try:
        data = request.get_json()
        username = data.get('username')
        message = data.get('message')

        # Obtain user_id based on username
        user_id = get_user_id_by_username(username)

        # Process friend request
        data_text = accept_friend_request(user_id)
        print("Data", data_text)
        if data_text == "True":  # Assuming accept_friend_request returns "True" on success
            receiver_url = ngrok_url + 'receive_user_id'  # Replace with actual URL of ReceiverApp
            requests.post(receiver_url, json={'user_id': user_id})
            with open('config.json', 'r+') as file:
                config = json.load(file)
                config["user_id"] = str(user_id)  # Convert user_id to string before assigning
                file.seek(0)  # Move the cursor to the beginning of the file
                json.dump(config, file, indent=4)  # Dump the updated config dictionary back to the file
                file.truncate()

            return jsonify({'success': True}), 200
        else:
            return jsonify({'error': 'Friend request failed to accept. Please try again.'}), 400

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500



def accept_friend_request(user_id):
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)
        Roblox_Cookie = config['Roblox_Cookie']
        config_file.close()
    url = f"https://friends.roblox.com/v1/users/{user_id}/accept-friend-request"
    headers = {
        '.ROBLOSECURITY': Roblox_Cookie,
    }
    response = requests.post(url, cookies=headers)
    cookies = {
        "x-csrf-token": response.headers["x-csrf-token"]
    }
    response3 = requests.post(url, cookies=headers, headers=cookies)
    if response3.status_code != 200:
        print(f"Failed to accept friend request. Status code: {response.status_code}")
        return "False"
    else:
        print("Successfully added")
        return "True"




def get_user_id_by_username(username):
    url = 'https://users.roblox.com/v1/usernames/users'
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    data = {
        'usernames': [username],
        'excludeBannedUsers': True
    }
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        json_res = response.json()
        if 'data' in json_res and json_res['data']:
            print("data")
            return json_res['data'][0]['id']
        else:
            raise ValueError('Invalid username!')
    except requests.exceptions.HTTPError as e:
        if response.status_code == 429 and 'Too many requests' in e.response.text:
            print("Please wait")
        else:
            raise ValueError('Failed to retrieve user ID:', e)









@app.route('/join_private_server', methods=['POST'])
def join_private_server():
    data = request.get_json()
    username = data.get('username')
    print(username)
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)
        Roblox_Cookie = config['Roblox_Cookie']   
        server_id = config["server_id"]
        
    url = "https://games.roblox.com/v1/vip-servers/{}".format(server_id)
    headers = {
        '.ROBLOSECURITY': Roblox_Cookie,
    }

    response = requests.get(url, cookies=headers)
    print(response.json())
    if response.status_code == 200:
        with open('data/data.json', 'r+') as data_file:
            data_json = json.load(data_file)
            if username in data_json["users"]:
                data_json["users"][username]["ps"] = response.json().get("link")
                data_file.seek(0)  # Move cursor to the beginning of file
                json.dump(data_json, data_file, indent=4)  # Write updated data back to file
                data_file.truncate()  # Truncate remaining content (in case new content is smaller)
        current_time = datetime.now()
        new_popup_time = current_time + timedelta(minutes=1)

        popup_timer_value = new_popup_time.isoformat()
        with open('config.json', 'r+') as data_file:
            data_json = json.load(data_file)
            data_json["popup_timer"] = popup_timer_value
            data_file.seek(0)  # Move cursor to the beginning of file
            json.dump(data_json, data_file, indent=4)  # Write updated data back to file
            data_file.truncate()  # Truncate remaining content (in case new content is smaller)
        return ({'server_link': response.json().get("link")}), 200





# Route to redeem a code
@app.route('/redeem-code', methods=['POST'])
def redeem_code():
    try:
        # Get username and code from request data
        data = request.get_json()
        username = data.get('username')
        redeem_code = data.get('code')

        if not username or not redeem_code:
            return jsonify({'error': 'Username and code are required fields.'}), 400

        # Load codes from JSON file
        with open('codes.json', 'r') as f:
            codes = json.load(f)

        # Check if code exists and get its value
        if redeem_code in codes:
            redeemed_amount = codes.pop(redeem_code)

            # Save updated codes back to JSON file
            with open('codes.json', 'w') as f:
                json.dump(codes, f, indent=4)

            # Load users from JSON file
            with open('data/data.json', 'r') as f:
                users = json.load(f)

            # Find the user by username and update balance
            if username in users['users']:
                users['users'][username]['balance'] += redeemed_amount

                # Save updated users back to JSON file
                with open('data/data.json', 'w') as f:
                    json.dump(users, f, indent=4)

                return jsonify({'success': True, 'amount': redeemed_amount}), 200
            else:
                return jsonify({'error': 'User not found.'}), 400

        else:
            return jsonify({'error': 'Code not found or already redeemed.'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500








if __name__ == '__main__':
    app.run(debug=True, port=7000)
