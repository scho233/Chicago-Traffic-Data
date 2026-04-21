#
# Samuel Cho
# This program connects to a database that searches information the user wants to see in terms of traffic cameras
# Users can also view a visual representation of data in some of the options
#
import sqlite3
import matplotlib.pyplot as plt
from datetime import datetime

##################################################################  
#
# print_stats
#
# Given a connection to the database, executes various
# SQL queries to retrieve and output basic stats.
#
def print_stats(dbCursor):
    print("General Statistics:")
    
    # Count of Red Light Cams
    dbCursor.execute("SELECT COUNT(*) FROM RedCameras;")
    row = dbCursor.fetchone()
    print("  Number of Red Light Cameras:", f"{row[0]:,}")

    # Count of Speed Cams
    dbCursor.execute("SELECT COUNT(*) FROM SpeedCameras;")
    row = dbCursor.fetchone()
    print("  Number of Speed Cameras:", f"{row[0]:,}")

    # Count of Red Light Violations
    dbCursor.execute("SELECT COUNT(*) FROM RedViolations;")
    row = dbCursor.fetchone()
    print("  Number of Red Light Camera Violation Entries:", f"{row[0]:,}")

    # Count of Speed Cam Violations
    dbCursor.execute("SELECT COUNT(*) FROM SpeedViolations;")
    row = dbCursor.fetchone()
    print("  Number of Speed Camera Violation Entries:", f"{row[0]:,}")

    # Date Range
    dbCursor.execute("SELECT MIN(Violation_Date), MAX(Violation_Date) FROM RedViolations;")
    row = dbCursor.fetchone()
    print("  Range of Dates in the Database:", f"{row[0]} - {row[1]}")

    # Total Red Light Violations
    dbCursor.execute("SELECT SUM(Num_Violations) FROM RedViolations;")
    row = dbCursor.fetchone()
    print("  Total Number of Red Light Camera Violations:", f"{row[0]:,}")

    # Total Speed Violations
    dbCursor.execute("SELECT SUM(Num_Violations) FROM SpeedViolations;")
    row = dbCursor.fetchone()
    print("  Total Number of Speed Camera Violations:", f"{row[0]:,}")

##################################################################
def graphData(xAxis, yAxis, title, map):
    x = sorted(map.keys())
    y = [map[key] for key in x]
    plt.plot(x, y)
    plt.xlabel(xAxis)
    plt.ylabel(yAxis)
    plt.title(title)
    plt.show()

# Show all intersections with user's word
def optionOne(dbCursor):
    userInput = input("Enter the name of the intersection to find (wildcards _ and % allowed): ") 

    dbCursor.execute("SELECT Intersection_ID, Intersection FROM Intersections WHERE Intersection LIKE ? ORDER BY Intersection ASC", (userInput,))
    rows = dbCursor.fetchall()

    # Check if rows have any data.
    print()
    if len(rows) == 0:
        print("No intersections matching that name were found.")
    else:
        for row in rows:
            print(f"{row[0]} : {row[1]}")

# Show all Red Light and Speed Cameras at the intersection
def optionTwo(dbCursor):
    userInput = input("Enter the name of the intersection (no wildcards allowed): ") 
    
    # Red Light Cameras
    dbCursor.execute("SELECT Camera_ID, Address FROM RedCameras JOIN Intersections ON (Intersections.Intersection_ID = RedCameras.Intersection_ID) WHERE Intersection LIKE ? ORDER BY Camera_ID ASC", (userInput,))
    rows = dbCursor.fetchall()

    # Check if rows have any data.
    print()
    if len(rows) == 0:
        print("No red light cameras found at that intersection.")
    else:
        print("Red Light Cameras:")
        for row in rows:
            print(f"   {row[0]} : {row[1]}")
    print()
    # Speed Cameras
    dbCursor.execute("SELECT Camera_ID, Address FROM SpeedCameras JOIN Intersections ON (Intersections.Intersection_ID = SpeedCameras.Intersection_ID) WHERE Intersection LIKE ? ORDER BY Camera_ID ASC", (userInput,))
    rows = dbCursor.fetchall()

    # Check if rows have any data.
    if len(rows) == 0:
        print("No speed cameras found at that intersection.")
    else:
        print("Speed Cameras:")
        for row in rows:
            print(f"   {row[0]} : {row[1]}")

