from flask import *
import random
from main_ai import Main
from main_db import DATA
from data_source import DataSource
from honeybadger.contrib import FlaskHoneybadger

db = DATA()
ai = Main() 
data = DataSource()

app = Flask(__name__)            
app.config['HONEYBADGER_ENVIRONMENT'] = 'production' #Set HONEYBADGER_ENVIRONMENT configuration variable in the application to 'production'
app.config['HONEYBADGER_API_KEY'] = 'hbp_MYOQ2R1pf24h8CnVXiXCtQbYv8Bijm4yNgCZ'
app.config['HONEYBADGER_PARAMS_FILTERS'] = 'password, secret, credit-card'
FlaskHoneybadger(app, report_exceptions=True) #allows for admin to receive error reports and updates

theme = 'css/dist/theme/blood.css'

@app.route("/", methods=['GET', 'POST']) 
def index():
    global theme
    try: theme = request.get_json()['theme_url'].replace('static/', '')
    except Exception as e: print(e)
    if request.method == "POST": return name() 
    return render_template("index.html", theme=theme, placeholder="e.g. likes, interests, favourite things...")  
    
    
@app.route("/Your Baby Name", methods=['GET', 'POST']) #shows the name and will have a button that will send to a page with facts and data or a button to show similar names
def name(): 
    genders, origins = [], {}
    try: 
        keys, names, descriptions = ai.get_babynames(request.form['prompt'], (request.form['gender'] if request.form['gender'] != 'unknown' else 'boy and girl'))
        if len(keys) == 0: print('\n', '-------------- Invalid Input ---------------', '\n'); return not_acceptable(406,'Input a valid prompt -', 'Invalid Prompt')
        else:
            for name in names:
                try: genders, origins = ai.get_name_data_ai(name, genders, origins)      
                except Exception as e: print(e)
            return render_template("your_names.html", theme=theme, keys=keys, names=names, descriptions=descriptions, origins=origins, genders=genders)
    except Exception as e: 
        print('\n', '-------------------------- Issue retrieving names ----------------------------', '\n', e, '\n')
        return not_acceptable(406,'Issue retrieving names -', 'OpenAI API Error')
    
@app.route("/Fact Page", methods=['GET', 'POST']) 
def fact_page():
    if request.method == 'POST':
        try:
            name_dict, graph_dict = data.get_data(request.form['baby_name'], ('boys' if request.form['baby_gender'] == 'male' else 'girls'))
            gender = (request.form['baby_gender'].capitalize() if (request.form['baby_gender'].capitalize() == 'Male' or request.form['baby_gender'].capitalize() == 'Female') else 'Unisex')
            return render_template("fact_page.html", theme=theme, name=request.form['baby_name'].capitalize() , country=ai.get_text(('what country does ' + request.form['baby_name'] + ' originate from? (repsonce should only contain country)')), desc=request.form['baby_desc'], gender=gender.capitalize(), origin=request.form['baby_origin'], img=ai.get_img(random.choice(['family', 'kids', 'baby', 'child'])), name_dict=name_dict, graph_dict=graph_dict)
        except Exception as e: 
            print(e)
            return bad_request(400)
    return bad_request(400)
    
@app.route("/name finder", methods=['GET', 'POST']) 
def name_finder_page():
    if request.method == "POST": 
        try: return name()   
        except Exception as e: print(e)
    return render_template("name_finder.html", theme=theme, placeholder="e.g. likes, interests, favourite things...")

@app.route("/about", methods=['GET', 'POST'])
def about_page(): return render_template("about_page.html", theme=theme, img=ai.get_img(random.choice(['family', 'baby', 'child'])))

@app.route("/boy names", methods=['GET', 'POST'])
def top_100_boy_page(genders='Boy'):
    if request.method == "POST": 
        try:
            name_dict, graph_dict = data.get_data(request.form['name'], 'boys')
            return render_template("fact_page.html", theme=theme, name=request.form['name'], origin=None, gender='Male', country=ai.get_text(('what country does ' + request.form['name'] + ' originate from? (repsonce should only contain country)')), desc=ai.get_text('what type of person would best suit the name ' + request.form['name'] + ' (minimum 50 words)?'), img=ai.get_img('boy'), name_dict=name_dict, graph_dict=graph_dict)
        except Exception as e: 
            print(e)
            return bad_request(400)
    names, counts = ai.get_100_names(genders)
    return render_template("top_100.html", theme=theme, gender=genders, action='top_100_boy_page', names=names, counts=counts)

