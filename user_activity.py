from app import db
import util

def get_activity(userid):
    return db.session.execute("SELECT description, closetime FROM user_activity WHERE userid = :userid", {"userid":userid}).fetchall()

def add_activity(userid, description):
    db.session.execute("INSERT INTO user_activity (userid, description, closetime) VALUES (:userid, :description, NOW())", {"userid":userid, "description":description})