# Prints out percentage of violations for a specific date
def optionThree(dbCursor):
    userInput = input("Enter the date that you would like to look at (format should be YYYY-MM-DD): ") 
    
    # Red Light Violations
    dbCursor.execute("SELECT SUM(Num_Violations) FROM RedViolations WHERE Violation_Date = ?", (userInput,))
    row = dbCursor.fetchone()
    numRed = 0
    if row[0] != None:
        numRed = row[0]

    # Speed Violations
    dbCursor.execute("SELECT SUM(Num_Violations) FROM SpeedViolations WHERE Violation_Date = ?", (userInput,))
    row = dbCursor.fetchone()
    numSpeed = 0
    if row[0] != None:
        numSpeed = row[0]

    # Check if rows have any data.
    print()
    if (numRed == 0 and numSpeed == 0):
        print("No violations on record for that date.")
    else:
        total = numRed + numSpeed
        redPercent = numRed / total * 100
        speedPercent = numSpeed / total * 100
        print("Number of Red Light Violations:", f"{numRed:,}", f"({redPercent:.3f}%)")
        print("Number of Speed Violations:", f"{numSpeed:,}", f"({speedPercent:.3f}%)")
        print("Total Number of Violations:", f"{total:,}")

# Prints out number of speed and red light cameras at each intersection
def optionFour(dbCursor):
    # Red Light Cameras
    dbCursor.execute("SELECT Intersection, Intersections.Intersection_ID, COUNT(Camera_ID) FROM Intersections JOIN RedCameras ON (Intersections.Intersection_ID = RedCameras.Intersection_ID) GROUP BY Intersection ORDER BY COUNT(Camera_ID) DESC, Intersections.Intersection_ID DESC")
    rows = dbCursor.fetchall()
    total = 0
    for row in rows:
        total += row[2]
    
    print("Number of Red Light Cameras at Each Intersection")
    for row in rows:
        print(f"  {row[0]} ({row[1]}) : {row[2]}", f"({row[2] / total * 100:.3f}%)")

    # Speed Cameras
    print()
    dbCursor.execute("SELECT Intersection, Intersections.Intersection_ID, COUNT(Camera_ID) FROM Intersections JOIN SpeedCameras ON (Intersections.Intersection_ID = SpeedCameras.Intersection_ID) GROUP BY Intersection ORDER BY COUNT(Camera_ID) DESC, Intersections.Intersection_ID DESC")
    rows = dbCursor.fetchall()
    total = 0
    for row in rows:
        total += row[2]
    
    print("Number of Speed Cameras at Each Intersection")
    for row in rows:
        print(f"  {row[0]} ({row[1]}) : {row[2]}", f"({row[2] / total * 100:.3f}%)")

