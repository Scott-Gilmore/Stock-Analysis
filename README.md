# Stock-Analysis
Some python files I have written as a hobby to do some basic analysis of the stock market.
The file stockBuys.py is a code written to do data processing on google sheets csvs and NASDAQ csvs. I applied my own parameters for what would constitute buying a stock at
the end of the day and selling it the next for profit. The outputs of the code are emails containing the ticker symbol to buy as well as failure emails if something goes
wrong.
I run the backgroundStock.py file in a loop on a raspberry pi and each day at around 12:30 in will re-run the file stockBuys.py file to email me that days buyers. The 
backgroundStock.py file also contains code to pull prices of the previously bought stocks data which will allow me to analyze any trends that may exist.
