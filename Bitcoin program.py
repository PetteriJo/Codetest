import json
import urllib.request
import time
import datetime


def guide():
    print("You have two options:")
    print("0: Quit")
    print("1: Explore bitcoin within your date range")
    print()


def ask_dates():
    while True:
        try:
            first_date = input("Please give starting date (yyyy.mm.dd): ")
            first_unix = convert_to_unix(first_date)
        except ValueError:
            print("Incorrect input, please try again.")
            continue
        except IndexError:
            print("Incorrect input, please try again.")
            continue
        except OverflowError:
            print("Incorrect input, please try again.")
            continue

        while True:
            try:
                last_date = input("Please give last date (yyyy.mm.dd): ")
                last_unix = convert_to_unix(last_date)
            except ValueError:
                print("Incorrect input, please try again.")
                continue
            except IndexError:
                print("Incorrect input, please try again.")
                continue
            except OverflowError:
                print("Incorrect input, please try again.")
                continue

            return first_unix, last_unix
            

def convert_to_unix(date):
    date1 = (date.split("."))
    year = int(date1[0])
    month = int(date1[1])
    day = int(date1[2])
    date2 = datetime.date(year, month, day)
    unixtime = int(time.mktime(date2.timetuple()))
    return unixtime


def bearish(unix1, database):
    """Gives longest downward trend for bitcoin"""
    longest_trend = 0
    streak = 0
    last_price = 0
    start = unix1 * 1000

    for unix, price in database["prices"]:
        if unix >= start:   #this ensures that only data from as close to midnight as possible as the day’s price is used
            if price <= last_price:
                streak += 1
            else:   #cuts the streak and checks if the current streak is longer than longest trend
                if streak > longest_trend:
                    longest_trend = streak
                streak = 0

            last_price = price
            start += 24 * 60 * 60 * 1000    #adds milliseconds worth full day
            
    if streak > longest_trend:  #checks if longest trend was ongoing at the end
        longest_trend = streak

    if longest_trend > 1:
        print(f"Within a given date range the longest bearish trend was {longest_trend} days.")
    elif longest_trend == 1:
        print(f"Within a given date range the longest bearish trend was {longest_trend} day.")
    else:
        print(f"Within a given date range the price of bitcoin only went up.")


def highest_volume(unix1, database):
    """Gives the day of highest trading volume"""
    highest = 0
    highest_unix = 0
    start = unix1 * 1000

    for unix, volume in database["total_volumes"]:
        if unix >= start:   #this ensures that only data from as close to midnight as possible as the day’s price is used
            if volume > highest:    #checks if days volume is higher than highest volume and saves the timestamp
                highest = volume
                highest_unix = unix
            
            start += 24 * 60 * 60 * 1000    #adds milliseconds worth full day
    
    highest_date = datetime.date.fromtimestamp(highest_unix / 1000)
    print(f"Within a given date range {highest_date} had the highest trading volume.")


def time_travel(unix1, database):
    """Gives two dates: date you should buy bitcoins and day you should sell your bitcoins"""
    biggest_difference = 0
    last_price = 0
    start = unix1 * 1000
    unix_buy = 0
    unix_sell = 0
    increasing = False

    for unix, price in database["prices"]:
        if unix >= start:   #checks if the data of the price is first of the day
            if last_price == 0:     #checks if there is no yesterdays price to compare
                last_price = price
            else:
                if price > last_price:  #checks if price is greater than yesterday's price 
                    if increasing == False:     #if True then no need to compare
                        start2 = unix
                        highest_price = 0
                        unix_highest = 0
                        for compare_unix, compare_price in database["prices"]:      #checks every low point and compares it to the highest point of following days
                            if compare_unix >= start2:   #checks comparable prices only after considered low point 
                                if compare_price > highest_price:   
                                    highest_price = compare_price
                                    unix_highest = compare_unix

                                start2 += 24 * 60 * 60 * 1000

                        difference = highest_price - last_price

                        if difference > biggest_difference:     #checks if price difference is bigger than biggest difference and saves the timestamps
                            biggest_difference = difference
                            unix_buy = unix - 24 * 60 * 60 * 1000
                            unix_sell = unix_highest

                        increasing = True
                else:
                    increasing = False

            last_price = price
            start += 24 * 60 * 60 * 1000

    if biggest_difference == 0: #if bitcoin's value only decreases
        print("Your time machine is worthless within a given date range")
    else:
        date_buy = datetime.date.fromtimestamp(unix_buy / 1000)
        date_sell = datetime.date.fromtimestamp(unix_sell / 1000)
        print(f"Within a given date range you should buy {date_buy} and sell {date_sell}. Your profit per bought/sold bitcoin would be {biggest_difference:.2f} €. ")


def explore():
    while True:
        first_unix, last_unix = ask_dates()
        request = urllib.request.urlopen(f"https://api.coingecko.com/api/v3/coins/bitcoin/market_chart/range?vs_currency=eur&from={first_unix}&to={last_unix+3600}")
        data = json.loads(request.read())

        if first_unix >= last_unix: #First date can't be same or later than last date
            print("Choose different days.")
        else:
            break
    print("**********************************************")
    bearish(first_unix, data)
    print("*")
    highest_volume(first_unix, data)
    print("*")
    time_travel(first_unix, data)
    print("***********************************")
    print("I hope this information helped you.")
    print("***********************************")

def main():
    print()
    print("Welcome to my bitcoin program!")
    print("------------------------------")
    while True:
        guide()
        command = input("What do you want to do? (Please give 0 or 1): ")

        if command == "0":
            break
        elif command == "1":
            explore()

main()
