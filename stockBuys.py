#Try so that in the case of failure the higher level program will continue to run
try:
#import tools that will be used
    import pandas, webbrowser, os.path, time, shutil, numpy, csv, traceback, sys, smtplib
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
    sheetOrder = [4, 2, 5, 1, 3]
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
#Cycle through the sheets
    for o in sheetOrder:
        try:
            os.system("pkill chromium")
        except:
            pass
        try:
            shutil.rmtree("/home/pi/Downloads/")
        except:
            pass
#begin to download SPY and google sheets
        webbrowser.open(sheets[o-1])
        webbrowser.open("https://www.nasdaq.com/api/v1/historical/SPY/etf/" + pastDay + "/" + currentDay)
        tic = time.time()
#Check to see if the google sheet has properly uploaded
        while not os.path.isfile("/home/pi/Downloads/stockData - Sheet" + str(o) + ".csv"):
            toc = time.time() - tic
            if toc > 10:
                break
            else:
                continue
#Check to see if spy historical data has downloaded correctly
        while not os.path.isfile("/home/pi/Downloads/HistoricalQuotes.csv"):
            toc = time.time() - tic
            if toc > 10:
                break
            else:
                continue
#Read spy .csv file
        fail = False
        try:
            spyData = pandas.read_csv("/home/pi/Downloads/HistoricalQuotes.csv")
            spyCloseArray = spyData.loc[:," Close/Last"]
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
            data_frame.columns = [" Close/Last"]
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
        yearVal = numpy.mean(spyCloseArray[247:])
        annualIncrease = currentVals[0] - yearVal
        spyAnnualGrowth = annualIncrease/yearVal
        monthVal = numpy.mean(spyCloseArray[20:24])
        monthlyIncrease = currentVals[0] - monthVal
        spyMonthlyGrowth = monthlyIncrease/monthVal
        weekVal = spyCloseArray[4]
        weeklyIncrease = currentVals[0] - weekVal
        spyWeeklyGrowth = weeklyIncrease/weekVal
        dayVal = spyCloseArray[0]
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
        for t in range(0,(len(stockNames))):
#When t is zero we just download, no comparisons yet
            if t == 0:
                d = d + 1
                placeIn = d
                webDownload = "https://www.nasdaq.com/api/v1/historical/" + stockNames[d] + "/stocks/" + pastDay + "/" + currentDay
                webbrowser.open(webDownload)
                fileNames = "HistoricalQuotes (" + str(placeIn) + ").csv"
#When t is in that range the stock previously downloaded will be checked for existence and processed. Meanwhile a new download will begin
            elif t <= (len(stockNames)-2):
#d is used for current download placeIn for previous
                d = d + 1
                placeIn = d - 1
#Check to see if download worked on previos run through. If not create an empty file to replace it
                tac = time.time()
                while not os.path.isfile("/home/pi/Downloads/HistoricalQuotes (" + str(placeIn) + ").csv"):
                    tec = time.time() - tac
                    if tec > 10:
                        mydata = [0,0,0,0,0,0,0,0,0,0,0,0]
                        data_frame = pandas.DataFrame(data=mydata)
                        data_frame.to_csv("/home/pi/Downloads/HistoricalQuotes (" + str(placeIn) + ").csv")
                        break
                    else:
                        continue
#Download data to be analyzed on the next cycle
                webDownload = "https://www.nasdaq.com/api/v1/historical/" + stockNames[d] + "/stocks/" + pastDay + "/" + currentDay
                webbrowser.open(webDownload)
#Try to read the file and do math on it
                fileNames = "HistoricalQuotes (" + str(placeIn) + ").csv"
                try:
                    currentStockTable = pandas.read_csv("/home/pi/Downloads/HistoricalQuotes (" + str(placeIn) + ").csv")
                    closeArray = currentStockTable.loc[:," Close/Last"]
