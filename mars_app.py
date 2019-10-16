import mars_functions as M
import flask as fl
import pymongo
import time as t

# Let's set up a Flask App
app = fl.Flask(__name__)


#--------/ CONNECT TO MONGO MARS /------------
my_db = 'mission_to_mars'
my_col = 'mars_scrape'
collection = M.mongo_me(my_db,my_col)

#--------/ APP ROUTES /------------


#--------/ INDEX /-----------------
@app.route("/")
def index():
     
    print('staring index route')
    
    #--------/ PULLING FROM MARS COLLECTION /------------
    my_mars = M.last_doc(collection)

    return fl.render_template('index.html',latest_scrape=my_mars)
    
    
@app.route("/scrape")
def scrape():
    
    print('starting scrape route')

    M.scrape_mars()
    
    print('Fresh Scrape!')

    # Redirect back to home page
    return fl.redirect("/", code=302)

#--------/ RUN APP /------------
if __name__ == "__main__":
    app.run(debug=True)