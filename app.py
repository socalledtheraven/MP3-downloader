from flask import Flask, render_template, request, Response, url_for, send_file, flash, session
import functions

app = Flask(__name__)
app.config['SECRET_KEY'] = '2c7f07064e05560b9745cfef4fda2b7307aaf3f7' # fix this, but its the original owner's so no real rush

max_results_count = 5
# videos vost for current client

@app.route('/') 
@app.route('/index')
def index():
    # clear data on the main page
    session['videos'] = [] 
    session['urls'] = [] 
    session['current_title'] = "" 
    return render_template("index.html", videos=False)


@app.route('/search', methods=["POST"])
def search():
    # clear old data
    videos_list = []
    session['urls'] = [] 
    session['current_title'] = "" 
   
    title = request.form["search_input"]
    # entered link
    try:
        if "http" in  title:
            video = functions.search_video_data(title)
            video['number'] = len(videos_list) + 1
            session['videos'] = [video]
        # entered text
        else:
            session['urls'] = functions.get_linklist_by_title(title) ############33
        # urls = functions.get_linklist_by_title(title)
            for i in range(min(len(session['urls']), max_results_count)):
                video = functions.search_video_data(session['urls'][i])
                video['number'] = i+1
                videos_list.append(video)     
                
            session['videos'] = videos_list   
    except:
        flash('Searching error.')
     
    return render_template("index.html", videos = session['videos'])

@app.route('/download', methods=["POST"])
def download():
    action, video_number = request.form["button"], int(request.form["data"])
    #print("Entered action:", action, "entered video id", video_number)

    # validate number
    if video_number < 0 or video_number > len(session['videos']): # do nothing, for safety
        return render_template("index.html", videos = session['videos'])

    if action == "Download":

        try:
            stream, session['current_title'] = functions.get_stream(session['videos'][video_number-1])
            stream.download(filename='temp-download.txt')
        except:
            flash('Downloading error.')
            session['videos'][video_number-1]['description'] = session['videos'][video_number-1]['description'] + ' | unavailable to download'
            return render_template("index.html", videos = session['videos'])

        
        # only one file can be downloaded at moment
        for each in session['videos']:
            each['ready'] = False
        session['videos'][video_number-1]['ready'] = True
        session.modified = True
       
        flash('File is ready. You can download it pushing button "Save"')
        
        return render_template("index.html", videos = session['videos'])

    elif action == "Save":
        return send_file('temp-download.txt', as_attachment=True, download_name = session['current_title'] )

@app.errorhandler(503)
def page_not_found(e):
    flash('FIle is too big.')
    return render_template("index.html", videos = session['videos'])



@app.route('/wakemydyno.txt')
def get_text():
    return Response("", mimetype="text/plain")



if __name__ == "__main__":
    app.run(debug=True)  
