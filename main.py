import tkinter as tk
import pyperclip as pc 
import math
import json 
from datetime import datetime




def roundPrice(price):
    # Επιστρέφει την στρογγυλοποιημένη και την διαφορά των 2
    remain = price%5
    if (remain <= 2):
        endPrice = int(round(price))
    else:
        endPrice = int(price + 5 - remain)
    
    return endPrice, endPrice - price


def resetOutputField():
    global totalFirstBefore, totalFirstAfter, totalSecond, totalThird
    totalFirstBefore = 0 
    totalFirstAfter = 0 
    totalSecond = 0 
    totalThird = 0 

    beforeFPA.config(state="normal")
    afterFPA.config(state="normal")
    beforeFPA.delete(1.0, tk.END)
    afterFPA.delete(1.0, tk.END)
    beforeFPA.config(state="disabled")
    afterFPA.config(state="disabled")


def writeToTextbox(logBox, text: str):

    logBox.config(state="normal") # enables the widget to write
    logBox.insert(tk.END, text)
    logBox.config(state="disabled") # disbles is afterwards
    logBox.see(tk.END)
    root.update()


def prepareInput(value: str):
    if (value == "" or value is None):
        return 0
    
    return float(value.strip().replace(",", "."))
    

    
def calculate_price(event=None):
    global totalFirstBefore, totalFirstAfter, totalSecond, totalThird

    if(prepareInput(firstProductField.get()) == 0):
        return
    

    resetOutputField()


   
    firstProdCost = prepareInput(firstProductField.get())
    secondProdCost = prepareInput(secondProductField.get())
    thirdProdCost = prepareInput(thirdProductField.get())
    transportCost = float(prepareInput(transportCostField.get()))


    totalFirstBefore = math.ceil(firstProdCost * (1+profitPercentage) + workCost * costVar.get() + transportCost)
    totalFirstAfter = math.ceil((firstProdCost * (1+profitPercentage) + workCost * costVar.get()) * (1+fpaPercentage) + transportCost)

    totalSecond = math.ceil(secondProdCost * (1+profitPercentage) * (1+fpaPercentage)) 

    totalThird = math.ceil(thirdProdCost * (1+profitPercentage) * (1+fpaPercentage)) 

    totalBefore, diff = roundPrice(totalFirstBefore + totalSecond + totalThird)
    totalFirstBefore += diff


    totalAfter, diff = roundPrice(totalFirstAfter + totalSecond + totalThird)
    totalFirstAfter += diff

    addToLog([firstProdCost, secondProdCost, thirdProdCost], totalBefore, totalAfter, transportCost)
    writeToTextbox(beforeFPA,  "%d€ (%d, %d, %d)" % (totalBefore, totalFirstBefore, totalSecond, totalThird))
    writeToTextbox(afterFPA,  "%d€ (%d, %d, %d)" % (totalAfter, totalFirstAfter, totalSecond, totalThird))


def copyBeforePrice():
    copyString = "  %d€ προ" % (totalFirstBefore)

    if (totalSecond > 0):
        copyString += ",  %d€ τελική" % (totalSecond)
    
    if (totalThird > 0):
        copyString += ",  %d€ τελική" % (totalThird)


    if (totalSecond == 0 and totalThird == 0):
        pc.copy(copyString)
    else:
        copyString += ". Σύνολο: %d€" % (totalFirstBefore + totalSecond + totalThird)
        pc.copy(copyString)
    
    


def copyAfterPrice():
    copyString = "  %d€ τελική" % (totalFirstAfter)

    if (totalSecond > 0):
        copyString += ",  %d€ τελική" % (totalSecond)
    
    if (totalThird > 0):
        copyString += ",  %d€ τελική" % (totalThird)

    if (totalSecond == 0 and totalThird == 0):
        pc.copy(copyString)

    else:
        copyString += ". Σύνολο: %d€" % (totalFirstAfter + totalSecond + totalThird)
        pc.copy(copyString)



def saveParameters():
    # Saves the parameters on exiting, controlled by root.protocol @ end of code
    params = {
        "transportCost" : prepareInput(transportCostField.get()),
        "workCost" : workCost,
        "profitPercentage": profitPercentage,
        "fpaPercentage": fpaPercentage
    }

    with open("parameters.json", "w") as paramsFile:
        json.dump(params, paramsFile, indent=4)
    
    root.destroy()



