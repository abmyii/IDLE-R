from PySide import QtCore, QtGui
import re
import time

class CodeAnalyser(QtCore.QObject):
    
    def __init__(self, editor):
        self._editor = editor
    
    def analyse(self):
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
        # Find if there is a way to make re match with matched strings
        variables = re.findall('([a-zA-Z_]\w*)\s*=\s*([^;\n]*)', text)
        
        # find functions
        functions = re.findall('def\s+([a-zA-Z_]\w*)\s*\((.*)\)', text)
        
        # find classes
        # NOTE: Join with lower regexp?
        classes = re.findall('class\s+([a-zA-Z_]\w*)\s*', text)
        # NOTE: Do we need this?
        classes_parents = re.findall('class\s+[a-zA-Z_]\w*\s*\((.*)\)', text)
        # NOTE: Merge with functions?
        class_functions = re.findall('def\s+([_]\w*)\s*\((.*)\)', text)
        print classes, classes_parents, class_functions
        print len(classes), len(classes_parents), len(class_functions)
        
        # find imports
        imports = re.findall('import\s+([a-zA-Z\.][\w\.]*)', text)
        from_imports = re.findall(
         'from\s+([a-zA-Z\.][\w\.]*)\s+import\s+([a-zA-Z\.][\w\.]*)',
         text)
         
        # Return the analysis info
        #return comments, lambdas, variables, classes, functions, imports, from_imports
        print('Analysis took: {} s'.format(time.time() - start_time))
        print('Comments: {}'.format(comments))
        print('Lambdas: {}'.format(lambdas))
        print('Variables: {}'.format(variables))
        print('Functions: {}'.format(functions))
        print('Classes: {}'.format(classes))
        print('Imports: {}'.format(imports))
        print('From-Imports: {}'.format(from_imports))

class PythonCompleter(QtGui.QCompleter):
	def __init__(self, editor, db=None):
		# make the wordlist
		self.wordlist = ['import', 'print']

		# setup the completer
		QtGui.QCompleter.__init__(self, sorted(self.wordlist), editor)
		self.setModelSorting(QtGui.QCompleter.CaseSensitivelySortedModel)
		self.setWrapAround(False)
