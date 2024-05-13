import json
import os
import re
import tkinter as tk
from tkinter import filedialog
import deepl
from googletrans import Translator

class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.show)
        self.widget.bind("<Leave>", self.hide)

    def show(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        
        # Create tooltip if not already created
        if self.tooltip is None:
            self.tooltip = tk.Toplevel(self.widget)
            self.tooltip.wm_overrideredirect(True)
            self.tooltip.wm_geometry(f"+{x}+{y}")
            label = tk.Label(self.tooltip, text=self.text, background="#ffffe0", relief="solid", borderwidth=1)
            label.pack(ipadx=1)

    def hide(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

#All DeepL languages keys and translationCodes
deeplLanguages = {
	"Bulgarian" : "BG",
	"Chinese (simplified)" : "ZH",
	"Czech" : "CS",
	"Danish" : "DA",
	"Dutch" : "NL",
	"English (American)" : "EN-US",
	"English (British)" : "EN-GB",
	"Estonian" : "ET",
	"Finnish" : "FI",
	"French" : "FR",
	"German" : "DE",
	"Greek" : "EL",
	"Hungarian" : "HU",
	"Indonesian" : "ID",
	"Italian" : "IT",
	"Japanese" : "JA",
	"Korean" : "KO",
	"Latvian" : "LV",
	"Lithuanian" : "LT",
	"Norwegian (Bokmål)" : "NB",
	"Polish" : "PL",
	"Portuguese (all Portuguese varieties excluding Brazilian Portuguese)" : "PT-PT",
	"Portuguese (Brazilian)" : "PT-BR",
	"Romanian" : "RO",
	"Russian" : "RU",
	"Slovak" : "SK",
	"Slovenian" : "SL",
	"Spanish" : "ES",
	"Swedish" : "SV",
	"Turkish" : "TR",
	"Ukrainian" : "UK",
}

#EzDialogue Syntax
parseToJsonDict = {
	"T":"",#NPC Dialogue
	"O":"?> ",#Player Reponse Option
	"G":"-> ",#GOTO after Player Response Option
	"I":"$if ",#If statement
	"OB": " {",#Opening Bracket
	"CB": "}",#Close Bracket
	"S": "",#Signal
}

#All Google Languages keys and their translation code
googleLanguages = {
    'Afrikaans': 'af',
    'Albanian': 'sq',
    'Amharic': 'am',
    'Arabic': 'ar',
    'Armenian': 'hy',
    'Azerbaijani': 'az',
    'Basque': 'eu',
    'Belarusian': 'be',
    'Bengali': 'bn',
    'Bosnian': 'bs',
    'Bulgarian': 'bg',
    'Catalan': 'ca',
    'Cebuano': 'ceb',
    'Chichewa': 'ny',
    'Chinese (Simplified)': 'zh-cn',
    'Chinese (Traditional)': 'zh-tw',
    'Corsican': 'co',
    'Croatian': 'hr',
    'Czech': 'cs',
    'Danish': 'da',
    'Dutch': 'nl',
    'English': 'en',
    'Esperanto': 'eo',
    'Estonian': 'et',
    'Filipino': 'tl',
    'Finnish': 'fi',
    'French': 'fr',
    'Frisian': 'fy',
    'Galician': 'gl',
    'Georgian': 'ka',
    'German': 'de',
    'Greek': 'el',
    'Gujarati': 'gu',
    'Haitian Creole': 'ht',
    'Hausa': 'ha',
    'Hawaiian': 'haw',
    'Hebrew': 'iw',
    'Hebrew': 'he',
    'Hindi': 'hi',
    'Hmong': 'hmn',
    'Hungarian': 'hu',
    'Icelandic': 'is',
    'Igbo': 'ig',
    'Indonesian': 'id',
    'Irish': 'ga',
    'Italian': 'it',
    'Japanese': 'ja',
    'Javanese': 'jw',
    'Kannada': 'kn',
    'Kazakh': 'kk',
    'Khmer': 'km',
    'Korean': 'ko',
    'Kurdish (Kurmanji)': 'ku',
    'Kyrgyz': 'ky',
    'Lao': 'lo',
    'Latin': 'la',
    'Latvian': 'lv',
    'Lithuanian': 'lt',
    'Luxembourgish': 'lb',
    'Macedonian': 'mk',
    'Malagasy': 'mg',
    'Malay': 'ms',
    'Malayalam': 'ml',
    'Maltese': 'mt',
    'Maori': 'mi',
    'Marathi': 'mr',
    'Mongolian': 'mn',
    'Myanmar (Burmese)': 'my',
    'Nepali': 'ne',
    'Norwegian': 'no',
    'Odia': 'or',
    'Pashto': 'ps',
    'Persian': 'fa',
    'Polish': 'pl',
    'Portuguese': 'pt',
    'Punjabi': 'pa',
    'Romanian': 'ro',
    'Russian': 'ru',
    'Samoan': 'sm',
    'Scots Gaelic': 'gd',
    'Serbian': 'sr',
    'Sesotho': 'st',
    'Shona': 'sn',
    'Sindhi': 'sd',
    'Sinhala': 'si',
    'Slovak': 'sk',
    'Slovenian': 'sl',
    'Somali': 'so',
    'Spanish': 'es',
    'Sundanese': 'su',
    'Swahili': 'sw',
    'Swedish': 'sv',
    'Tajik': 'tg',
    'Tamil': 'ta',
    'Telugu': 'te',
    'Thai': 'th',
    'Turkish': 'tr',
    'Ukrainian': 'uk',
    'Urdu': 'ur',
    'Uyghur': 'ug',
    'Uzbek': 'uz',
    'Vietnamese': 'vi',
    'Welsh': 'cy',
    'Xhosa': 'xh',
    'Yiddish': 'yi',
    'Yoruba': 'yo',
    'Zulu': 'zu'
}

#region globalVariables
authKey = ""
deeplTranslator=None
deepLEnabled = False
defaultLanguage = ""
#endregion

#region folder Variables
inputFolder = "1.Input\\"#Input DialogueHere
parsedFolder = "2.Parsed\\"#Parsed Files into respective T: O: G: etc will be placed here
translationsFolder = "3.Translations\\"#Files after translations will be placed here
finalFolder = "4.Final\\"#Final JSONS translated will be placed here
#endregion

#region Tkinter GUI

def main(root=""):
	windowW = 400
	if deepLEnabled:
		windowH = 440
	else:
		windowH = 400
	if root == "":
		root = tk.Tk()
	root.title("Main Menu")
	toolbarMethod(root)

	#region parsingMethods
	def parseOne():#Parse Single File
		filePath = filedialog.askopenfilename(initialdir=inputFolder,filetypes=[("Json File","*.json")]) #Open File explorer to select a JSON file
		if filePath:
			fileRegex = re.sub(r"/",r"\\",filePath)
			fileSplit = fileRegex.split(inputFolder)
			print("Parsing | [0/1] | Current File: "+inputFolder+fileSplit[1])
			parseSingle(inputFolder+fileSplit[1])
			print("Parsing | [1/1] | Complete.\n")
			root.update()  # Refresh the window
	def parseAll():
		parseMuli()
		root.update()  # Refresh the window
	#endregion
	#region translationMethods
	def translate_menu():
		refreshWindow(root)
		translateMain(root)
		root.update()  # Refresh the window
	#endregion
	#region backToJSONMethods
	def BTJSingle():
		filePath = filedialog.askopenfilename(initialdir=translationsFolder,filetypes=[("Text File","*.txt")]) #Open File Explorer to select single file of .txt format.
		if filePath:
			fileRegex = re.sub(r"/",r"\\",filePath)
			fileSplit = fileRegex.split(translationsFolder)
			print("Convert to Json | [0/1] | Current File: "+translationsFolder+fileSplit[1])
			convertToJsonSingle(translationsFolder+fileSplit[1])
			print("Convert to Json | [1/1] | Complete.\n")
			root.update()  # Refresh the window
	def BTJMulti():
		convertToJsonMulti()
		root.update()  # Refresh the window
	#endregion

	tk.Label(root, text="Main Menu").pack()

	#region Parsing GUI Row
	tk.Label(root, text="[1] Parse Files").pack(pady=10)
	parseFrame = tk.Frame(root)
	parseFrame.pack()
	tk.Button(parseFrame, text="Manual Select Files", command=parseOne).pack(side=tk.LEFT, padx=(0, 5))
	tk.Button(parseFrame, text="All "+inputFolder+" Folder", command=parseAll).pack(side=tk.LEFT, padx=(0, 5))
	#endregion

	#region Translation GUI Row
	tk.Label(root, text="[2] Translate").pack(pady=10)
	tk.Button(root, text="Translate", command=translate_menu).pack()
	#endregion

	#region Convert to JSON GUI Row
	tk.Label(root, text="[3] Convert Back to JSON").pack(pady=10)
	transToJsonFrame = tk.Frame(root)
	transToJsonFrame.pack()
	tk.Button(transToJsonFrame, text="Manual Select Files", command=BTJSingle).pack(side=tk.LEFT, padx=(0, 5))
	tk.Button(transToJsonFrame, text="All Translated Files", command=BTJMulti).pack(side=tk.LEFT, padx=(0, 5))
	#endregion

	tk.Button(root, text="Exit", command=root.quit).pack(pady=20)	#Quit Button
	if deepLEnabled:#If deepL is enabled display a label with the monthly limit.
		tk.Label(root, text="DeepL Character Usage: "+str(deeplTranslator.get_usage().character.count) +"/"+str(deeplTranslator.get_usage().character.limit)).pack()
		
	tk.Label(root, text="Created by GitHub.com/SeanKR-IRE. 2024\n V1.0.0").pack(pady=10)
	centreWindow(root,windowW,windowH)
	root.mainloop()

def toolbarMethod(root:tk.Tk):

	def settings():
		settingsMenu(root)
	def showDropdown(event:tk.Event):
		dropdownMenu.update_idletasks() 
		dropdownMenu.post(event.widget.winfo_rootx(),event.widget.winfo_rooty() + event.widget.winfo_height())
	#def hideDropdown(event:tk.Event):
	#	dropdownMenu.unpost() 			#Can't seem to get working.
	#	dropdownMenu.update_idletasks() 
	
	toolbarFrame = tk.Frame(root,bd=1, relief=tk.RAISED)

	tbButton1 = tk.Button(toolbarFrame,text="Options")
	tbButton1.pack(side=tk.LEFT,padx=2,pady=2)

	dropdownMenu = tk.Menu(root,tearoff=0)
	dropdownMenu.add_command(label="Settings",command=settings)
	dropdownMenu.add_command(label="Exit", command=root.quit)

	tbButton1.bind("<Enter>", showDropdown)
	#tbButton1.bind("<Leave>", hideDropdown)

	toolbarFrame.pack(side=tk.TOP,fill=tk.X)

def settingsMenu(root):		#Settings Menu for user configuration.
	windowW = 350
	windowH = 130
	def checkbox_callback():
		if checkbox_var.get():
			checkbox_var.set(False)
			checkbox.select()
			apiKeyFrame.pack()
			entry.delete(0, tk.END)
			entry.insert(0, settingValues["DeepL API Key"])
		else:
			checkbox_var.set(True)
			checkbox.deselect()
			apiKeyFrame.pack_forget()
	def saveToJson():
		if checkbox_var.get():
			defLanguage = "EN-GB"
		else:
			defLanguage = 'en'
		if checkbox_var != deepLEnabled:
			print("WARNING! Restart the entire program for the translation library to initalize!")
			print("ENSURE YOU HAVE API IN CORRECTLY!")
		finalValue = {
			"Use DeepL": checkbox_var.get(),
			"DeepL API Key": entry.get(),
			"Default Language": defLanguage
		}
		jsonSaveHandler(finalValue)
		root.update()
	def destroyWindow():
		root.update()
		settingRoot.destroy()


	settingValues = json.load(open("settings.json"))
	settingRoot = tk.Toplevel(root)
	settingRoot.title("Settings")

	checkbox_var = tk.BooleanVar(value=settingValues['Use DeepL'])


	tk.Label(settingRoot, text="Settings").pack()
	deeplFrame = tk.Frame(settingRoot)
	deeplFrame.pack()

	checkbox = tk.Checkbutton(deeplFrame, text="Use DeepL or Google Translate", variable=checkbox_var, command=checkbox_callback)
	checkbox.pack()
	tooltip = Tooltip(checkbox,"True for DeepL, False for Google Translate\nDeepL will be much faster and may be more accurate but requires money after 500K words/Month.")

	apiKeyFrame = tk.Frame(deeplFrame)
	apiKeyFrame.pack(pady=10)  

	label = tk.Label(apiKeyFrame, text="Enter API Key:")
	label.pack(side=tk.LEFT, padx=(0, 5))  

	entry = tk.Entry(apiKeyFrame, width=40)
	entry.pack(side=tk.LEFT) 

	checkbox_callback()
	
	operationButtons = tk.Frame(settingRoot)
	operationButtons.pack(pady=10)  # Add padding around the frame
	quitButton = tk.Button(operationButtons, text="Return", command=destroyWindow,height=20)
	quitButton.pack(side=tk.LEFT, padx=(0, 5),pady=10)  # Pack label to the left with padding on the right

	# Create an entry field
	saveButton = tk.Button(operationButtons, text="Save", command=saveToJson,height=20)
	saveButton.pack(side=tk.LEFT,pady=10)  # Pack entry to the left

	centreWindow(settingRoot,windowW,windowH)
	# Run the application
	settingRoot.mainloop()

def centreWindow(root:tk.Tk,width,height):
	screenW = root.winfo_screenwidth()
	screenH = root.winfo_screenheight()

	x = (screenW-width)//2
	y = (screenH-height)//2

	root.geometry(f"{width}x{height}+{x}+{y}")

def refreshWindow(root:tk.Tk):
	"Remove all widgets from the root window"
	for widget in root.winfo_children():
		widget.destroy()

def returnToMain(root:tk.Tk):
	refreshWindow(root)
	main(root)
	root.update()  # Refresh the window

def translateMain(root:tk.Tk):
	"Menu for selecting the desired language to translate a file to."
	
	def singleTranslation():
		fileName = filedialog.askopenfilename(initialdir=parsedFolder,filetypes=[("Text File","*.txt")])
		if fileName:
			fileRegex = re.sub(r"/",r"\\",fileName)
			fileSplit = fileRegex.split(parsedFolder)
			selectedFile = parsedFolder+fileSplit[1]
			language = languageOptions.get(selectionOptions.get())
			print("Translations | [0/1] | Current File: "+selectedFile)
			cycleThroughOptions(selectedFile,language)
			print("Translations | [1/1] | Complete.\n")
	def multiTranslation():
		language = languageOptions.get(selectionOptions.get())
		cycleThroughOptionsMulti(language)
	def returnMenu():
		returnToMain(root)

	selectionOptions = tk.StringVar(root)
	if deepLEnabled:
		languageOptions = deeplLanguages
	else:
		languageOptions = googleLanguages
	try:
		selectionOptions.set(findKey(settingValues["Default Language"],languageOptions))
	except Exception as e:
		print(f"E FindKey: {e}")
	tk.Label(root, text="Select desired output").pack()
	selectionBox = tk.OptionMenu(root,selectionOptions,*languageOptions)
	selectionBox.pack()

	tk.Button(root, text="Select File", command=singleTranslation).pack()
	tk.Button(root, text="Translate all", command=multiTranslation).pack()
	tk.Button(root, text="Return to main menu", command=returnMenu).pack()

	root.mainloop()

#endregion

#region Parsing

def parseMuli():                 
	"Converts all JSONS in InputFolder into ledgeable text files located in Output."
	printPrefix = f"Parsing | "
	dirlength = expensiveDirWalk(inputFolder,".json") 
	cur = 0
	size = len(dirlength)
	maxLen = len(str(size))
	formattedCur = f"{cur:0{maxLen}}"
	for i,e in enumerate(dirlength):
		formattedCur = f"{i:0{maxLen}}"
		cur = i
		print(f"{printPrefix}[{formattedCur}/{size}] | Current File: {e}")
		parseSingle(e)
	cur+=1
	formattedCur = f"{cur:0{maxLen}}"
	print(f"{printPrefix}[{formattedCur}/{size}] | Complete.\n")

def parseSingle(file):
	"Single File Parse."
	f = open(file)
	data = json.load(f)
	outputFileParsed = ""
	fileSplit = file.split("\\")
	lastSplit = fileSplit[len(fileSplit)-1]		#File.json
	directory = parsedFolder
	for i,dir in enumerate(fileSplit): #If sub-directories make them
		if i >0:
			if dir != lastSplit:
				directory+=dir+"\\"
	fileName = re.sub(".json","",lastSplit,flags=re.IGNORECASE)
	maxIndex = len(data)-1		#Used for ProgressBar
	totalIters = len(data)		#Used for ProgressBar
	progressCharSpacing = 20	#Used for ProgressBar
	for i, item in enumerate(data):
		progress = (i+1)/totalIters
		progressChar = int(progress*progressCharSpacing)
		print(f"[{'#' * progressChar}{' ' * (progressCharSpacing - progressChar)}] {progress * 100:.1f}%", end='\r')
		commands_raw = item.get('commands_raw', None)
		if commands_raw is not None:
			commands = re.sub(r'\n', r'°', commands_raw)    #Converting any new line break (\n) into a character never really used. This is to ensure the EzDialogue editor will always look the same no matter what language Once you do convertToJsonSingle()
			regexFinish = parseNPCText(commands)
			outputFileParsed += regexFinish
		else:
			print("No 'commands_raw' found in", file)
		if i<maxIndex:
			outputFileParsed+="\n\n"

	saveFile(outputFileParsed, fileName+"Parsed", directory)

def parseNPCText(text):
	patterns = {
		"If condition": r'\$if\s+([^}]+)\{',
		"Option": r'(?<!\\)\?>',
		"If": r'(?<!\\)\$if',
		"Signal": r'(?<!\\)signal\([^)]*\)',
		"SignalValue": r'(?<!\\)signal\([^,]+,[^,]+,([^)]+)\)'

	}
	entireNode = text.split("°")
	lastNPCText = False
	enteredCode = False
	nested = False
	npcText = "T: "
	formattedOutput = ""
	operationCount = 1
	indexCount = 0
	for line in entireNode:
		if line[:3]== "$if": #Check if is validIf
			enteredCode=True
			nested = True
			condition = re.search(patterns["If condition"],line).group(1).strip()
			formattedOutput+= f"I{operationCount}: {condition.lstrip()}\nOB{operationCount}: °\n"
		elif line == '}':
			if nested:
				enteredCode=True
				nested = False
				formattedOutput+= f"CB{operationCount}: °\n"
		elif re.search(patterns["Option"],line):
			enteredCode=True
			goTo = ""
			option = ""
			newLine = line.split("?>")[1]
			tempSplit = newLine.split("->")
			option = tempSplit[0]
			if "{" in line:
				nested = True
				option = f"{option[:option.find('{')]}\nOB{operationCount}: °"
			if "->" in newLine:
				goTo += f"G{operationCount}: {tempSplit[1].lstrip()} °\n"


			formattedOutput+= f"O{operationCount}: {option.lstrip()}\n{goTo}"
		elif re.search(patterns["Signal"],line):
			enteredCode=True
			formattedOutput+=f"S{operationCount}: {line.lstrip()}°\n"
		elif nested:
			enteredCode=True
			if "->" in line:
				goTo = line.split("->")
				formattedOutput+=f"G{operationCount}: {goTo[1].lstrip()}°\n"
			else:
				formattedOutput+=f"T{operationCount}: {line.lstrip()}°\n"

		if enteredCode:
			if not nested:
				operationCount+=1
			if not lastNPCText:
				lastNPCText = True
				npcText+="\n"
		if not lastNPCText:
			npcText+= f"{line}°"
		indexCount+=1
		if indexCount == 8:
			pass
	return npcText+formattedOutput


#endregion

#region Translations
def cycleThroughOptionsMulti(language):
	printPrefix = f"Translations [{language}] | "
	dirlength = expensiveDirWalk(parsedFolder,"Parsed.txt")
	cur = 0
	size = len(dirlength)
	maxLen = len(str(size))
	formattedCur = f"{cur:0{maxLen}}"
	for i,e in enumerate(dirlength):
		formattedCur = f"{i:0{maxLen}}"
		cur = i
		print(f"{printPrefix}[{formattedCur}/{size}] | Current File: {e}")
		cycleThroughOptions(e,language)
	cur+=1
	formattedCur = f"{cur:0{maxLen}}"
	print(f"{printPrefix}[{formattedCur}/{size}] | Complete.\n")
			
def cycleThroughOptions(absFileLocation,language):

	def seperateString(input):
		def textLine(input,list,index,language):
			if input != "°":
				breakSplit = input.split("°")
				breakCount = input.count("°")
				finalString = ""
				for i,e in enumerate(breakSplit):
					if e != "\\":
						if e:
							temp = translationMethod(language,e)
							finalString +=temp
					else:
						finalString+="\\"
					if i < breakCount:
						finalString+="°"
				if input == finalString:
					pass
				else:
					pass
				list[index]=finalString
			else:
				list[index]=input
		# Define regular expressions for matching ${*} and signal(*)
		variablePattern = r'\${(.*?)}'
		signalPattern = r'signal\((.*?)\)'
		variableSplit = re.split(variablePattern,input)
		firstList = [s for s in variableSplit if s]
		hackyIndex = 0
		endWhile = False
		while not endWhile:
			try:
				entry=firstList[hackyIndex]
			except IndexError:#I'm losing my marbles
				endWhile= True
			try:
				if not endWhile:
					entryInListIndex = input.find(entry)
					checkVariableValue = input[entryInListIndex-2:entryInListIndex]
					if checkVariableValue == "${":#Dont touch Variable Names

						firstList[hackyIndex]="${"+entry+"}"
						hackyIndex+=1
					else:
						if re.search(signalPattern,entry):#signal(*) check
							signalSplit = re.split(signalPattern,entry)
							secondList = [s for s in signalSplit if s]
							for secIndex,secEntry in enumerate(secondList):
								try:
									secEntryInListIndex = input.find(secEntry)
									checkSignalValue = input[secEntryInListIndex-7:secEntryInListIndex]
									if checkSignalValue == "signal(":#if signal
										args=""
										signalARGS = secEntry.split(",")
										signalArgsStart  = signalARGS[2].lstrip()[:1]
										if signalArgsStart == "\"" or signalArgsStart == "\'":#Ensure it is some form of string output
											signalARGS[2] = translationMethod(language,signalARGS[2])
											args = ",".join(signalARGS)
										else:
											args= secEntry
										secondList[secIndex]="signal("+args+")"
									else:
										textLine(secEntry,secondList,secIndex,language)
								except IndexError:
									print("E sepStringNested")
							firstList.pop(hackyIndex)
							firstList[hackyIndex:hackyIndex]=secondList
							hackyIndex +=secIndex
						else:#Everything else to be translated
							textLine(entry,firstList,hackyIndex,language)
							hackyIndex+=1
			except IndexError:
				pass
		return "".join(firstList)

	fileContents = readFile(absFileLocation)
	if absFileLocation.find("\\")>0:
		splitFile= absFileLocation.split("\\")
	else:
		splitFile= absFileLocation.split("/")
	fileName = re.sub("Parsed.txt","",splitFile[len(splitFile)-1],flags=re.IGNORECASE)
	fileLines = fileContents.split("\n")
	directory = ""
	startD = False
	
	parseF = parsedFolder[:len(parsedFolder)-1]
	for e in splitFile:
		if e == parseF and not startD:
			startD=True
			directory+=translationsFolder
		elif startD and e != fileName+"Parsed.txt":
			directory+=e+"/"
	outputFile = ""
	totalIters = len(fileLines)
	progressCharSpacing = 20
	for i, line in enumerate(fileLines):
		progress = (i+1)/totalIters
		progressChar = int(progress*progressCharSpacing)
		print(f"[{'#' * progressChar}{' ' * (progressCharSpacing - progressChar)}] {progress * 100:.1f}%", end='\r')
		colonSpaceIndex = line.find(": ")
		if colonSpaceIndex > -1:
			rawText = line[colonSpaceIndex+2:]
			operation = line[:1]
			operationOrder = line[:colonSpaceIndex]
			if operation == "T" or operation == "O" or operation=="S": #Only translate lines beginning with T|O|S
					translatedText = seperateString(rawText)
					outputFile+= f"{operationOrder}: {translatedText}\n"
			else:
				outputFile+= f"{operationOrder}: {rawText}\n"
		else:
			outputFile+="\n"

	saveFile(outputFile,fileName+f"[{language}]Parsed",directory)		##TODO This code also being a bitch

def translationMethod(language,input=""):
	if deepLEnabled:
		return deeplTranslate(language,input)
	else:
		return googleTranslator.translate(input,src=defaultLanguage,dest=language).text

def deeplTranslate(language:str,input = ""):
	"Core code behind deepL translation."
	lng = re.sub("\n","",language).split(" - ")[0]
	return deeplTranslator.translate_text(input,target_lang = lng).text

#endregion

#region backToJSON

def convertToJsonMulti():
	printPrefix = "Convert to Json | "
	dirlength = expensiveDirWalk(translationsFolder,"Parsed.txt")
	cur = 0
	size = len(dirlength)
	maxLen = len(str(size))
	formattedCur = f"{cur:0{maxLen}}"
	for i,e in enumerate(dirlength):
		formattedCur = f"{i:0{maxLen}}"
		cur = i
		print(f"{printPrefix}[{formattedCur}/{size}] | Current File: {e}")
		convertToJsonSingle(e)
	cur+=1
	formattedCur = f"{cur:0{maxLen}}"
	print(f"{printPrefix}[{formattedCur}/{size}] | Complete.\n")

def convertToJsonSingle(file):
	try:
		fileSplit= file.split("[")
		fileName = fileSplit[0]
		fileLanguage = fileSplit[1].split("]")[0]
		expensiveEntry = False
		if fileName.find("\\\\"):
			expensiveEntry = True
			origin = fileName.split("\\")
		subDirectories = ""
		for i, e in enumerate(origin):
			if i < len(origin)-1 and i != 0:
				subDirectories+=e+"\\"
		temp = 2
		originalJson = json.load(open(inputFolder+subDirectories+origin[len(origin)-1]+".json"))
		copyJson = originalJson
		if expensiveEntry:
			fileData = readFile(file)
		else:
			fileData = readFile(translationsFolder+file)
		undoneRegex = re.sub(r'\n',"",fileData)
		individualNodes =  undoneRegex.split("T: ")[1:]				#File will always start with 'T: '. thus this means that split will cause an empty list entry at the beginning, thus [1:]

		totalIters = len(individualNodes)
		progressCharSpacing = 20
		for indexPos, node in enumerate(individualNodes):
			progress = (indexPos+1)/totalIters
			progressChar = int(progress*progressCharSpacing)
			print(f"[{'#' * progressChar}{' ' * (progressCharSpacing - progressChar)}] {progress * 100:.1f}%", end='\r')
			goto = re.sub(r"G[0-9]+: ",parseToJsonDict["G"],node)
			options = re.sub(r"O[0-9]+: ",parseToJsonDict["O"],goto)
			singals = re.sub(r"S[0-9]+: ",parseToJsonDict["S"],options)
			closeBracket = re.sub(r"CB[0-9]+: ",parseToJsonDict["CB"],singals)
			openBracket = re.sub(r"OB[0-9]+: ",parseToJsonDict["OB"],closeBracket)
			ifSub = re.sub(r"I[0-9]+: ",parseToJsonDict["I"],openBracket)
			nLREGEX = re.sub(r"°","\\n",ifSub)

			individualNodes[indexPos] = nLREGEX
		
		for jsonIndexPos, item in enumerate(originalJson):
			commands_raw = item.get('commands_raw', None)
			if commands_raw is not None:
				if originalJson[jsonIndexPos].get('commands_raw',None) == commands_raw:
					copyJson[jsonIndexPos]["commands_raw"] = individualNodes[jsonIndexPos]
		
		saveJson(origin[len(origin)-1]+f"[{fileLanguage}]",copyJson,finalFolder+subDirectories)
	except Exception as error:
		print(f"E [Convert to Json]: {error}")

#endregion

#region CRUD File methods

def checkDirDependencies():
	"Checks if folders exist on run, if not make what's not existing.Also checks if settingsjson is configured"
	if not os.path.isdir(inputFolder):
		os.mkdir(inputFolder)
	if not os.path.isdir(parsedFolder):
		os.mkdir(parsedFolder)
	if not os.path.isdir(translationsFolder):
		os.mkdir(translationsFolder)
	if not os.path.isdir(finalFolder):
		os.mkdir(finalFolder)
	if not os.path.isfile("settings.json"):
		jsonSaveHandler()

def readFile(path):
	"Reads a file from a given path"
	try:
		with open(path, 'r', encoding="utf-8") as file:
			contents = file.read()
		return contents
	except FileNotFoundError:
		print(f"File '{path}' not found.")
		return None

def saveFile(contents, filename, folder,type=".txt"):
	"Saves a string to a given directory as a txt file"
	try:
		relativePath = folder + filename + type
		try:
			relativePath = re.sub("/","\\\\",relativePath)
		except Exception as e:
			print(e)
		relativePathSplit = relativePath.split("\\")
		directory = ""
		for i,e in enumerate(relativePathSplit): ##TODO Code is being a bitch
			if i < len(relativePathSplit)-1:
				directory+=e+"\\"
				if not os.path.isdir(directory):
					os.mkdir(directory)
		with open(directory+filename+type, "w",encoding="utf-8") as file:
			file.write(contents)
	except Exception as e:
		print(f"E saveFile: {e}")
	pass

def jsonSaveHandler(file={}):
	"Saving the users settings, or initalizing if not configured."
	filename="settings"

	if file:
		settings = file
	else:
		settings = {    
			"Use DeepL": False,
			"DeepL API Key": "",
			"Default Language": "en"
		}
	
	saveJson(filename,settings)

def saveJson(filename,contents,directory=""):
	"Saves <contents> into the <directory>/<filename>.json"
	try:
		finalAbsPath = directory+filename+".json"
		if not os.path.isdir(directory):
			steppingDir = ""
			splitDir = directory.split("\\")
			splitDir = [s for s in splitDir if s]
			for e in splitDir:
				steppingDir += e+"\\"
				if not os.path.isdir(steppingDir):
					os.mkdir(steppingDir)
		with open(finalAbsPath, "w") as file:
			json.dump(contents, file, indent=4)
	except Exception as e:
		print(f"e saveJson: {e}")

def expensiveDirWalk(directory,fileEndType):
	"Used to crawl through all subDirectories in <directory> to find all <fileEndType>s, if none will just pick up file normally"
	try:
		undoneFiles = []
		for root,dirs,files in os.walk(directory):
			for file in files:
				if file.endswith(fileEndType):
					undoneFiles.append(os.path.join(root,file))
		return undoneFiles
	except Exception:
		print(f"DIR [{directory}] does not exist.")

def findKey(value,dictionary):
	"Used to find the key of a certain value"
	for key,val in dictionary.items():
		if val == value:
			return key
	return None
#endregion

if __name__ == "__main__":
	checkDirDependencies()
	loadingSettings = True
	while loadingSettings:
		try:
			settingValues = json.load(open("settings.json"))
			loadingSettings = False
			loadedSettings=True
			deepLEnabled = settingValues["Use DeepL"]
			if deepLEnabled:
				authKey = settingValues["DeepL API Key"]
				deeplTranslator= deepl.Translator(authKey)
			else:
				googleTranslator = Translator()
			defaultLanguage = settingValues["Default Language"]
		except Exception as e:
			print(f"E LoadingSettings : {e}\nQuickFix: Delete \"settings.json\" and reload")
	main()