from PyQt5 import QtGui, QtCore, QtWidgets
import sys
from cparser import c_parser
from cparser.plyparser import ParseError, Coord
import semantic as smthc

from gui import design

def insertTokenIntoTable(table, token, column):
    #ttype, tvalue, tlineno, tlexpos = token.type, token.value, token.lineno, token.lexpos
    row_position = table.rowCount() 

    table.insertRow(row_position)
    table.setItem(row_position, 0, QtWidgets.QTableWidgetItem(str(token.type)))
    table.setItem(row_position, 1, QtWidgets.QTableWidgetItem(str(token.value)))
    table.setItem(row_position, 2, QtWidgets.QTableWidgetItem(str(token.lineno)))
    table.setItem(row_position, 3, QtWidgets.QTableWidgetItem(str(column)))

class ParserApp(QtWidgets.QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)

        self.actionOpen_file.setShortcut('Ctrl+O')
        self.actionOpen_file.setStatusTip('Open file')
        self.actionOpen_file.triggered.connect(self.openFileDialog)

        self.actionSave_file.setShortcut('Ctrl+S')
        self.actionSave_file.setStatusTip('Save file')
        self.actionSave_file.triggered.connect(self.saveFileDialog)

        self.actionAnalyze.setShortcut('Ctrl+Q')
        self.actionAnalyze.setStatusTip('Start lexer and parser')
        self.actionAnalyze.triggered.connect(self.analyzeCode)
        self.filename = ''

    def saveFileDialog(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        file, _ = QtWidgets.QFileDialog.getSaveFileName(self, 
            'Save source file', '', 'C code files (*.c);;Text files (*.txt);;All files (*)', options=options)

        if file:
            with open(file, 'w') as f:
                f.write(self.peCode.toPlainText())

    def openFileDialog(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog

        file, _ = QtWidgets.QFileDialog.getOpenFileName(self,
            'Open source file', '', 'C code files (*.c);;Text files (*.txt);;All files (*)', options=options)
        
        if file:
            self.filename = file
            with open(file, 'r') as f:
                data = f.read()
                self.peCode.setPlainText(data)

    def addTreeItems(self, parent, elements):

        for txt, children in elements:
            item = QtGui.QStandardItem(txt)
            parent.appendRow(item)
            if children:
                self.addTreeItems(item, children)

    def analyzeCode(self):
        # clear gui part
        data = self.peCode.toPlainText()
        self.tTokens.setRowCount(0)
        self.model = QtGui.QStandardItemModel()
        self.peLog.setPlainText('')
        self.treeTree.setModel(self.model)
        try:
            # lexical part
            parser = c_parser.CParser()
            parser.clex.build()
        
            parser.clex.input(data)
            self.tTokens.setColumnCount(4)
            self.tTokens.setHorizontalHeaderLabels(['Type', 'Value', 'Row', 'Column'])

            for token in parser.clex.lexer:
                insertTokenIntoTable(self.tTokens, token, parser.clex.find_tok_column(token))

            # self.tTokens.resizeColumnsToContents()
            
            # syntaxical part
            ast = parser.parse(data, filename=self.filename)
            tree = []
            ast.write(tree)

            self.model = QtGui.QStandardItemModel()
            self.addTreeItems(self.model, tree)
            self.treeTree.setModel(self.model)
            self.model.setHorizontalHeaderLabels(['Tree'])
            self.treeTree.expandAll()
            
            # semathic part
            smthc.global_scope = []
            state = smthc.stt()
            smthc.check_children_scopes(ast, state)
            
        except ParseError as error:
            # error handling for gui
            from datetime import datetime

            error_line = str(datetime.now()) + ' :: Error during parsing happened: {}'.format(error)
            self.peLog.setPlainText(error_line)


def main():
    app = QtWidgets.QApplication(sys.argv)
    form = ParserApp()
    form.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()