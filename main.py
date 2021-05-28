from app import app
from flask import jsonify
from flask import flash, request
import json
import uuid
import requests


carts = [{"cartId": "3317f46f-8dbb-4206-a3a1-668d1f50b1d0" , "accountId" : "j2ee", "items": [{"itemId" : "EST-1", "quantity" : "1", "inStock" : "true", "total" : "16.50" }]}]
#carts =  [{"accountId":"j2ee","cartId":"7cc7aa98-c07b-4282-b342-f5b2ae14d19b","items":[{"ProductId":"RP-LI-02","ProductName":"Green Adult Iguana","inStock":"true","itemId":"EST-13","quantity":1,"total":37.0},{"ProductId":"FI-SW-01","ProductName":"Small Angelfish","inStock":"true","itemId":"EST-2","quantity":1,"total":16.5},{"ProductId":"FL-DSH-01","ProductName":"With tail Manx","inStock":"true","itemId":"EST-15","quantity":1,"total":23.5},{"ProductId":"FI-SW-01","ProductName":"Large Angelfish","inStock":"true","itemId":"EST-1","quantity":"1","total":"16.50"},{"ProductId":"FI-FW-01","ProductName":"Spotted Koi","inStock":"true","itemId":"EST-4","quantity":1,"total":18.5},{"ProductId":"K9-BD-01","ProductName":"Male Adult Bulldog","inStock":"true","itemId":"EST-6","quantity":1,"total":74.0}]}]

# Use GET requests to retrieve resource representation/information only
@app.route('/carts', methods=['GET'])
def findAll():
    try:
        respone = jsonify(carts)
        respone.status_code = 200
        return respone
    except Exception as e:
        print(e) 

# Use GET requests to retrieve resource representation/information only
@app.route('/carts/<id>/items', methods=['GET'])
def findOne(id):
    try:
        one = find(id)
        if(one):
            
            for i in one['items']:
                status, item = get_items(i['itemId'])  
                i['ProductId'] = item['productId']
                status, product = get_product(i['ProductId'])  
                i['ProductName'] = item['attribute1'] + " " + product['name']
                
                print(item)

            respone = jsonify(one)
            respone.status_code = 200
            return respone
        else:
            return not_found()
    except Exception as e:
        print(e)


# Use GET requests to retrieve resource representation/information only
@app.route('/carts/<id>/merge', methods=['GET'])
def merge(id):
    sessionid = request.args.get('sessionId')

    print("sessionId = " + sessionid) 

    try: 
        session_items = find(sessionid)
        
        if(session_items):            
            for i in session_items['items']:
                status, item = get_items(i['itemId'])  
                i['ProductId'] = item['productId']
                status, product = get_product(i['ProductId'])  
                i['ProductName'] = item['attribute1'] + " " + product['name']
                
            print("session = " + str(session_items['items'])) 

        my_items = find(id)
        
        if(my_items):   
            for i in my_items['items']:
                status, item = get_items(i['itemId'])  
                i['ProductId'] = item['productId']
                status, product = get_product(i['ProductId'])  
                i['ProductName'] = item['attribute1'] + " " + product['name']
 
            print("cart = " + str(my_items['items'])) 

        if(session_items is not None and my_items is not None):
            for x in range(len(session_items['items'])):
                for y in range(len(my_items['items'])):
                    #print(session_items['items'][x] , " == " , my_items['items'][y])
                    if session_items['items'][x]['itemId'] == my_items['items'][y]['itemId']:
                        print(x , " : " , session_items['items'][x]['itemId'] , " == " , y , " : ", my_items['items'][y]['itemId'])
                        quantity = int(session_items['items'][x]['quantity']) + int(my_items['items'][y]['quantity']) 
                        total = float(session_items['items'][x]['total']) + float(my_items['items'][y]['total'])
                        my_items['items'][y]['quantity'] = quantity
                        my_items['items'][y]['total'] = float(total)
                        del session_items['items'][x]
                        break

                    
            items = session_items['items']   + my_items['items'] 
        elif(session_items is None and my_items is not None): 
            items = my_items['items'] 
        elif(session_items is not None and my_items is None): 
            items = session_items['items'] 
        else:
            return not_found()
 

        remove(id)
        remove(sessionid)
 
        cart =  {"cartId": uuid.uuid4() , "accountId" : id , "items": items}
        carts.append(cart)

        respone = jsonify(carts)
        respone.status_code = 200
        return respone 

    except Exception as e:
        print(e)

# Use POST APIs to create new subordinate resources
@app.route('/carts/<id>/update', methods=['POST'])
def update_cart(id):
    try:  
        #_json = {"items":[{"name":"EST-6","value":"4"},{"name":"EST-4","value":"5"},{"name":"EST-1","value":"6"},{"name":"EST-15","value":"7"},{"name":"EST-2","value":"14"},{"name":"EST-13","value":"8"}]}
        _json = request.json  
        
        items = find(id)

        for x in range(len(items['items'])):
            for y in _json['items']:
                if items['items'][x]['itemId'] == y['name']:
                    print(items['items'][x]['itemId'], " == " ,  y['name']) 

                    # get items http client
                    status, item = get_items(y['name'])  

                    if(status != 200):
                        not_found()

                    # get stock http client
                    status, stock = get_inventoris(y['name'])  

                    if(status != 200 or stock['qty'] == 0):
                        items['items'][x]['inStock'] = "false" 

                    quantity = int(y['value'])
                    listprice = float(item['listPrice'] )
                    total = listprice * float(quantity)
                    items['items'][x]['quantity'] = quantity
                    items['items'][x]['total']    = total

                    #print(str(listprice) , " + ", str(quantity) , " == " , str(total))
 
        respone = jsonify(items)
        respone.status_code = 200
        return respone
            
    except Exception as e:
        print(e)