# Prints out number of speed and red light violations at each intersection in a specific year
def optionFive(dbCursor):
    userInput = input("Enter the year that you would like to analyze: ") 
    print()
    # Red Violations
    dbCursor.execute("SELECT Intersection, Intersections.Intersection_ID, SUM(RedViolations.Num_Violations) FROM Intersections JOIN RedCameras ON (Intersections.Intersection_ID = RedCameras.Intersection_ID) JOIN RedViolations ON (RedCameras.Camera_ID = RedViolations.Camera_ID) WHERE Violation_Date LIKE ? GROUP BY Intersection ORDER BY SUM(RedViolations.Num_Violations) DESC, Intersections.Intersection_ID DESC", (userInput + "%",))
    rows = dbCursor.fetchall()
    total = 0

    print()
    print("Number of Red Light Violations at Each Intersection for", userInput)

    if (len(rows) == 0):
        print("No red light violations on record for that year.")
    else:
        for row in rows:
            total += row[2]

        for row in rows:
            print(f"  {row[0]} ({row[1]}) : {row[2]:,}", f"({row[2] / total * 100:.3f}%)")
        print("Total Red Light Violations in", userInput, ":", f"{total:,}")
    
    # Speed Cameras
    dbCursor.execute("SELECT Intersection, Intersections.Intersection_ID, SUM(SpeedViolations.Num_Violations) FROM Intersections JOIN SpeedCameras ON (Intersections.Intersection_ID = SpeedCameras.Intersection_ID) JOIN SpeedViolations ON (SpeedCameras.Camera_ID = SpeedViolations.Camera_ID) WHERE Violation_Date LIKE ? GROUP BY Intersection ORDER BY SUM(SpeedViolations.Num_Violations) DESC, Intersections.Intersection_ID DESC", (userInput + "%",))
    rows = dbCursor.fetchall()
    total = 0

    print()
    print("Number of Speed Violations at Each Intersection for", userInput)
    
    if (len(rows) == 0):
        print("No speed violations on record for that year.")
    else:
        for row in rows:
            total += row[2]
        
        for row in rows:
            print(f"  {row[0]} ({row[1]}) : {row[2]:,}", f"({row[2] / total * 100:.3f}%)")
        print("Total Speed Violations in", userInput, ":", f"{total:,}")

# Prints number of speed and red light violations per year for a specific camera id
def optionSix(dbCursor):
    userInput = input("Enter a camera ID: ")

    dbCursor.execute("SELECT strftime('%Y', RedViolations.Violation_Date) AS Year, SUM(RedViolations.Num_Violations) FROM RedViolations WHERE RedViolations.Camera_ID = ? GROUP BY Year", (userInput,))
    redRows = dbCursor.fetchall()

    dbCursor.execute("SELECT strftime('%Y', SpeedViolations.Violation_Date) AS Year, SUM(SpeedViolations.Num_Violations) FROM SpeedViolations WHERE SpeedViolations.Camera_ID = ? GROUP BY Year", (userInput,))
    speedRows = dbCursor.fetchall()

    print()
    if (len(redRows) == 0 and len(speedRows) == 0):
        print("No cameras matching that ID were found in the database.")
        return
    else:
        print("Yearly Violations for Camera", userInput)

    # Add results of rows to map
    resultsMap = {}
    for row in redRows:
        if (row[0] not in resultsMap):
            resultsMap[row[0]] = 0
        resultsMap[row[0]] += row[1]

    for row in speedRows:
        if (row[0] not in resultsMap):
            resultsMap[row[0]] = 0
        resultsMap[row[0]] += row[1]
    
    for year, num in resultsMap.items():
        print(f"{year} : {num:,}") 
 
    #Ask User for plot of data
    title = "Yearly Violations for Camera " + userInput 
    userInput = input("Plot? (y/n) ")
    print()
    if (userInput == "y"):
        graphData("Year", "Number of Violations", title, resultsMap)

# Prints number of speed and red light violations per month in a specifc year and camera id
def optionSeven(dbCursor):
    # Check database for camera
    camInput = input("Enter a camera ID: ")
    dbCursor.execute("SELECT Camera_ID FROM RedViolations WHERE Camera_ID = ?", (camInput,))
    redRows = dbCursor.fetchall()

    dbCursor.execute("SELECT Camera_ID FROM SpeedViolations WHERE Camera_ID = ?", (camInput,))
    speedRows = dbCursor.fetchall()

    print()
    if (len(redRows) == 0 and len(speedRows) == 0):
        print("No cameras matching that ID were found in the database.")
        return
    
    yearInput = input("Enter a year: ")

    dbCursor.execute("SELECT strftime('%m/%Y', RedViolations.Violation_Date) AS Date, SUM(RedViolations.Num_Violations) FROM RedViolations WHERE RedViolations.Camera_ID = ? AND RedViolations.Violation_Date LIKE ? GROUP BY Date", (camInput, yearInput + "%"))
    redRows = dbCursor.fetchall()

    dbCursor.execute("SELECT strftime('%m/%Y', SpeedViolations.Violation_Date) AS Date, SUM(SpeedViolations.Num_Violations) FROM SpeedViolations WHERE SpeedViolations.Camera_ID = ? AND SpeedViolations.Violation_Date LIKE ? GROUP BY Date", (camInput, yearInput + "%"))
    speedRows = dbCursor.fetchall()

    # Add results of rows to map
    resultsMap = {}
    for row in redRows:
        if (row[0] not in resultsMap):
            resultsMap[row[0]] = 0
        resultsMap[row[0]] += row[1]

    for row in speedRows:
        if (row[0] not in resultsMap):
            resultsMap[row[0]] = 0
        resultsMap[row[0]] += row[1]
    
    print()
    print("Monthly Violations for Camera " + camInput + " in " + yearInput)
    for month, num in resultsMap.items():
        print(f"{month} : {num:,}") 
    
    #Ask User for plot of data
    title = "Monthly Violations for Camera " + camInput + " (" + yearInput + ")"
    print()
    userInput = input("Plot? (y/n) ")
    if (userInput == "y"):
        monthArr = {}
        for key, value in resultsMap.items():
            month, _ = key.split('/')
            monthArr[month] = value
        graphData("Month", "Number of Violations", title, monthArr)

