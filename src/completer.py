from PySide import QtCore, QtGui
import re
import time

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
        comments = re.findall('(#.*)', text)
        text = re.sub('(#.*)', '', text)
        
        # find lambdas and then remove them so we don't get them
        # confused with variables
        lambdas = re.findall('([a-zA-Z]\w*)\s*=\s*lambda\s+(.+):', text)
        text = re.sub('([a-zA-Z]\w*)\s*=\s*lambda\s+(.+):', '', text)
        
        # find variables
        # work out how to catch variables that are blocked by the ([^;\n]*)
        # (i.e variables defined on two lines or that has \ or ; in a string)
        variables = re.findall('([a-zA-Z_]\w*)\s*=\s*([^;\n]*)', text)
        variables = process_variables(variables)
        
        # find functions
        functions = re.findall('def\s+([a-zA-Z_]\w*)\s*\((.*)\)', text)
        
        # find classes
        classes = re.findall('class\s+([a-zA-Z_]\w*)\s*(\(.*\))*:', text)
        classes = map(lambda m: [m[0], re.sub('[()]', '', m[1])], classes)
        # NOTE: Make sure this gets ALL of the class functions and the above
        #  functions re doesn't get the class ones (or at least knows that they
        #  are from the class).
        class_functions = re.findall('def\s+([_]\w*)\s*\((.*)\)', text)
        #print classes, class_functions
        #print len(classes), len(class_functions)
        
        # find imports
        imports = re.findall('import\s+([a-zA-Z\.][\w\.]*)', text)
        from_imports = re.findall(
         'from\s+([a-zA-Z\.][\w\.]*)\s+import\s+([a-zA-Z\.][\w\.]*)',
         text)
         
        # Return the analysis info
        #print('Analysis took: {} s'.format(time.time() - start_time))
        #print('Comments: {}'.format(comments))
        #print('Lambdas: {}'.format(lambdas))
        #print('Variables: {}'.format(variables))
        #print('Functions: {}'.format(functions))
        #print('Classes: {}'.format(classes))
        #print('Imports: {}'.format(imports))
        #print('From-Imports: {}'.format(from_imports))
        #return comments, lambdas, variables, classes, functions, imports, from_imports
        return variables

class PythonCompleter(QtGui.QCompleter):
	def __init__(self, editor, db=None):
		# make the wordlist
		self.wordlist = ['import', 'print']

		# setup the completer
		QtGui.QCompleter.__init__(self, sorted(self.wordlist), editor)
		self.setModelSorting(QtGui.QCompleter.CaseSensitivelySortedModel)
		self.setWrapAround(False)