#Define variables for comparison with spy
                    sumYear = 0
                    sumMonth = 0
                    for s in range(len(closeArray)-5,len(closeArray)):
                        indString = closeArray[s]
                        indNum = float(indString[2:])
                        sumYear = sumYear + indNum
                    yearVal = sumYear/5
                    annualIncrease = currentVals[placeIn] - yearVal
                    annualGrowth = annualIncrease/yearVal
                    for p in range(20,24):
                        monString = closeArray[p]
                        monNum = float(monString[2:])
                        sumMonth = sumMonth + monNum
                    monthVal = sumMonth/4
                    monthlyIncrease = currentVals[placeIn] - monthVal
                    monthlyGrowth = monthlyIncrease/monthVal
                    weekString = closeArray[4]
                    weekVal = float(weekString[2:])
                    weeklyIncrease = currentVals[placeIn] - weekVal
                    weeklyGrowth = weeklyIncrease/weekVal
                    dayString = closeArray[0]
                    dayVal = float(dayString[2:])
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

#If on the last number there is no download required just comparison
            else:
                d = d + 1
                placeIn = d - 1
                tac = time.time()
#Check to see if the file exists
                while not os.path.isfile("/home/pi/Downloads/HistoricalQuotes (" + str(placeIn) + ").csv"):
                    tec = time.time() - tac
                    if tec > 10:
                        mydata = [0,0,0,0,0,0,0,0,0,0,00,0,0,0]
                        data_frame = pandas.DataFrame(data=mydata)
                        data_frame.to_csv("/home/pi/Downloads/HistoricalQuotes (" + str(placeIn) + ").csv")  
                        break
                    else:
                        continue
#Process file, try in case of failure
                fileNames = "HistoricalQuotes (" + str(placeIn) + ").csv"
                try:
                    currentStockTable = pandas.read_csv("/home/pi/Downloads/HistoricalQuotes (" + str(placeIn) + ").csv")
                    closeArray = currentStockTable.loc[:," Close/Last"]
#Do the data massaging to get into comparison form
                    sumYear = 0
                    sumMonth = 0
                    for s in range(len(closeArray)-5,len(closeArray)):
                        indString = closeArray[s]
                        indNum = float(indString[2:])
                        sumYear = sumYear + indNum
                    yearVal = sumYear/5
                    annualIncrease = currentVals[placeIn] - yearVal
                    annualGrowth = annualIncrease/yearVal
                    for p in range(20,24):
                        monString = closeArray[p]
                        monNum = float(monString[2:])
                        sumMonth = sumMonth + monNum
                    monthVal = sumMonth/4
                    monthlyIncrease = currentVals[placeIn] - monthVal
                    monthlyGrowth = monthlyIncrease/monthVal
                    weekString = closeArray[4]
                    weekVal = float(weekString[2:])
                    weeklyIncrease = currentVals[placeIn] - weekVal
                    weeklyGrowth = weeklyIncrease/weekVal
                    dayString = closeArray[0]
                    dayVal = float(dayString[2:])
                    dailyIncrease = currentVals[placeIn] - dayVal
                    dailyGrowth = dailyIncrease/dayVal
#Do comparisons to spy
                    buyScore = 0
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
                        try:
                            os.mkdir("/home/pi/Documents/Background/" + stockNames[placeIn] + "/")
                        except:
                            pass
                        mydata = [currentVals[placeIn]]
                        data_frame = pandas.DataFrame(data=mydata)
                        data_frame.to_csv("/home/pi/Documents/Background/" + stockNames[placeIn] + "/" + stockNames[placeIn] + ".csv")
                except:
                    failedStocks = failedStocks + stockNames[placeIn] + " " 
                    pass
#Send an early email if on the third run of the loop
                if o == sheetOrder[2] or o == sheetOrder[3]:
                    subject = "Preliminary Stocks"
                    earlyGuys = ""
                    failedEarly = ""
                    try:
                        earlyGuys = buyGuys.strip() + ". "
                    except:
                        pass
                    try:
                        failedEarly = failedStocks.strip()
                    except:
                        pass
                    body = earlyGuys + "Failed stocks dont buy " + failedEarly + "."
                    body = body.strip(". ") + "."
                    smtp_server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
                    smtp_server.login(sender_address, account_password)
                    message = f"Subject: {subject}\n\n{body}"
                    smtp_server.sendmail(sender_address, receiver_address, message)
                    smtp_server.close()
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