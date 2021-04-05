import time, datetime, webbrowser, pandas, smtplib, shutil, os.path, numpy
from importlib import reload
import stockBuysV2
import wsbScraper
import stockAnalysis
#All the sheets which are used for analysis
sheet1 = "https://docs.google.com/spreadsheets/d/e/2PACX-1vROGz7o6U1zLmzORxJg3dTSWRPF6FmSWkQvMIrxeznqQEVMebvWPuUUL21MRKsEuYIDSHtxasb_r8aF/pub?gid=0&single=true&output=csv"
sheet2 = "https://docs.google.com/spreadsheets/d/e/2PACX-1vROGz7o6U1zLmzORxJg3dTSWRPF6FmSWkQvMIrxeznqQEVMebvWPuUUL21MRKsEuYIDSHtxasb_r8aF/pub?gid=1599939664&single=true&output=csv"
sheet3 = "https://docs.google.com/spreadsheets/d/e/2PACX-1vROGz7o6U1zLmzORxJg3dTSWRPF6FmSWkQvMIrxeznqQEVMebvWPuUUL21MRKsEuYIDSHtxasb_r8aF/pub?gid=1197833442&single=true&output=csv"
sheet4 = "https://docs.google.com/spreadsheets/d/e/2PACX-1vROGz7o6U1zLmzORxJg3dTSWRPF6FmSWkQvMIrxeznqQEVMebvWPuUUL21MRKsEuYIDSHtxasb_r8aF/pub?gid=1637827314&single=true&output=csv"
sheet5 = "https://docs.google.com/spreadsheets/d/e/2PACX-1vROGz7o6U1zLmzORxJg3dTSWRPF6FmSWkQvMIrxeznqQEVMebvWPuUUL21MRKsEuYIDSHtxasb_r8aF/pub?gid=1414740708&single=true&output=csv"
sheets = [sheet1, sheet2, sheet3, sheet4, sheet5]
#open usernames and passwords for email
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
while True:
    #Gather date and time data so the program knows when to run
    timeNow = time.localtime()
    hour = timeNow.tm_hour
    minute = timeNow.tm_min
    day = datetime.datetime.today().weekday()
    #If the hours and minutes fall in this window run the program
    if hour == 12 and minute > 45 and day < 5:
        #Remove previously saved data if still there
        reload(stockAnalysis)
        try:
            shutil.rmtree("/home/pi/Documents/Background/")
            os.mkdir("/home/pi/Documents/Background/")
        except:
            pass
        #EMail that it started
        subject = "Started Effectively"
        body = "Background stock program started. Previous stock data:\n" + stockAnalysis.message
        smtp_server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        smtp_server.login(sender_address, account_password)
        message = f"Subject: {subject}\n\n{body}"
        smtp_server.sendmail(sender_address, receiver_address, message)
        smtp_server.close()
        #Run stock program
        reload(stockBuysV2)
        try:
            reload(wsbScraper)
        except:
            pass
        time.sleep(1000)
    #pauses program      
    boughtedGuys = stockBuysV2.buyGuysO
    boughtGuys = boughtedGuys.strip(" ")
    if hour > 6 and hour < 12:
#Early processing of string
        splitGuys = boughtGuys.split()
        downloadSuccessful = True
#Open the sheets
        for k in range(5):
            webbrowser.open(sheets[k])
#see if they opened
            tic = time.time()
            while not os.path.isfile("/home/pi/Downloads/stockData - Sheet" + str(k+1) + ".csv"):
                toc = time.time() - tic
                if toc > 10:
                    downloadSuccessful = False
                    break
                else:
                    continue
#if the download was successful process data
        if downloadSuccessful:
            stock = "SPY"
            placeIn = 0
            sheetNumber = 1
            currentDataSheet = pandas.read_csv("/home/pi/Downloads/stockData - Sheet" + str(sheetNumber) + ".csv")
            currentVals = currentDataSheet.loc[:,"Price"]
            priceNow = currentVals[placeIn]
            stockRNTable = pandas.read_csv("/home/pi/Documents/Background/" + stock + "/" + stock + ".csv")
            stockArray = stockRNTable.loc[:,"0"]
            shutil.rmtree("/home/pi/Documents/Background/" + stock + "/")
            try:
                os.mkdir("/home/pi/Documents/Background/" + stock + "/")
            except:
                pass
            newStockPrices = numpy.append(stockArray, priceNow)
            data_frame = pandas.DataFrame(data=newStockPrices)
            data_frame.to_csv("/home/pi/Documents/Background/" + stock + "/" + stock + ".csv")
            for g in range(len(splitGuys)):
                stockFirst = splitGuys[g].split(";")
                stock = stockFirst[0]
                position = stockFirst[1].split(",")
                sheetNumber = position[0]
                placeIn = int(position[1])
                currentDataSheet = pandas.read_csv("/home/pi/Downloads/stockData - Sheet" + sheetNumber + ".csv")
                currentVals = currentDataSheet.loc[:,"Price"]
                priceNow = currentVals[placeIn]
                stockRNTable = pandas.read_csv("/home/pi/Documents/Background/" + stock + "/" + stock + ".csv")
                stockArray = stockRNTable.loc[:,"0"]
                shutil.rmtree("/home/pi/Documents/Background/" + stock + "/")
                try:
                    os.mkdir("/home/pi/Documents/Background/" + stock + "/")
                except:
                    pass
                newStockPrices = numpy.append(stockArray, priceNow)
                data_frame = pandas.DataFrame(data=newStockPrices)
                data_frame.to_csv("/home/pi/Documents/Background/" + stock + "/" + stock + ".csv")
    try:
        shutil.rmtree("/home/pi/Downloads/")
    except:
        pass
    time.sleep(300)