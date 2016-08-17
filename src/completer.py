from PySide import QtCore, QtGui
import re
import time

class Completer(QtGui.QCompleter):
    
    def __init__(self, parent, stringList=[]):
        if stringList:
            QtGui.QCompleter.__init__(self, stringList, parent)
        else:
            QtGui.QCompleter.__init__(self, parent)
        
        # Default setup
        self.setCaseSensitivity(QtCore.Qt.CaseSensitive)
        self.setWidget(parent)
        self.setCompletionMode(self.PopupCompletion)
        self.connect(self, QtCore.SIGNAL("activated(const QString&)"), self.onActivated)
    
    def onActivated(self, completion):
        self.parent().complete(completion, self.completionPrefix())
    
    def showCompleter(self):
        # DON'T COMPLETE IF THERE IS ONLY ONE OPTION (just pick first option)
        # Set the start index for completing
        popup = self.popup()
        popup.setCurrentIndex(self.completionModel().index(0,0))
        
        # Start completing
        rect = self.parent().cursorRect()
        rect.setWidth(self.popup().sizeHintForColumn(0)
            + self.popup().verticalScrollBar().sizeHint().width())
        rect.moveTopLeft(self.parent().cursorRect().bottomRight())
        rect.translate(0, -self.parent().font().pointSize())
        self.complete(rect)

def process_variables(variables):
    # Processes the variables list and outputs a dict with the
    # variable name as the key and value as the item
    variables_dict = {}
    for variable in variables:
        if len(variable) == 2:
            # Check if the variable's value is a chain assignment
            value = variable[1]
            names = []
            if re.findall('([a-zA-Z_]\w*)\s*=\s*([^;\n]*)', value):
                names += variable[0]
                # If so, keep looping until we get to the actual value
                while True:
                    find = re.findall('([a-zA-Z_]\w*)\s*=\s*([^;\n]*)', value)
                    if find:
                        # If the current item of the chain is a variable name
                        # add it to the names list
                        names += find[0][0]
                        value = find[0][1]
                    else:
                        break
                # Set all of the variable names in the names list to 'value'
                variables_dict.update(dict.fromkeys(names, value))
            else:
                # Otherwise put the variable into the dict
                variables_dict[variable[0]] = variable[1]
    # If any variable is linked to another, set it's value to the others value
    for variable in variables_dict.copy():
        value = variables_dict[variable]
        variables_dict[variable] = variables_dict.get(value, value)
        # Remove empty variables (this will probably go when I fix the regex)
        # problem below in the variables section
        if not variables_dict[variable]:
            variables_dict.pop(variable)
    # Convert values to int/float if possible
    # Eval values (so that all of the values will be picked up by eval?)
    for key in variables_dict:
        # Get the variable value
        item = variables_dict[key]
        try:
            # Try to convert to int
            variables_dict[key] = int(item)
        except ValueError:
            # We would only get a ValueError if the item is a number but not int
            try:
                # Try to convert to float
                variables_dict[key] = float(item)
            except ValueError:
                # This might be because the number has more than 1 . in it
                pass
    return variables_dict

class CodeAnalyser(QtCore.QObject):
    
    def __init__(self, editor):
        self._editor = editor
    
    def analyse(self):
        # Make all of the re's sets so that we don't get two identical matches
        start_time = time.time()
        
        text = self._editor.toPlainText()
        
        # find comments and then remove them for the text we are analysing
        # so we don't get code confused with comments
        self.comments = re.findall('(#.*)', text)
        text = re.sub('(#.*)', '', text)
        
        # find lambdas and then remove them so we don't get them
        # confused with variables
        self.lambdas = re.findall('([a-zA-Z]\w*)\s*=\s*lambda\s+(.+):', text)
        text = re.sub('([a-zA-Z]\w*)\s*=\s*lambda\s+(.+):', '', text)
        
        # find variables
        # work out how to catch variables that are blocked by the ([^;\n]*)
        # (i.e variables defined on two lines or that has \ or ; in a string)
        variables = re.findall('([a-zA-Z_]\w*)\s*=\s*([^;\n]*)', text)
        self.variables = process_variables(variables)
        
        # find functions
        self.functions = re.findall('def\s+([a-zA-Z_]\w*)\s*\((.*)\)', text)
        
        # find classes
        classes = re.findall('class\s+([a-zA-Z_]\w*)\s*(\(.*\))*:', text)
        self.classes = map(lambda m: [m[0], re.sub('[()]', '', m[1])], classes)
        # NOTE: Make sure this gets ALL of the class functions and the above
        #  functions re doesn't get the class ones (or at least knows that they
        #  are from the class).
        self.class_functions = re.findall('def\s+([_]\w*)\s*\((.*)\)', text)
        #print classes, class_functions
        #print len(classes), len(class_functions)
        
        # find imports
        self.imports = re.findall('import\s+([a-zA-Z\.][\w\.]*)', text)
        self.from_imports = re.findall(
         'from\s+([a-zA-Z\.][\w\.]*)\s+import\s+([a-zA-Z\.][\w\.]*)',
         text)
         
        # Print the analysis info (debug)
        print('Analysis took: {} s'.format(time.time() - start_time))
        print('Comments: {}'.format(self.comments))
        print('Lambdas: {}'.format(self.lambdas))
        print('Variables: {}'.format(self.variables))
        print('Functions: {}'.format(self.functions))
        print('Classes: {}'.format(self.classes))
        print('Imports: {}'.format(self.imports))
        print('From-Imports: {}'.format(self.from_imports))

class Autocompleter(dict):
    
    def __init__(self):
        self.modules = {}
    
    def add_module(self, module):
        # Use hasattr to determine if the module has the __dict__ attr?
        # Auto-import using __import__?
        self[module.__name__] = module.__dict__
        self.modules[module.__name__] = module
	
	def autocomplete(self, section, text):
        # Use __dict__ attr of ANY object (add that special variable to AC)
        # Or dir if there isn't any
		text = set(text)
		return [comp for comp in self[section] if text.issubset(comp.lower())]
    
    def __getitem__(self, obj):
        completions = list(self.get(obj))
        if obj in self.modules.keys() and hasattr(self.modules[obj], '__dict__') \
           or hasattr(self.get(obj), '__dict__'):
            completions.append('__dict__')
        return sorted(completions)

# DEFUNCT: Replaced by Autocompleter
# OR: Use with autocompleter as frontend to display matches
class PythonCompleter(QtGui.QCompleter):
	def __init__(self, editor, db=None):
		# make the wordlist
		self.wordlist = ['import', 'print']

		# setup the completer
		QtGui.QCompleter.__init__(self, sorted(self.wordlist), editor)
		self.setModelSorting(QtGui.QCompleter.CaseSensitivelySortedModel)
		self.setWrapAround(False)
