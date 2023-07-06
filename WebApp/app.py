from flask import Flask, redirect, render_template, request, url_for,jsonify
from algo import main
from troll import f
app = Flask(__name__)
group_number = 28
tabu = []
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        global group_number
        group_number = request.form['name']
        return redirect(url_for('hello'))
    return render_template('form.html')

@app.route('/update_tabu', methods=['POST'])
def update_tabu():
    global tabu
    selected_seats = request.get_json().get('selected_seats')
    if selected_seats:
        tabu.append(selected_seats[0])
    #print(tabu)
    
    return jsonify(message='Tabu list updated successfully')
   
@app.route('/hello',methods=['GET', 'POST'])
def hello():
  return render_template('index.html', taken_seats=main(group_number,tabu))

if __name__ == '__main__':
    app.run(debug=True)