@app.route("/girl names", methods=['GET', 'POST'])
def top_100_girl_page(genders='Girl'):
    if request.method == "POST": 
        try:
            name_dict, graph_dict = data.get_data(request.form['name'], 'girls')
            return render_template("fact_page.html", theme=theme, name=request.form['name'], origin=None, gender='Female', country=ai.get_text(('what country does ' + request.form['name'] + ' originate from? (repsonce should only contain country)')), desc=ai.get_text('what type of person would best suit the name ' + request.form['name'] + ' (minimum 50 words)?'), img=ai.get_img('girl'), name_dict=name_dict, graph_dict=graph_dict)
        except Exception as e: 
            print(e)
            return bad_request(400)
    names, counts = ai.get_100_names(genders)
    return render_template("top_100.html", theme=theme, gender=genders, action='top_100_girl_page', names=names, counts=counts)

@app.route("/contact", methods=['GET', 'POST'])
def contact_page(): return render_template("contact_page.html", theme=theme)

@app.route("/contact form", methods=['GET', 'POST'])
def contact_form_page():
    if request.method == 'POST': return thanks() 
    return render_template("contact-form.html", theme=theme, title="Contact Form")

@app.route("/thank you", methods=['GET', 'POST']) 
def thanks(): 
    try:
        if ai.check_email(request.form['email']):
            try: ai.send_email(request.form['email'], request.form['name'])
            except Exception as e: print(e)
            return render_template("form1.html", theme=theme, template="template-form1-2.html", display1="none", display2="none", display3="none", display4="none", display5="none", display6="none", display7="none", display8="none", display9="none", display10="block",  display11="block", title="Thank You", header=('Thanks ' + request.form['name'] + ' For Contacting Us!'), s_header='We will get back to you shortly!')
        return not_acceptable(406,'Input a valid email -', 'Invalid Email')
    except: return bad_request(400)

@app.route("/demo")
def demo(): return render_template("demo.html")

@app.errorhandler(400)                                                        
def bad_request(e): return render_template('form1.html', template="template-form1.html", colour1='#333333', colour2='#777777', colour3='#dddddd', display1="none", display2="none", display3="none", display4="none", display5="block", display6="none", display7="none", display8="none", display9="none", display10="block", display11="none", title="Bad Request", header='400 Error', s_header='request could not be complete, please return to previous page'), 400      

@app.errorhandler(404)                                                        
def page_not_found(e): return render_template('form1.html', template="template-form1.html", colour1='#333333', colour2='#777777', colour3='#dddddd', display1="none", display2="none", display3="none", display4="none", display5="block", display6="none", display7="none", display8="none", display9="none", display10="block", display11="none", title="Page Not Found", header='404 Error', s_header='page not found, please return to previous page'), 404  

@app.errorhandler(500)                                                
def internal_sever_error(e): return render_template('form1.html', template="template-form1.html", colour1='#333333', colour2='#777777', colour3='#dddddd', display1="none", display2="none", display3="none", display4="none", display5="block", display6="none", display7="none", display8="none", display9="none", display10="block", display11="none", title="Sever Error", header='500 Error', s_header='internal sever error, please check local host connectivity'), 500  

@app.errorhandler(401) 
def unauthorized(e): return render_template('form1.html', template="template-form1.html", colour1='#FF0000', colour2='#800000', colour3='#CA3433', display1="none", display2="none", display3="none", display4="none", display5="block", display6="none", display7="none", display8="none", display9="none", display10="block", display11="none", title="Validation Error", header='401 Error', s_header='access not granted, please return to previous page'), 401

@app.errorhandler(406) 
def not_acceptable(e, error='Validation error,', header='406 Error'): return render_template('form1.html', template="template-form1.html", colour1='#FF0000', colour2='#800000', colour3='#CA3433', display1="none", display2="none", display3="none", display4="none", display5="block", display6="none", display7="none", display8="none", display9="none", display10="block", display11="none", title="Input Validation Error", header=header, s_header=error+" please return to previous page and try again"), 406

@app.errorhandler(408)                                                
def timed_out(e): return render_template('form1.html', template="template-form1.html", colour1='#333333', colour2='#777777', colour3='#dddddd', display1="none", display2="none", display3="none", display4="none", display5="block", display6="none", display7="none", display8="none", display9="none", display10="block", display11="none", title="Request Timed Out", header='408 Error', s_header='request timed out, please return to previous page'), 408  


if __name__ == '__main__':
    app.run(debug=True, port=8000, use_reloader=True, processes=0, threaded=True)
    
