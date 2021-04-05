#Try so that in the case of failure the higher level program will continue to run
try:
#import tools that will be used
    import pandas, webbrowser, os.path, time, shutil, numpy, csv, traceback, sys, smtplib, requests
#Recieve date so that data can be downloaded
    from datetime import date
    currentDay = str(date.today())
    yearString = str(int(currentDay[:4]) - 1)
    pastDay = yearString[:] + currentDay[4:]
#URL's for the sheets with current stock data
    sheet1 = "https://docs.google.com/spreadsheets/d/e/2PACX-1vROGz7o6U1zLmzORxJg3dTSWRPF6FmSWkQvMIrxeznqQEVMebvWPuUUL21MRKsEuYIDSHtxasb_r8aF/pub?gid=0&single=true&output=csv"
    sheet2 = "https://docs.google.com/spreadsheets/d/e/2PACX-1vROGz7o6U1zLmzORxJg3dTSWRPF6FmSWkQvMIrxeznqQEVMebvWPuUUL21MRKsEuYIDSHtxasb_r8aF/pub?gid=1599939664&single=true&output=csv"
    sheet3 = "https://docs.google.com/spreadsheets/d/e/2PACX-1vROGz7o6U1zLmzORxJg3dTSWRPF6FmSWkQvMIrxeznqQEVMebvWPuUUL21MRKsEuYIDSHtxasb_r8aF/pub?gid=1197833442&single=true&output=csv"
    sheet4 = "https://docs.google.com/spreadsheets/d/e/2PACX-1vROGz7o6U1zLmzORxJg3dTSWRPF6FmSWkQvMIrxeznqQEVMebvWPuUUL21MRKsEuYIDSHtxasb_r8aF/pub?gid=1637827314&single=true&output=csv"
    sheet5 = "https://docs.google.com/spreadsheets/d/e/2PACX-1vROGz7o6U1zLmzORxJg3dTSWRPF6FmSWkQvMIrxeznqQEVMebvWPuUUL21MRKsEuYIDSHtxasb_r8aF/pub?gid=1414740708&single=true&output=csv"
    sheets = [sheet1, sheet2, sheet3, sheet4, sheet5]
    sheetOrder = [4,2,5,1,3]
    buyGuys = ""
    failedStocks = ""
    buyGuysO = ""
#Get user and pword from txt file for security
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
    text_file_key = open("/home/pi/Documents/apitoken.txt", "r")
    sender_keyPre = text_file_key.readlines()
    apiKey = sender_keyPre[0].split()
    apiKey = apiKey[0]
    text_file_key.close()
    headers = {
        'Content-Type': 'application/csv',
        'Authorization' : 'Token ' + apiKey
        }
#Cycle through the sheets
    for o in sheetOrder:
        try:
            os.system("pkill chromium")
        except:
            pass
        try:
            shutil.rmtree("/home/pi/Downloads/")
            os.mkdir("/home/pi/Downloads/")
        except:
            pass
#begin to download SPY and google sheets
        webbrowser.open(sheets[o-1])
        spyRequest = requests.get("https://api.tiingo.com/tiingo/daily/SPY/prices?startDate="+pastDay+"&endDate="+currentDay+"&format=csv&resampleFreq=daily", headers = headers)
        tic = time.time()
#Check to see if the google sheet has properly uploaded
        while not os.path.isfile("/home/pi/Downloads/stockData - Sheet" + str(o) + ".csv"):
            toc = time.time() - tic
            if toc > 20:
                break
            else:
                continue