# Prints speed and red light violations in a year for comparison
def optionEight(dbCursor):
    userInput = input("Enter a year: ")
    dbCursor.execute("SELECT Violation_Date, SUM(Num_Violations) FROM RedViolations WHERE Violation_Date LIKE ? GROUP BY Violation_Date ORDER BY Violation_Date ASC", (userInput + "%",))
    redRows = dbCursor.fetchall()

    dbCursor.execute("SELECT Violation_Date, SUM(Num_Violations) FROM SpeedViolations WHERE Violation_Date LIKE ? GROUP BY Violation_Date ORDER BY Violation_Date ASC", (userInput + "%",))
    speedRows = dbCursor.fetchall()

    # Organize data to get first 5 and last 5 dates
    counter = 0
    redMap = {}
    for row in redRows:
        if (counter == 5):
            break
        redMap[row[0]] = row[1]
        counter += 1
    for row in reversed(redRows):
        if (counter == 10):
            break
        redMap[row[0]] = row[1]
        counter += 1

    speedMap = {}
    counter = 0
    for row in speedRows:
        if (counter == 5):
            break
        speedMap[row[0]] = row[1]
        counter += 1
    for row in reversed(speedRows):
        if (counter == 10):
            break
        speedMap[row[0]] = row[1]
        counter += 1

    # Print out the violations
    print()
    print("Red Light Violations:")
    for date, violations in sorted(redMap.items()):
        print(f"{date} {violations}")

    print()
    print("Speed Violations:")
    for date, violations in sorted(speedMap.items()):
        print(f"{date} {violations}")

    # Plot both red and speed violations per day
    year = userInput
    print()
    userInput = input("Plot? (y/n) ")
    if (userInput == "y"):
        # Set up 365 days with 0's set
        redY = [0] * 365
        speedY = [0] * 365

        for row in redRows:
            date = datetime.fromisoformat(row[0])
            idx = (date - datetime(int(year), 1, 1)).days
            redY[idx] = row[1]
        for row in speedRows:
            date = datetime.fromisoformat(row[0])
            idx = (date - datetime(int(year), 1, 1)).days
            speedY[idx] = row[1]
        
        x = list(range(365))
        plt.plot(x, redY, label = "Red Light", color = "Red")
        plt.plot(x, speedY, label = "Speed", color = "Orange")
        plt.xlabel("Day")
        plt.ylabel("Number of Violations")
        plt.title("Violations Each Day of " + year)
        plt.legend()
        plt.show()

 # Prints data and coordinates for red light and speed cameras on a street   
