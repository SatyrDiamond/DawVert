# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import sys
from PyQt6 import QtWidgets, uic, QtCore, QtGui
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QFileDialog

from objects import core as dv_core
from pathlib import Path
from functions import plug_conv
from threading import Thread
import traceback

from objects.convproj import fileref
from objects.exceptions import ProjectFileParserException
filesearcher = fileref.filesearcher

scriptfiledir = os.path.dirname(os.path.realpath(__file__))

plug_conv.load_plugins()

from objects_ui.ui_pyqt import Ui_MainWindow

class converterstate():
	is_converting = False

convprocess = {}
def process_converter(qt_obj):
	try:
		converterstate.is_converting = True
		dawvert_core = qt_obj.dawvert_core

		dawvert_core.config.load('./__config/config.ini')

		inname = dawvert_core.input_get_current_name()
		outname = dawvert_core.output_get_current_name()

		in_file = qt_obj.ui.InputFilePath.text()
		out_file = qt_obj.ui.OutputFilePath.text()

		file_name = os.path.splitext(os.path.basename(in_file))[0]

		dawvert_core.config.path_samples_extracted += file_name + '/'
		dawvert_core.config.path_samples_downloaded += file_name + '/'
		dawvert_core.config.path_samples_generated += file_name + '/'
		dawvert_core.config.path_samples_converted += file_name + '/'

		os.makedirs(dawvert_core.config.path_samples_extracted, exist_ok=True)
		os.makedirs(dawvert_core.config.path_samples_downloaded, exist_ok=True)
		os.makedirs(dawvert_core.config.path_samples_generated, exist_ok=True)
		os.makedirs(dawvert_core.config.path_samples_converted, exist_ok=True)

		filesearcher.reset()
		filesearcher.add_basepath('projectfile', os.path.dirname(in_file))
		filesearcher.add_basepath('dawvert', scriptfiledir)

		filesearcher.add_searchpath_partial('projectfile', '.', 'projectfile')

		filesearcher.add_searchpath_full_filereplace('extracted', dawvert_core.config.path_samples_extracted, None)
		filesearcher.add_searchpath_full_filereplace('downloaded', dawvert_core.config.path_samples_downloaded, None)
		filesearcher.add_searchpath_full_filereplace('generated', dawvert_core.config.path_samples_generated, None)
		filesearcher.add_searchpath_full_filereplace('converted', dawvert_core.config.path_samples_converted, None)
		filesearcher.add_searchpath_full_filereplace('external_data', os.path.join(scriptfiledir, '__external_data'), None)

		qt_obj.ui.SubStatusText.setText('Processing Input...')
		dawvert_core.parse_input(in_file, dawvert_core.config)
		qt_obj.ui.progressBar.setValue(25)
		qt_obj.ui.SubStatusText.setText('Converting Project Type and Samples...')
		dawvert_core.convert_type_output(dawvert_core.config)
		qt_obj.ui.progressBar.setValue(50)
		qt_obj.ui.SubStatusText.setText('Converting Plugins...')
		dawvert_core.convert_plugins(dawvert_core.config)
		qt_obj.ui.progressBar.setValue(75)
		qt_obj.ui.SubStatusText.setText('Processing Output...')
		dawvert_core.parse_output(out_file)
		qt_obj.ui.progressBar.setValue(100)
		qt_obj.ui.StatusText.setText('Status: OK')
		qt_obj.ui.SubStatusText.setText('')
	except ProjectFileParserException:
		converterstate.is_converting = False
		ex_type, ex_value, ex_traceback = sys.exc_info()
		qt_obj.ui.StatusText.setText('Status: Project File Error')
		qt_obj.ui.SubStatusText.setText(str(ex_value))
	except SystemExit:
		converterstate.is_converting = False
		ex_type, ex_value, ex_traceback = sys.exc_info()
		qt_obj.ui.StatusText.setText('Status: Exited with no output')
		qt_obj.ui.SubStatusText.setText('See Console.')
		print(traceback.format_exc())
	except:
		converterstate.is_converting = False
		ex_type, ex_value, ex_traceback = sys.exc_info()
		qt_obj.ui.StatusText.setText('Status: Error. See Console.')
		qt_obj.ui.SubStatusText.setText(ex_type.__name__+': '+str(ex_value))
		print(traceback.format_exc())
	converterstate.is_converting = False

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
	def __init__(self, *args, obj=None, **kwargs):
		super(MainWindow, self).__init__(*args, **kwargs)

		wid = QtWidgets.QWidget(self)
		self.ui = Ui_MainWindow()
		self.ui.setupUi(wid)
		self.setWindowTitle('DawVert - The DAW Converter')
		self.setWindowIcon(QtGui.QIcon('icon.png'))
		self.setCentralWidget(wid)
		self.setAcceptDrops(True)

		layout = QtWidgets.QVBoxLayout()

		self.ui.InputFileButton.clicked.connect(self.__choose_input)
		self.ui.OutputFileButton.clicked.connect(self.__choose_output)
		self.ui.ListWidget_InPlugSet.currentRowChanged.connect(self.__change_input_plugset)
		self.ui.ListWidget_InPlugin.currentRowChanged.connect(self.__change_input_plugin_nofb)

		self.ui.ListWidget_OutPlugSet.currentRowChanged.connect(self.__change_output_plugset)
		self.ui.ListWidget_OutPlugin.currentRowChanged.connect(self.__change_output_plugin)

		self.ui.ConvertButton.setEnabled(False)
		self.ui.ConvertButton.clicked.connect(self.__do_convert)

		self.ui.AutoDetectButton.clicked.connect(self.__do_auto_detect)

		self.dawvert_core = dv_core.core()

		for x in self.dawvert_core.input_get_pluginsets_names():
			self.ui.ListWidget_InPlugSet.addItem(x)

		for x in self.dawvert_core.output_get_pluginsets_names():
			self.ui.ListWidget_OutPlugSet.addItem(x)

		self.__update_convst()

	def dragEnterEvent(self, event):
		if event.mimeData().hasUrls():
			event.accept()
		else:
			event.ignore()

	def dropEvent(self, event):
		files = [u.toLocalFile() for u in event.mimeData().urls()]
		for f in files:
			self.ui.InputFilePath.setText(f)
			self.ui.OutputFilePath.setText(f.rsplit('.',1)[0])
			self.__do_auto_detect()

	def __choose_input(self):
		filename, _filter = QFileDialog.getOpenFileName(
			self,
			"Open File",
			"",
			"",
		)
		self.ui.InputFilePath.setText(filename)

	def __choose_output(self):
		filename, _filter = QFileDialog.getSaveFileName(
			self,
			"Open File",
			"",
			"",
		)
		self.ui.OutputFilePath.setText(filename)

	def __do_auto_detect(self):
		filename = self.ui.InputFilePath.text()
		if os.path.exists(filename):
			try:
				detect_plugin_found = self.dawvert_core.input_autoset(filename)
				plugnames = self.dawvert_core.input_get_plugins()
				if detect_plugin_found:
					self.ui.ListWidget_InPlugin.setCurrentRow(plugnames.index(detect_plugin_found))
					return True
				else:
					outshort = self.dawvert_core.input_autoset_fileext(filename)
					if outshort:
						self.ui.ListWidget_InPlugin.setCurrentRow(plugnames.index(outshort))
						return outshort != None
			except:
				pass

	def __update_convst(self):
		in_file = self.ui.InputFilePath.text().replace('/', '\\')
		out_file = self.ui.OutputFilePath.text().replace('/', '\\')
		inplug = self.dawvert_core.input_get_current()
		outplug = self.dawvert_core.output_get_current()
		not_same = in_file!=out_file
		out_exists = not os.path.exists(out_file)
		in_usable, in_usable_msg = self.dawvert_core.input_get_usable()
		out_usable, out_usable_msg = self.dawvert_core.output_get_usable()
		outstate = bool(inplug and outplug and not_same and out_exists and in_usable)

		self.ui.ConvertButton.setEnabled(outstate and not converterstate.is_converting)
		if converterstate.is_converting: 
			self.ui.StatusText.setText('Status: Converting')
			self.ui.SubStatusText.setText('')
		elif not outstate:
			self.ui.StatusText.setText('Status: Not Ready')
			if not in_file: self.ui.SubStatusText.setText('No input file.')
			elif not out_file: self.ui.SubStatusText.setText('No output file.')
			elif not inplug: self.ui.SubStatusText.setText('Input plugin not selected.')
			elif not outplug: self.ui.SubStatusText.setText('Output plugin not selected.')
			elif not not_same: self.ui.SubStatusText.setText('Not overwriting input file.')
			elif not out_exists: self.ui.SubStatusText.setText('Not overwriting output file.')
			elif not in_usable: 
				self.ui.StatusText.setText('Status: Input Plugin Unusable')
				self.ui.SubStatusText.setText(in_usable_msg)
			elif not out_usable: 
				self.ui.StatusText.setText('Status: Output Plugin Unusable')
				self.ui.SubStatusText.setText(out_usable_msg)
		else:
			self.ui.StatusText.setText('Status: Ready')
			self.ui.SubStatusText.setText('')


	def __change_input_plugset(self, num):
		plugsetname = self.dawvert_core.input_get_pluginsets_index(num)
		self.dawvert_core.input_load_plugins(plugsetname)
		self.__update_input_plugins()
		self.__change_input_plugin(0)

	def __change_input_plugin(self, num):
		pluginname = self.dawvert_core.input_get_plugins_index(num)
		if pluginname: self.dawvert_core.input_set(pluginname)
		else: 
			plugnames = self.dawvert_core.input_get_plugins()
			if plugnames: self.dawvert_core.input_set(plugnames[0])
		self.__update_convst()

	def __change_input_plugin_nofb(self, num):
		pluginname = self.dawvert_core.input_get_plugins_index(num)
		if pluginname: self.dawvert_core.input_set(pluginname)
		self.__update_convst()

	def __update_input_plugins(self):
		self.ui.ListWidget_InPlugin.clear()
		for x in self.dawvert_core.input_get_plugins_names():
			self.ui.ListWidget_InPlugin.addItem(x)

	def __change_output_plugset(self, num):
		plugsetname = self.dawvert_core.output_get_pluginsets_index(num)
		self.dawvert_core.output_load_plugins(plugsetname)
		self.__update_output_plugins()
		self.__change_output_path()

	def __change_output_plugin(self, num):
		pluginname = self.dawvert_core.output_get_plugins_index(num)
		if pluginname: self.dawvert_core.output_set(pluginname)
		self.__update_convst()
		self.__change_output_path()

	def __change_output_path(self):
		outfound = self.dawvert_core.output_get_current()
		filename = self.ui.OutputFilePath.text()
		if outfound and filename:
			try:
				fileext = self.dawvert_core.output_get_extension()
				filename = Path(filename)
				filename = filename.with_suffix('.'+fileext)
				self.ui.OutputFilePath.setText(str(filename))
			except:
				pass
		self.__update_convst()

	def __update_output_plugins(self):
		self.ui.ListWidget_OutPlugin.clear()
		for x in self.dawvert_core.output_get_plugins_names():
			self.ui.ListWidget_OutPlugin.addItem(x)

	def __do_convert(self):
		thread1 = Thread(target = process_converter, args = (self,))
		thread1.start()
		self.__update_convst()

app = QtWidgets.QApplication(sys.argv)

window = MainWindow()
window.show()
app.exec()