#Check to see if spy historical data has downloaded correctly
#Read spy .csv file
        fail = False
        try:
            spyText = spyRequest.text
            spyTXT = open('/home/pi/Downloads/spy.txt','a')
            spyTXT.write(spyText)
            spyTXT.close()
            spy_read = pandas.read_csv(r'/home/pi/Downloads/spy.txt')
            spyCloseArray = spy_read.loc[:,"close"] 
        except:
            subject = "SPY Failure"
            body = "Spy download failed on pass " + str(o)
            smtp_server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
            smtp_server.login(sender_address, account_password)
            message = f"Subject: {subject}\n\n{body}"
            smtp_server.sendmail(sender_address, receiver_address, message)
            smtp_server.close()
            mydata = [0,1,2,4,8,16,32,64,128,256]
            data_frame = pandas.DataFrame(data=mydata)
            data_frame.columns = ["close"]
            data_frame.to_csv("/home/pi/Downloads/HistoricalQuotes.csv")
            fail = True
            pass
        if fail:
            continue
# Read google sheet and do some processing
        try:
            sheetNum = str(o)
            sheetNumber = "/home/pi/Downloads/stockData - Sheet" + sheetNum + ".csv"
            stockNames1 = pandas.read_csv(sheetNumber)
            currentVals = stockNames1.loc[:,"Price"]
            stockNames1 = pandas.read_csv(sheetNumber)
            stockNames = stockNames1.loc[:,"Ticker"]
        except:
            subject = "Sheet Failure"
            body = "Current data download failed on pass " + str(o)
            smtp_server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
            smtp_server.login(sender_address, account_password)
            message = f"Subject: {subject}\n\n{body}"
            smtp_server.sendmail(sender_address, receiver_address, message)
            smtp_server.close()
            pass
        if fail:
            continue
#process the spy data
        yearVal = numpy.mean(spyCloseArray[0:4])
        annualIncrease = currentVals[0] - yearVal
        spyAnnualGrowth = annualIncrease/yearVal
        monthVal = numpy.mean(spyCloseArray[len(spyCloseArray)-25:len(spyCloseArray-21)])
        monthlyIncrease = currentVals[0] - monthVal
        spyMonthlyGrowth = monthlyIncrease/monthVal
        weekVal = spyCloseArray[len(spyCloseArray)-5]
        weeklyIncrease = currentVals[0] - weekVal
        spyWeeklyGrowth = weeklyIncrease/weekVal
        dayVal = spyCloseArray[len(spyCloseArray)-1]
        dailyIncrease = currentVals[0] - dayVal
        spyDailyGrowth = dailyIncrease/dayVal
#Inform me through email if spy growth has been 0
        if (spyDailyGrowth == 0) and o == sheetOrder[0]:
            subject = "Somethings Fishy"
            body = "Daily growth of spy is zero, google sheet probably didn't update."
            smtp_server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
            smtp_server.login(sender_address, account_password)
            message = f"Subject: {subject}\n\n{body}"
            smtp_server.sendmail(sender_address, receiver_address, message)
            smtp_server.close()
 # for comparison purposes
        monthToYearMultiplier = spyAnnualGrowth/spyMonthlyGrowth
        dayToMonthMultiplier = spyMonthlyGrowth/spyDailyGrowth
        dayToWeekMultiplier = spyWeeklyGrowth/spyDailyGrowth
#Define d and start a for loop that will loop through downloads for each stock   
        d = 0
        for t in range(0,(len(stockNames)-1)):
#When t is zero we just download, no comparisons yet
            d = d + 1
            placeIn = d
            webDownload = "https://api.tiingo.com/tiingo/daily/" + stockNames[d] + "/prices?startDate=" + pastDay +"&endDate=" + currentDay+ "&format=csv&resampleFreq=daily"
            currentRequest = requests.get(webDownload, headers = headers)
            currentText = currentRequest.text
            fileName = "prices (" + str(placeIn) + ")"
#When t is in that range the stock previously downloaded will be checked for existence and processed. Meanwhile a new download will begin
            try:
                directory = '/home/pi/Downloads/'+ fileName +'.txt'
                currentTXT = open(directory,'a')
                currentTXT.write(currentText)
                currentTXT.close()
                current_read = pandas.read_csv(r'/home/pi/Downloads/'+ fileName +'.txt')
                closeArray = current_read.loc[:,"close"]
