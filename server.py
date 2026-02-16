from pymongo import MongoClient
from flask import Flask, request, jsonify,json
from flask_sock import Sock
from datetime import datetime
import os
from dotenv import load_dotenv
import bcrypt
from flask_cors import CORS

load_dotenv()
app=Flask(__name__)
CORS(app)
socket=Sock(app)
client=MongoClient(os.getenv("MONGO_URL"))
database=client["smart_cart"]
collection=database['products']
cart=database['cart']
device=database['device']
user=database['user']
s=bcrypt.gensalt()
carts={}
clients={}
@socket.route("/ws")
def websocket(ws):
    print("WS CONNECTED")

    while True:
        data = ws.receive()
        if data is None:
            break

        print("RAW:", data)

        try:
            message = json.loads(data)
        except:
            ws.send(json.dumps({"error": "invalid json"}))
            continue

        if message["connection"] == "register":
            carts[message["cartID"]] = ws
            ws.send(json.dumps({"status": "registered"}))

        elif message["connection"] == "sub":
            clients[ws] = message["cartID"]
            ws.send(json.dumps({"status": "subscribed"}))

        elif message["connection"] == "senddata":
            cartID = message["cartID"]
            print("barcode:", message["barcode"])

            tosend = {
                "barcode": message["barcode"],
                "weight": message["weight"]
            }

            sent = False
            for client_ws, cid in list(clients.items()):
                if cid == cartID:
                    try:
                        client_ws.send(json.dumps(tosend))
                        sent = True
                    except:
                        clients.pop(client_ws, None)

            ws.send(json.dumps({"sent": sent}))

    clients.pop(ws, None)
    print("WS DISCONNECTED")

@app.route("/add_product",methods=["POST"])
def add_product():
    data=request.json
    barcode=data.get("barcode")
    product={
        "barcode":barcode,
        "item":data.get("item"),
        "weight":data.get("weight"),
        "price":data.get("price"),
        "discount":data.get("discount")

    }
    collection.replace_one({"barcode":barcode},product,upsert=True)
    return jsonify("item added"),200
@app.route("/get_product/<barcode>",methods=["GET"])
def get_product(barcode):
    product=collection.find_one({"barcode":barcode},{"_id":0})
    if not product:
        return jsonify({"error":"product not found"}),404
    else:
        return jsonify(product),200
@app.route("/user_creation",methods=["POST"])
def user_creation():
    data=request.json
    password=data.get("password")
    hashed_pass=bcrypt.hashpw(password.encode('utf-8'),s)
    user_data={
        "userid":data.get("userid"),
        "name":data.get("name"),
        "email":data.get("email"),
        "password":hashed_pass.decode('utf-8')

        
    
    }
    user.replace_one({"userid":data["userid"]},user_data,upsert=True)
    return jsonify({"message":"user updated"}),200
@app.route("/add_cart",methods=["POST"])
def add_cart():
    data=request.json
    userid=data.get("userid")
    barcode=data.get("barcode")
    quantity=data.get("quantity")
    product=collection.find_one({"barcode":barcode},{"_id":0})
    if not product:
        return jsonify({"message":"product not found"}),404
    cart_items={
        "userid":userid,
        "barcode":barcode,
        "item":product["item"],
        "quantity":quantity,
        "price":product["price"],
        "timestamp":datetime.utcnow()

    }
    cart.insert_one(cart_items)
    return jsonify({"message":"cart updated"}),200
@app.route("/verification",methods=["POST"])
def view_list():
    data=request.json
    useride=data["userid"]
    passworde=data["password"]
    userdatal=user.find_one({"userid":useride},{"_id":0})
    if userdatal:
        stored_pw=userdatal["password"]
        if bcrypt.checkpw(passworde.encode("utf-8"),stored_pw.encode("utf-8")):
            return jsonify({"message:":"password is correct"}),200
        else:
            return jsonify({"message":"wrong password"}),200
    else:
        return jsonify({"message":"user not found"}),404

    
@app.route("/view_list/<userid>",methods=["GET"])
def view_listl(userid):
    cartlist=list(cart.find_one({"userid":userid},{"_id":0}))
    if not cartlist:
        return jsonify({"error:":"An error occured"}),404
    else:
        return jsonify(cartlist),200
if __name__=="__main__":
    app.run(host="0.0.0.0",port=5000)