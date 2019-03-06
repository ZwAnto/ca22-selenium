import smtplib
from email.mime.text import MIMEText

def sendMail(n_obs,user,mdp):
    # set up the SMTP server
    s = smtplib.SMTP(host='smtp-mail.outlook.com', port=587)
    s.starttls()
    s.login(user, mdp)
    
    msg = MIMEText("""
    SCRAPING FINISHED: %s new observations.
    """ % (str(n_obs)))
    
    # setup the parameters of the message
    msg['From']=user
    msg['To']="antoine.hamon22@gmail.com"
    msg['Subject']="SCRAPING RESULTS"

    # send the message via the server set up earlier.
    s.send_message(msg)
