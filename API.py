from flask import Flask, jsonify
from flask import make_response
from flask import abort,request

app = Flask(__name__)

#default route
@app.route("/")
def hello():
    return "Hello World!"
#Test Test only
# @app.route("/ev3test/<chr:port>/<int:angle>")
# def ev3test(port,angle):
#     if (angle==1) and (port=="A"):
#         return "Angle : 50: port is A"
#     else:
#         abort(404)

@app.route("/ev3test/<int:angle>")
def ev3test(angle):
    return "Angle : "+str(angle)+str(request.args.get('port'))+": port is A"
    
#reset the robotic arm position
@app.route("/ev3reset")
def ev3reset():
    return "resetAll!"
#control the port and speed
@app.route("/ev3rotate")
def ev3rotate():
    return "Port number and Speed"
#catch the piece
@app.route("/ev3catch")
def ev3catch():
    return "I have gotten the pieces"

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

if __name__ == '__main__':
    #app.run(debug=True)
    app.run(host='0.0.0.0')