#Define variables for comparison with spy
                yearVal = numpy.mean(closeArray[0:4])
                annualIncrease = currentVals[placeIn] - yearVal
                annualGrowth = annualIncrease/yearVal
                monthVal = numpy.mean(closeArray[len(closeArray)-25:len(closeArray)-21])
                monthlyIncrease = currentVals[placeIn] - monthVal
                monthlyGrowth = monthlyIncrease/monthVal
                weekVal = closeArray[len(closeArray)-5]
                weeklyIncrease = currentVals[placeIn] - weekVal
                weeklyGrowth = weeklyIncrease/weekVal
                dayVal = closeArray[len(closeArray)-1]
                dailyIncrease = currentVals[placeIn] - dayVal
                dailyGrowth = dailyIncrease/dayVal
#In the case of an exception add the stock to failed stocks so I know it failed
                buyScore = 0
#Comparisons to determine buyability
                if spyAnnualGrowth < annualGrowth:
                    buyScore = buyScore + 1
                if spyMonthlyGrowth < monthlyGrowth:
                    buyScore = buyScore + 1
                if spyDailyGrowth > dailyGrowth:
                    buyScore = buyScore + 1
                if (annualGrowth > (monthlyGrowth*monthToYearMultiplier)):
                    buyScore = buyScore + 1
                if (monthlyGrowth > (dailyGrowth*dayToMonthMultiplier)):
                    buyScore = buyScore + 1
                if spyWeeklyGrowth < weeklyGrowth:
                    buyScore = buyScore + 1
                if (weeklyGrowth > (dailyGrowth*dayToWeekMultiplier)):
                    buyScore = buyScore + 1
                if buyScore == 7:
                    buyGuys = buyGuys + stockNames[placeIn] + " "
                    buyGuysO = buyGuysO + stockNames[placeIn] + ";" + str(o) + "," + str(placeIn) + " "
                    mydata = [currentVals[placeIn]]
                    data_frame = pandas.DataFrame(data=mydata)
                    try:
                        os.mkdir("/home/pi/Documents/Background/" + stockNames[placeIn] + "/")
                    except:
                        pass
                    data_frame.to_csv("/home/pi/Documents/Background/" + stockNames[placeIn] + "/" + stockNames[placeIn] + ".csv")
            except:
                failedStocks = failedStocks + stockNames[placeIn] + " "
                pass
    mydata = [currentVals[0]]
    data_frame = pandas.DataFrame(data=mydata)
    try:
        os.mkdir("/home/pi/Documents/Background/" + stockNames[0] + "/")
    except:
        pass
    data_frame.to_csv("/home/pi/Documents/Background/" + stockNames[0] + "/" + stockNames[0] + ".csv")
#Put the whole thing in a try so when it inevitably failed it'll tell me so
except Exception as e:
    print(e)
    exc_type, exc_value, exc_traceback = sys.exc_info()
    line = exc_traceback.tb_lineno
    print(str(line))
    try:
        subject = "Something Went Wrong"
        body = "Something went wrong in the overall code. Try to diagnose. " + str(e) + ". Line " + str(line)
        smtp_server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        smtp_server.login(sender_address, account_password)
        message = f"Subject: {subject}\n\n{body}"
        smtp_server.sendmail(sender_address, receiver_address, message)
        smtp_server.close()
    except:
        pass
    try:
        shutil.rmtree("/home/pi/Downloads/")
    except:
        pass
    pass
#Send email at end with all stocks
try:
    subject = "Todays Stocks"
    buyGuys = buyGuys.strip() + ". "
    failedStocks = failedStocks.strip()
    body = buyGuys + "Failed stocks dont buy " + failedStocks + "."
    body = body.strip(". ") + "."
    smtp_server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    smtp_server.login(sender_address, account_password)
    message = f"Subject: {subject}\n\n{body}"
    smtp_server.sendmail(sender_address, receiver_address, message)
    smtp_server.close()
except Exception as e:
    print(e)
    exc_type, exc_value, exc_traceback = sys.exc_info()
    line = exc_traceback.tb_lineno
    print(str(line))
    pass