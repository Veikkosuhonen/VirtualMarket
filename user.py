from app import db
import util
import shop
import user_activity
import transaction


def get_users():
    return db.session.execute("SELECT id, username, (SELECT COUNT(userid) FROM shop_owners WHERE userid = users.id) FROM users").fetchall()


def get_public_user(name):
    u = db.session.execute("SELECT id, join_date FROM users WHERE username = :name",{"name":name}).fetchone()
    if u == None:
        return None
    userid, join_date = u
    shops = shop.get_shops_owned_by(userid)
    return  {
        "username": name,
        "userid": userid,
        "shops": shops,
        "join_date": join_date
    }


def get_private_user(name):
    userid = util.get_userid(name)
    if userid == None:
        return None
    shops = shop.get_shops_owned_by(userid)
    balance, join_date = db.session.execute("SELECT balance, join_date FROM users WHERE id = :userid",{"userid":userid}).fetchone()
    inventory = db.session.execute("""
        SELECT items.itemname, user_inventory.quantity FROM items, user_inventory
        WHERE user_inventory.userid = :userid AND user_inventory.itemid = items.id AND user_inventory.quantity > 0""",
        {"userid":userid}).fetchall()
    # Get the private profile activity stuff
    incoming_invites = db.session.execute(
        "SELECT invites.id, users.username, shops.shopname, invites.invitestatus FROM users, shops, invites WHERE users.id = invites.senderid AND shops.id = invites.shopid AND invites.receiverid = :userid",
        {"userid":userid}).fetchall()
    sent_invites = db.session.execute(
        "SELECT invites.id, users.username, shops.shopname, invites.invitestatus FROM users, shops, invites WHERE users.id = invites.receiverid AND shops.id = invites.shopid AND invites.senderid = :userid",
        {"userid":userid}).fetchall()
    pending_incoming_invites = [invite for invite in incoming_invites if invite[3] == 0]
    pending_sent_invites = [invite for invite in sent_invites if invite[3] == 0]
    activity = user_activity.get_activity(userid)
    transactions = transaction.get_transaction_activity(userid)

    return {
        "username": name,
        "userid": userid,
        "shops": shops,
        "incoming_invites": pending_incoming_invites,
        "sent_invites": pending_sent_invites,
        "balance": balance,
        "inventory": inventory,
        "activity": activity,
        "transactions": transactions,
        "join_date": join_date
    }