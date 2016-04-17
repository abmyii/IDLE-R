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
        variables = re.findall('([a-zA-Z_]\w*)\s*=', text)
        
        # find functions
        functions = re.findall('def\s+([a-zA-Z_]\w*)\s*\((.*)\)', text)
        
        # find classes
        classes = re.findall('class\s+([a-zA-Z_]\w*)\s*', text)
        class_functions = re.findall('def\s+([_]\w*)\s*\((.*)\)', text)
        
        # find imports
        # NOTE: process (from)/imports?
        imports = re.findall('import\s+([a-zA-Z\.][\w\.]*)', text)
        from_imports = re.findall(
         'from\s+([a-zA-Z\.][\w\.]*)\s+import\s+([a-zA-Z\.][\w\.]*)',
         text)
         
        # Return the analysis info
        print('Analysis took: {} s'.format(time.time() - start_time))
        #return comments, lambdas, variables, classes, functions, imports, from_imports
        #print(comments, lambdas, variables, classes, functions, imports, from_imports)
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
