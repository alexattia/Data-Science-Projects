import glob
import numpy as np
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import formataddr
import smtplib
import config_downl
from download_pics import internet_on
import datetime
import sys

def get_picture():
    pic_folder = '/Users/alexandreattia/Desktop/Work/machine_learning_flashcards_v1.4/png_web/'
    pics = glob.glob(pic_folder + '*')
    pic = np.random.choice(pics)
    flashcard_title = pic.split('/')[7].replace('_web.png', '').replace('_', ' ')
    return pic, flashcard_title

def send_email(flashcard_title, pic):
    """
    Send an email of with the picture of the day
    """
    # Create e-mail Multi Part
    msgRoot = MIMEMultipart('related')
    msgRoot['From'] = formataddr((str(Header('ML Flashcards', 'utf-8')), C.my_email_address))
    msgRoot['To'] = C.dest
    msgRoot['Subject'] = 'Today ML Flashcard : %s' % flashcard_title.title()
    msgAlternative = MIMEMultipart('alternative')
    msgRoot.attach(msgAlternative)

    # Create e-mail message
    msg = C.intro + C.message_init.format(flashcard_title=flashcard_title.title())
    msg += C.flashcard
    message = MIMEText(msg, 'html')
    msgAlternative.attach(message)
    
    # Add picture to e-mail
    fp = open(pic, 'rb')
    msgImage = MIMEImage(fp.read())
    fp.close()

    # Define the image's ID as referenced above
    msgImage.add_header('Content-ID', '<image1>')
    msgRoot.attach(msgImage)

    msg_full = msgRoot.as_string()
    
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login(C.my_email_address, C.password)
    server.sendmail(C.my_email_address, C.dest, msg_full)
    server.quit()
    print('%s - E-mail sent!' % datetime.datetime.now().strftime('%d/%m/%Y - %H:%M'))

if __name__ == '__main__':
    # config file with mail content, email addresses
    C = config_downl.Config()
    # Loop until there is a network connection
    time_slept = 0
    while not internet_on():
        time.sleep(1)
        time_slept += 1
        if time_slept > 15 : 
            print('%s - No network connection' % datetime.datetime.now().strftime('%d/%m/%Y - %H:%M'))
            sys.exit()
    p, fc = get_picture()
    send_email(fc, p)