def optionNine(dbCursor):
    # Get data for red light and speed cameras
    userInput = input("Enter a street name: ")
    dbCursor.execute("SELECT Camera_ID, Address, Latitude, Longitude FROM RedCameras WHERE Address LIKE ? ORDER BY Camera_ID", ("%" + userInput + "%",))
    redRows = dbCursor.fetchall()

    dbCursor.execute("SELECT Camera_ID, Address, Latitude, Longitude FROM SpeedCameras WHERE Address LIKE ? ORDER BY Camera_ID", ("%" + userInput + "%",))
    speedRows = dbCursor.fetchall()

    # Print out data collected
    print()
    if (len(redRows) == 0 and len(speedRows) == 0):
        print("There are no cameras located on that street.")
        return
    
    print("List of Cameras Located on Street: " + userInput)
    print("  Red Light Cameras:")
    for row in redRows:
        print(f"     {row[0]} : {row[1]} ({row[2]}, {row[3]})")

    print("  Speed Cameras:")
    for row in speedRows:
        print(f"     {row[0]} : {row[1]} ({row[2]}, {row[3]})")
    
    # Ask user for plot
    street = userInput
    print()
    userInput = input("Plot? (y/n) ")
    if userInput == "y":
        # Add lat and long of speed and red light cams to the list
        xRed = []
        yRed = []
        xSpeed = []
        ySpeed = []
        for row in redRows:
            yRed.append(row[2])
            xRed.append(row[3])
        for row in speedRows:
            ySpeed.append(row[2])
            xSpeed.append(row[3])

        image = plt.imread("chicago.png")
        xydims = [-87.9277, -87.5569, 41.7012, 42.0868]
        plt.imshow(image, extent=xydims)
        plt.title("Cameras on Street: " + street)

        plt.plot(xRed, yRed, color = 'red', marker = 'o')
        plt.plot(xSpeed, ySpeed, color = 'orange', marker = 'o')

        for row in redRows:
            plt.annotate(row[0], (row[3], row[2]))
        for row in speedRows:
            plt.annotate(row[0], (row[3], row[2]))
        plt.xlim([-87.9277, -87.5569])
        plt.ylim([41.7012, 42.0868])
        plt.show() 

#   
# main
#
dbConn = sqlite3.connect('chicago-traffic-cameras.db')
dbCursor = dbConn.cursor()

print("Project 2: Chicago Traffic Camera Analysis")
print("CS 341, Spring 2026")
print()
print("This application allows you to analyze various")
print("aspects of the Chicago traffic camera database.")
print()
print_stats(dbCursor)
print()

print("Select a menu option: ")
print("  1. Find an intersection by name")
print("  2. Find all cameras at an intersection")
print("  3. Percentage of violations for a specific date")
print("  4. Number of cameras at each intersection")
print("  5. Number of violations at each intersection, given a year")
print("  6. Number of violations by year, given a camera ID")
print("  7. Number of violations by month, given a camera ID and year")
print("  8. Compare the number of red light and speed violations, given a year")
print("  9. Find cameras located on a street")
print("or x to exit the program.")

userInput = input("Your choice --> ")
print()
while (userInput != "x"):
    if (userInput == "1"):
        optionOne(dbCursor)
    elif (userInput == "2"):
        optionTwo(dbCursor)
    elif (userInput == "3"):
        optionThree(dbCursor)
    elif (userInput == "4"):
        optionFour(dbCursor)
    elif (userInput == "5"):
        optionFive(dbCursor)
    elif (userInput == "6"):
        optionSix(dbCursor)
    elif (userInput == "7"):
        optionSeven(dbCursor)
    elif (userInput == "8"):
        optionEight(dbCursor)
    elif (userInput == "9"):
        optionNine(dbCursor) 
    else:
        print("Error, unknown command, try again...")
        
    print()
    print("Select a menu option: ")
    print("  1. Find an intersection by name")
    print("  2. Find all cameras at an intersection")
    print("  3. Percentage of violations for a specific date")
    print("  4. Number of cameras at each intersection")
    print("  5. Number of violations at each intersection, given a year")
    print("  6. Number of violations by year, given a camera ID")
    print("  7. Number of violations by month, given a camera ID and year")
    print("  8. Compare the number of red light and speed violations, given a year")
    print("  9. Find cameras located on a street")
    print("or x to exit the program.")
    userInput = input("Your choice --> ")
    print()


print("Exiting program.")
#
# done
#
