from flask import session
from app import db
from sqlalchemy import func, desc
from app.users.models import User, Account, ExpenseList


def check_balances(current_list="new"):
    balances = {}
    total_spent = (db.session.query(func.sum(Account.spent))\
                   .filter_by(user_id=session['user_id'], list_name=current_list).first())[0]
                    
    if not total_spent: total_spent = 0.0
    balances['ts_user'] = total_spent

    user = User.query.filter_by(id=session['user_id']).first()
    
    # Get the info for Partner 1
    partner1 = User.query.filter_by(email=user.partner1_email).first()
    if partner1:
        total_spent_partner1 = (db.session.query(func.sum(Account.spent))\
                            .filter_by(user_id=partner1.id, list_name=current_list).first())[0]                  
        if not  total_spent_partner1: total_spent_partner1 = 0.0
        balances['ts_p1'] =  total_spent_partner1
        
     # Get the info for Partner 2
    partner2 = User.query.filter_by(email=user.partner2_email).first()
    if partner2:
          total_spent_partner2 = (db.session.query(func.sum(Account.spent))\
                            .filter_by(user_id=partner2.id, list_name=current_list).first())[0]
                                                  
          if not total_spent_partner2: total_spent_partner2 = 0.0
          balances['ts_p2'] =  total_spent_partner2
          
    if partner1 and not partner2:
         balances['ts'] = balances['ts_user'] + balances['ts_p1']
         if balances['ts_user'] < balances['ts_p1']:
             balances['ower'] = user.name
             balances['ower_id'] = user.id
             balances['receiver'] = partner1.name
             balances['receiver_id'] = partner1.id
             
         else:
             balances['ower'] = partner1.name
             balances['ower_id'] = partner1.id
             balances['receiver'] = user.name
             balances['receiver_id'] = user.id
         balances['amount_owned'] = 0.5 * (balances['ts_user'] - balances['ts_p1'])    
         
    elif partner1 and partner2:
         balances['ts'] = balances['ts_user'] + balances['ts_p1'] + balances['ts_p2']
        
         mean = 0.3333333*(balances['ts']) 
         diff_u = balances['ts_user'] - mean
         diff_p1 = balances['ts_p1'] - mean
         diff_p2 = balances['ts_p2'] - mean   
         
         balances['mean'] = mean
         balances['diff_u'] = diff_u
         balances['diff_p1'] = diff_p1
         balances['diff_p2'] = diff_p2
                  
         group = {user.name:diff_u, partner1.name:diff_p1, partner2.name:diff_p2}
         group_id = {user.id:diff_u, partner1.id:diff_p1, partner2.id:diff_p2}
         
         neg = [key for key in group.keys() if group[key] < 0]
         pos = [key for key in group.keys() if group[key] >= 0]
         
         neg_id = [key for key in group_id.keys() if group_id[key] < 0]
         pos_id = [key for key in group_id.keys() if group_id[key] >= 0]
         
         balances['n_owers'] = len(neg)   
             
         if balances['n_owers'] == 1:
             balances['ower'] = neg[0]
             balances['ower_id'] = neg_id[0]
             balances['amount_owed1'] = group[pos[0]]
             balances['amount_owed2'] = group[pos[1]]
             balances['receiver1'] = pos[0]
             balances['receiver1_id'] = pos_id[0]
             balances['receiver2'] = pos[1]
             balances['receiver2_id'] = pos_id[1]
             
         if balances['n_owers'] == 2:
             balances['receiver'] = pos[0]
             balances['receiver_id'] = pos_id[0]
             balances['ower1'] = neg[0]
             balances['ower2'] = neg[1]
             balances['ower1_id'] = neg_id[0]
             balances['ower2_id'] = neg_id[1]
             balances['amount_owed1'] = group[neg[0]]
             balances['amount_owed2'] = group[neg[1]] 
                        
    elif not partner1 and partner2:
         balances['ts'] = balances['ts_user'] + balances['ts_p2']
         
         if balances['ts_user'] < balances['ts_p2']:
             balances['ower'] = user.name
             balances['ower_id'] = user.id
             balances['receiver'] = partner2.name
             balances['receiver_id'] = partner2.id
         else:
             balances['ower'] = partner2.name
             balances['ower_id'] = partner2.id
             balances['receiver'] = user.name
             balances['receiver_id'] = user.id
         balances['amount_owned'] = 0.5 * (balances['ts_user'] - balances['ts_p2'])  
    else:
         balances['ts'] = balances['ts_user'] 
         balances['amount_owned'] = 0.0
         
    balances['tot'] =  balances['ts']
    return balances
    