# Use POST APIs to create new subordinate resources
@app.route('/carts/<id>', methods=['POST'])
def add_cart(id):
    try:
        #new = {"itemId" : "EST-1", "quantity" : "1", "inStock" : "true", "total" : "16.50" }
        _json = request.json

        _itemId = _json['itemId']
        _qty = _json['quantity']

        # get items http client
        status, item = get_items(_itemId)  

        if(status != 200):
            not_found()

        # get stock http client
        status, stock = get_inventoris(_itemId)  

        if(status != 200 or stock['qty'] == 0):
            not_found()

        _stock = "true"
        _total = item['listPrice'] 

        new = {"itemId" : _itemId ,"quantity" : _qty , "inStock" : _stock, "total" : _total}

        one = find(id)  
  
        if one == None:
            new_cart =  {"cartId": uuid.uuid4() , "accountId" : id , "items": []}
            carts.append(new_cart)

            one = find(id)              
            #print(one) 
        
        for i in one['items']:
            if i['itemId'] == _itemId:
                remove_item(_itemId,one['items'])
                quantity = int(_qty) + int(i['quantity'])
                total_price = float(_total) * float(quantity)
                new = {"itemId" : _itemId ,"quantity" :  quantity , "inStock" : _stock, "total" : total_price}

        print("new = " , new)
        
        one['items'].append(new) 
        respone = jsonify(one['items'])
        respone.status_code = 200
        return respone
            
    except Exception as e:
        print(e)

# DELETE APIs are used to delete resources
@app.route('/carts/<id>', methods=['DELETE'])
def del_cart(id):
    try:        
        one = find(id) 
        
        if one == None:
            return not_found()

        remove(id) 

        message = {
            'status': 200,
            'message': 'Record deleted.'
        } 

        respone = jsonify(message)
        respone.status_code = 200
        return respone
    except Exception as e:
        print(e)


# DELETE APIs are used to delete resources
@app.route('/carts/<id>/item/<cartid>', methods=['DELETE'])
def del_item(id,cartid):
    try:        
        one = find(id) 
        
        if one == None:
            return not_found()
        
        if one['items'] == None:
            return not_found()
        else:
            remove_item(cartid,one['items'])        

        message = {
            'status': 200,
            'message': 'Record deleted.'
        } 

        respone = jsonify(message)
        respone.status_code = 200
        return respone
    except Exception as e:
        print(e)

@app.errorhandler(404)
def not_found(error=None):
    message = {
        'status': 404,
        'message': 'Record not found: ' + request.url,
    }
    respone = jsonify(message)
    respone.status_code = 404
    return respone    

@app.errorhandler(409)
def duplicate_found(error=None):
    message = {
        'status': 409,
        'message': 'Duplicate resource or resource already exists. : ' + request.url,
    }
    respone = jsonify(message)
    respone.status_code = 404
    return respone    
  
def find(key):
    for i in carts:
        if(i['accountId'] == key):
            #print(i['accountId']," ",key)
            return i


def filter(key):
    for i in carts:
        if(i['accountId'] == key):
            print(i['accountId']," ",key)
            return i['items']

def remove(key):
    for i in range(len(carts)):
        if carts[i]['accountId'] == key:
            del carts[i]
            break

def remove_item(key,items):
    for i in range(len(items)):
        if items[i]['itemId'] == key:
            del items[i]
            break     

def get_items(itemId):
    headers = {'Content-Type': 'application/json'}
    try:
        url = "http://items:8080/items/" + str(itemId)
        res = requests.get(url, headers=headers, timeout=3.0)
    except BaseException:
        res = None
    if res and res.status_code == 200:
        return 200, res.json()
    else:
        status = res.status_code if res is not None and res.status_code else 500
        return status, {'error': 'Sorry, product ratings are currently unavailable for this book.'}


def get_inventoris(itemId):
    headers = {'Content-Type': 'application/json'}
    try:
        url = "http://inventoris:8080/inventoris/" + str(itemId)
        res = requests.get(url, headers=headers, timeout=3.0)
    except BaseException:
        res = None
    if res and res.status_code == 200:
        return 200, res.json()
    else:
        status = res.status_code if res is not None and res.status_code else 500
        return status, {'error': 'Sorry, product ratings are currently unavailable for this book.'}        

def get_product(productId):
    headers = {'Content-Type': 'application/json'}
    try:
        url = "http://products:8080/products/" + str(productId)
        res = requests.get(url, headers=headers, timeout=3.0)
    except BaseException:
        res = None
    if res and res.status_code == 200:
        return 200, res.json()
    else:
        status = res.status_code if res is not None and res.status_code else 500
        return status, {'error': 'Sorry, product ratings are currently unavailable for this book.'}

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)