def loadParametrs():
    global transportCost, workCost, profitPercentage, fpaPercentage
    try:
        with open("parameters.json", "r") as paramsFile:
            params = json.load(paramsFile)
            transportCost = params["transportCost"]
            workCost = params["workCost"]
            profitPercentage = params["profitPercentage"]
            fpaPercentage = params["fpaPercentage"]

    except FileNotFoundError:
        transportCost = 3.5


def addToLog(startingPrice, beforeFPA_price: float, afterFPA_price: float, transportCost):
    
    writeString = datetime.now().strftime("%d/%m/%Y %H:%M") + "," 

    with open("history.csv", "a") as historyFile:
        # Prepare the line
        for price in startingPrice:
            writeString += str(price) + ","
        
        writeString += str(beforeFPA_price) + "," + str(afterFPA_price) + "," + str(transportCost) + ","
        writeString += str(workCost) + "," + str(profitPercentage) + "," + str(fpaPercentage)
        
        # and then write it
        historyFile.write(writeString)
        historyFile.write("\n")

        




# Create main window
root = tk.Tk()
root.title("Price Calculator")


# these values should only appear on first time launch
transportCost = -1.0 
workCost = -1
profitPercentage  = -1
fpaPercentage = -1

totalFirstBefore = 0 
totalFirstAfter = 0 
totalSecond = 0 
totalThird = 0 



loadParametrs()


costVar = tk.IntVar(value=1)
workChekcBox = tk.Checkbutton(root, text="Κοστος Εργασίας", variable=costVar )
workChekcBox.grid(row=0, column=0, columnspan=1, padx=30, sticky="w")


transCostLabel = tk.Label(root, text="Κόστος μεταφοράς:")
transCostLabel.grid(row=0, column=1)

transportCostField = tk.Entry(root, width=5)
transportCostField.insert(0, str(transportCost))
transportCostField.grid(row=0, column=2, pady=10, padx=20, sticky="w")


# Input label
inputLabel = tk.Label(root, text="Τιμές:")
inputLabel.grid(row=1, column=0, sticky="e")

# First prorduct input price
firstProductField = tk.Entry(root, width=15)
firstProductField.grid(row=1, column=1)

# Second prorduct input price
tk.Label(root, text="(θα έχει ΦΠΑ)").grid(row=2, column=0, sticky="e")
secondProductField = tk.Entry(root, width=15)
secondProductField.grid(row=2, column=1)


# Third prorduct input price
tk.Label(root, text="(θα έχει ΦΠΑ)").grid(row=3, column=0, sticky="e")
thirdProductField = tk.Entry(root, width=15)
thirdProductField.grid(row=3, column=1)



# BeforeFPA label 
label_beforeFPA = tk.Label(root, text="Προ ΦΠΑ:")
label_beforeFPA.grid(row=4, column=0, pady=20, sticky="e")

# BeforeFPA field
beforeFPA = tk.Text(root, height=1, width=20, state="disabled")
beforeFPA.grid(row=4, column=1, pady=10)

beforeFPA_copy = tk.Button(root, text="Copy", command=copyBeforePrice)
beforeFPA_copy.grid(row=4, column=2, sticky="w")


# BeforeFPA label 
label_afterFPA = tk.Label(root, text="Τελική:")
label_afterFPA.grid(row=5, column=0, pady=20, sticky="e")

afterFPA = tk.Text(root, height=1, width=20, state="disabled")
afterFPA.grid(row=5, column=1, pady=10)

afterFPA_copy = tk.Button(root, text="Copy", command=copyAfterPrice)
afterFPA_copy.grid(row=5, column=2, sticky="w")


# Button to trigger conversion
convert_button = tk.Button(root, text="Calculate", command=calculate_price)
convert_button.grid(row=6, column=0, columnspan=3, padx=10, pady=10)


root.bind("<Return>", calculate_price)
root.protocol("WM_DELETE_WINDOW", saveParameters) # Save the params when exiting
root.mainloop()
