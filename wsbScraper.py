import praw, collections
import pandas as pd
import datetime as dt
#Get passwords for access to reddit data
text_file_red = open("/home/pi/Documents/redditPwords.txt", "r")
redditPwordPre = text_file_red.readlines()
redditPword = redditPwordPre[0].split()
redditPword = redditPword[0].split(",")
text_file_red.close()
#access the praw module to use its functions
reddit = praw.Reddit(client_id=redditPword[0], client_secret=redditPword[1],user_agent=redditPword[2])
#Put data from wsb into an array
subreddit = reddit.subreddit("WallStreetBets")
topSub = subreddit.hot(limit=1000)
topics_dict = {"title":[], \
               "score":[], \
               "comms_num": [], \
               "body":[]}
tickerArray = []
#go through the submissions and do some processing
for submission in topSub:
    topics_dict["title"].append(submission.title)
    topics_dict["score"].append(submission.score)
    topics_dict["comms_num"].append(submission.num_comments)
    topics_dict["body"].append(submission.selftext)
topics_data = pd.DataFrame(topics_dict)
titles = topics_data.loc[:,"title"]
uppers = ""
tickerArray = []
#dont include accesses a file that has blacklisted words
text_file = open("/home/pi/Documents/blacklist.txt", "r")
dontIncludePre = text_file.readlines()
dontInclude = dontIncludePre[0].split()
dontInclude = dontInclude[0].split(",")
text_file.close()
#The embedded loops are used to iterate through titles and find ticker symbols
for h in range(0,len(titles)):
    title = titles[h]
    uppers = ' '
    for g in range(0,len(title)):
        if title[g].isupper() or title[g].isspace():
            uppers = uppers + title[g]
    try:
        uppers = uppers.strip()
        buppers = uppers.split()
    except:
        pass
    for u in range(0, len(buppers)):
        for k in range(0, len(dontInclude)):
            if buppers[u] == dontInclude[k]:
                buppers[u]=[]
        if len(buppers[u]) < 5 and len(buppers[u]) > 1:
            tickerArray += buppers[u].split()
tickersToCount = (word for word in tickerArray)
#find the most commonly occuring ticker symbols
c = collections.Counter(tickersToCount)
common = c.most_common(30)
body = ""
for f in range(0,30):
    currentGuy = common[f]
    name = currentGuy[0]
    num = str(currentGuy[1])
    body = body + name + " " + num + "\n"
#email me the data
import smtplib
text_file_user = open("/home/pi/Documents/username.txt", "r")
sender_addressPre = text_file_user.readlines()
sender_address = sender_addressPre[0].split()
sender_address = sender_address[0]
text_file_user.close()
text_file_pword = open("/home/pi/Documents/password.txt", "r")
account_passwordPre = text_file_pword.readlines()
account_password = account_passwordPre[0].split()
account_password = account_password[0]
text_file_pword.close()
receiver_address = sender_address
subject = "Reddit Stocks"
smtp_server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
smtp_server.login(sender_address, account_password)
message = f"Subject: {subject}\n\n{body}"
smtp_server.sendmail(sender_address, receiver_address, message)
smtp_server.close()