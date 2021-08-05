import flask, json, time
from duco_api import Wallet
from flask_cors import cross_origin
global lastclaim

print("Connecting to DUCO server...")
duco = Wallet()
print("Connected !")

faucetuser = "peer" # faucet's username
faucetpassword = "junu12345" # faucet's password
pathToClaimTimes = "ducofaucetclaims.json" # path to the file that stores claims



claimTime = 1 # claim time expressed in hours
faucetclaim = 1 # claim amount

lastclaim = {} # user's last claim

duco.login(username=faucetuser, password=faucetpassword) # it will just login lol

print(f"Faucet balance : {duco.get_balance()}") # prints faucet's balance for display reasons

app = flask.Flask(__name__)
app.config["DEBUG"] = False


def couldClaim(username):
    try:
        _lastclaim = lastclaim[username]
    except Exception as e:
        print(e)
        _lastclaim = 0
    print(_lastclaim)
    return (int(time.time()) - _lastclaim) >= (claimTime*3600)

def loadLastClaims():
    global lastclaim
    claimTimesFile = open(pathToClaimTimes, "r")
    lastclaim = json.loads(claimTimesFile.read())
    claimTimesFile.close()


def saveLastClaims():
    claimTimesFile = open(pathToClaimTimes, "w")
    claimTimesFile.write(str(lastclaim).replace("'", "\""))
    claimTimesFile.close()


loadLastClaims()

@app.route("/claim/<username>")
@cross_origin()
def claim(username):
    ableToClaim = couldClaim(username)

    if ableToClaim:
        feedback = duco.transfer(recipient_username=username, amount=faucetclaim)
        try:
            if feedback.split(",")[0] == "YES":
                lastclaim[username] = int(time.time())
                saveLastClaims()            
                print(f"Gave {faucetclaim} to @{username}")        
                return f"You got {faucetclaim} duinos :D"
            
            elif feedback.split(",")[0] == "IDK":
                print(f"Gave {faucetclaim} duinos to @{username}, but unable to retrieve tx.")        
                return "Couldn't figure if tx was successful. You have one more claim :D"
                
            else:
                print(f"Error while giving {faucetclaim} to @{username}")
                return "Error transferring DUCO, please try again later !"
        except IndexError:
            print(f"Error while transferring {faucetclaim} duinos to @{username}")
            return "Error transferring DUCO, please try again later !"
    else:
        print(f"@{username} already claimed faucet")
        return f"@{username} already claimed faucet, didn't give anything"

@app.route("/timebeforeclaim/<username>")
@cross_origin()
def timebeforeclaim(username):
    return (int(time.time()) - _lastclaim) - (claimTime*3600)



app.run(host='0.0.0.0', port=5000)