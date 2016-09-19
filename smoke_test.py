#!/usr/bin/ python
# -*- coding: utf-8 -*-
#########################################################################################
# Version 0.7
#
# Opens a document in the app that you test, takes a screenshot of the document and compares it with a
# standard one. Test is passed if the screenshots are equal. With a command line key, the 
# script can update the standard screenshots (in case the software or test documents was changed).
#
# The application under test is responsible for opening documents in a window of proper size and 
# at a proper scale. Make sure that the application's window appears in the middle of the screen
# what is needed to take a screenshot.
# Prefer using horizontal documents since they fit the screen the best.
#
# Author:  Mykola Shubin
# Licence: MIT
# Source:  https://github.com/nisb/smoke_test
#
# Changes:
# Version 0.1:
# - First release.
# Version 0.2:
# - Comparing screenshots directly instead of using Sikuli's exists() function.
#   The latter is not enough accurate and treats a wrong image as the correct one 
#   (false positive).
# Version 0.3:
# - Added the possibility to create standard screenshots automatically (-u command line key).
# - Added the Document class to manage documents, screenshots and comparison.
# - It's possible to open all test documents in one program session to increase performance.
# - Store screenshots and documents in the same folder.
# - Command line arguments support.
# - Can create screenshots in one app version (stable) and then test another. 
#   Two paths to app versions are supported.
# Version 0.4:
# - Read settings from a file.
# - To avoid many paths as input parameters, all test data are stored in one folder. The script
#   gets the path to this folder. Then standard paths are used. Example:
#   /SmokeTest/					- root, the path to it should be the script argument
#   /SmokeTest/setup.txt		- test settings (input data)
#   /SmokeTest/documents/		- test documents are here (input data)
#   /SmokeTest/failed_tests/	- data on failed tests (created as script output)
# Version 0.5
# - Moved the definitions for paths to the Trash and Desktop inside classes.
# Version 0.6
# - Turned the global constant SCREENSHOT_FILE_EXTENSION into a property of the class Screenshot() 
#   which is Screenshot.extension now. The script reads this parameter from setup.txt
# - The global DELAY constant was turned into the class GlobalDelay to be able to read this 
#   parameter from setup.txt in another module, and then pass it here to the superclass. 
#   This eliminates the need to define DELAY in each module.
# - Added a static variable in a class to hold the global delay.
# Version 0.7
# - Refactoring of main()
# 
# To Do:
# - ? Multiple screenshots per document support: 
#   make preparations, take a screenshot; make preparations, take a screenshot; ...
# - ? Multi-page document support. This is a special case of many screenshots per document.
#   
# 
#########################################################################################

from sikuli import *
import os
from os.path import expanduser
import filecmp
import sys
import getopt
import re
import datetime


#----------------------------------------------------------------------------------------
# takes and compares screenshots
# if file_name is given, it can create a new standard screenshot
class Screenshot():
	"""
		Create standard screenshots from a released version of a program under test.
		Create screenshots of a new version of a program under test.
		Compare the screenshots above and, if different, report that a test has failed.
	"""
	
	# paths to screenshots
	screenshot = ""
	screenshot_standard = ""

	file_name = "" # the name for a new standard screenshot. used in the screenshot creation mode

	def __init__(self, standard, name = ""):
		self.screenshot_standard = standard
		self.file_name = name
		# set up the environment
		self.DESKTOP = expanduser('~') + os.sep + "Desktop" + os.sep
	# end def __init__


	@staticmethod
	def set_extension(ext):
		""" Set up the screenshot file extension. It is specific to the OS and constant. """
		Screenshot.extension = ext
	# end def set_extension

	@staticmethod
	def get_extension():
		""" Get the screenshot file extension. """
		return Screenshot.extension
	# end def get_extension


	# take a screenshot of the active window
	def take_screenshot(self):
		""" Take a screenshot. Low level realisation. """
		wait(GlobalDelay.get())
		type('4', Key.CMD + Key.SHIFT)
		type(' ')
		click()
		wait(GlobalDelay.get())
	# end def take_screenshot


	# get the last screenshot
	def get_last(self):
		""" Find the last screenshot on disk. """
		all_screenshots = []
		for file in os.listdir(self.DESKTOP):
			if file.startswith("Screen Shot ") and file.endswith(Screenshot.get_extension()):
				all_screenshots.append(file)
		all_screenshots.sort()
		return (self.DESKTOP + all_screenshots[len(all_screenshots) - 1])
	# end def get_last


	def take(self):
		""" Take a screenshot. """
		self.take_screenshot()
		self.screenshot = self.get_last()
	# end def take_correct


	# compare taken screenshot with a standard
	def compare(self):
		""" Compare the taken screenshot with a standard one. """
		if filecmp.cmp(self.screenshot, self.screenshot_standard):
			passed = True
		else:
			passed = False
		return passed
	# end def compare


	# take a new standard screenshot
	def create(self):
		""" Take a new standard screenshot. """
		self.take()
		wait(GlobalDelay.get() * 2)
		try:
			os.rename(self.screenshot, (self.DESKTOP + self.file_name + Screenshot.get_extension()))
		except OSError as msg:
			print msg
		return (self.DESKTOP + self.file_name + Screenshot.get_extension()) # path to created screenshot
	# end def create


	def get_path(self):
		""" Get the path to the curent screenshot. """
		return self.screenshot
	# end def get_path

# end class Screenshot


class Document():
	""" Class to work with test documents. """

	screenshot_path = ""
	error_log_path = ""	# to save not matched screenshots

	def __init__(self, doc_path, application_path, update_screenshots_mode = False):
		self.document_path = doc_path
		self.app_path = application_path
		self.document_folder = doc_path.rpartition(os.sep)[0]
		self.document_name = doc_path.rpartition(os.sep)[2].rpartition(".")[0]
		if update_screenshots_mode:
			self.scrn = Screenshot("", self.document_name)
			return
		self.screenshot_path = self.get_standard_screenshot_path()
		if self.screenshot_path == None:
			msg = "No screenshots for " + self.document_name + " found"
			raise OSError(msg)
		self.scrn = Screenshot(self.screenshot_path, self.document_name)
		
		if len(self.get_error_log_path()) == 0:
			Document.error_log_path = self.document_folder.rpartition(os.sep)[0] + os.sep + self.get_curr_date_time()

		# set up the environment
		self.TRASH = expanduser('~') + os.sep + ".Trash"
	# end def __init__


	def get_curr_date_time(self):
		""" Create a unique name for a log folder in each test session. """
		curr = datetime.datetime.now().timetuple()
		name = "Failed_Tests"
		for item in range(0, 5):
			name += "_" + str(curr[item])
		return name
	# end def get_curr_date_time


	@staticmethod
	def get_error_log_path():
		return Document.error_log_path
	# end def get_error_log_path


	def open(self):
		""" Open a document. """
		command = 'open \'' + self.app_path + '\' \'' + self.document_path + '\''
		os.system(command)
		wait(GlobalDelay.get() * 8) # choose 8 - 10
	# end def open


	def close(self):
		""" Close a document. """
		type('w', Key.CMD) # close the document
		wait(GlobalDelay.get() * 4)
	# end def close


	# compare what's on the screen with the standard
	def check(self):
		""" Compare how the test document was shown on the screen with the standard one. """
		self.scrn.take()
		result = self.scrn.compare()
		if result:
			self.delete_screenshot()
		else:
			self.save_screenshot()
		return result
	# end def check


	# create a new standard screenshot
	def update_standard_screenshot(self):
		""" Update the screenshot of a standard document. """
		path = self.scrn.create()
		try:
			if os.path.exists(self.screenshot_path):
				# delete old screenshot
				os.rename(self.document_folder + os.sep + self.document_name + Screenshot.get_extension(), 
					self.TRASH + os.sep + self.document_name + Screenshot.get_extension())
			# update the old screenshot with a new one
			os.rename(path, self.document_folder + os.sep + self.document_name + Screenshot.get_extension()) 
		except OSError as msg:
			print msg, self.document_name
	# end def update_standard_screenshot


	# can be extended to work with several screenshots per document
	def get_standard_screenshot_path(self):
		""" Find created screenshot on the disk. """
		all_screenshots = []
		for file in os.listdir(self.document_folder):
			if file.startswith(self.document_name) and file.endswith(Screenshot.get_extension()):
				all_screenshots.append(self.document_folder + os.sep + file)
		if len(all_screenshots) == 0:
			return None
		all_screenshots.sort()
		return all_screenshots[0]
	# end def get_standard_screenshot_path


	def get_document_name(self):
		""" Get the test document name. """
		return self.document_name
	# end def get_document_name


	def save_screenshot(self):
		""" Save not matched screenshot to error folder for examination. """
		try:
			if not os.path.exists(self.error_log_path):
				os.makedirs(self.error_log_path)
			screenshot_path_in_log_folder = self.error_log_path + os.sep + self.document_name + Screenshot.get_extension()
			os.rename(self.scrn.get_path(), screenshot_path_in_log_folder)
		except OSError as msg:
			print msg, self.document_name
	# end def save_screenshot


	def delete_screenshot(self):
		""" Delete matched screenshot. """
		try:
			if os.path.exists(self.screenshot_path):
				os.rename(self.scrn.get_path(), self.TRASH + os.sep + self.scrn.get_path().rpartition(os.sep)[2])
		except OSError as msg:
			print msg, self.document_name
	# end def delete_screenshot

# end class Document


class Settings():
	""" Read script settings from a file and give them as dictionary values by keys. """
	settings = {}
	SETUP_FILE = "setup.txt"

	def __init__(self, path):
		self.path = path
	# end def __init__


	def read_settings(self):
		""" Read settings from a file. """
									# no space or tab symbol(s) is allowed before or after '='
									# no space or tab symbol(s) is allowed in the parameter name
									# no comments are allowed in the same line with data
									# more than one '=' per line isn't allowed
									#		# comment
									# examples:
		VALUE = "\w+=(.|/|\\|'|\")*\w+"
									#		path=/Applications/program.app
									#		repeat=3
		LIST_START = "\w+="			#		docs=
									#		document1.txt
									#		document2.txt
									# the end of list is a comment or end of file
		WRONG_FORMAT = "(==+)|( +=)|(= +)|(=\w+ *\w*=)|((?:\w+ +\w+)+=)"

		regex_value = re.compile(VALUE, re.U)
		regex_list_start = re.compile(LIST_START, re.U)
		regex_wrong_format = re.compile(WRONG_FORMAT, re.U)

		try:
			with open(self.path + self.SETUP_FILE, 'r') as input_file:
				list_in_progress = False  # when true, the next line can be a list item
				for line in input_file:
					# skip non-data lines
					match = re.findall(regex_wrong_format, line)
					# check for:	wrong format
					# 				too short line
					# 				comment
					# 				parameter name is missing
					if len(match) > 0 or \
					  len(line) <= 2 or \
					  line[0:1] == "#" or \
					  line[0:1] == "=":
						list_in_progress = False  # no list items are expected in the following line
						continue  # skip empty lines

					if line[-1] == "\n": line = line[0:-1]  # remove trailing "new line" symbol
					# check what kind of data is in the current line
					if not list_in_progress:
						# value or start of a list
						match = re.findall(regex_value, line)
						if len(match) >= 1:
							# value
							list_in_progress = False
							(parameter, value) = line.split("=")
							self.settings[parameter] = value
						else:
							match = re.findall(regex_list_start, line)
							if len(match) >= 1:
								# start of a list
								list_in_progress = True
								(parameter, value) = line.split("=")
								self.settings[parameter] = []
					else:
						# list item
						self.settings[parameter].append(line)
			return True
		except IOError as ioerr:
			print 'File error: ' + str(ioerr)
			return False
	# end def read_settings


	def get_parameter(self, parameter):
		""" Get a string or list from settings. """
		return self.settings[parameter]
	# end def get_parameter
	

	def get_int_parameter(self, parameter):
		""" Get a numeric parameter. """
		return int(self.settings[parameter])
	# end def get_int_parameter


	def get_float_parameter(self, parameter):
		""" Get a numeric parameter. """
		return float(self.settings[parameter])
	# end def get_float_parameter

# end class Settings


class GlobalDelay():
	"""
		Storage for the global delay value in ms.
		It is intended to pass the value from a sub-class defined in another module.
	"""

	@staticmethod
	def set(input_delay):
		# check if the delay value is in the reasonable range (ms)
		if (0.01 < input_delay < 20):
			GlobalDelay.delay = input_delay
		else:
			raise ValueError("GlobalDelay is out of range.")

	@staticmethod
	def get():
		return GlobalDelay.delay

# end class GlobalDelay


def open_the_app(app_path, the_app):
	""" Open the app under test. """
	command = 'open \'' + app_path + '\''
	os.system(command)
	wait(GlobalDelay.get() * 10)
	the_app.focus()
	if not the_app.isRunning():
		the_app.open()
		wait(GlobalDelay.get() * 15)
		the_app.focus()
		if not the_app.isRunning():
			print "Cannot open the app."
			raise SystemExit(1)
# end def open_the_app


def main():
	if len(sys.argv) < 2:  # Check number of command line arguments
		sys.stderr.write(
			"Please supply the path to a test document folder" + "\n" +
			"Usage : python %s [Sikuli arguments] -p /path/documents/" %
			sys.argv[0])
		raise SystemExit(1)

	try:
		options, arguments = getopt.getopt(sys.argv[1:], "p:u", ["test_folder_path=", "update"])
	except getopt.GetoptError as err:
		# print help information and exit:
		print str(err)  # will print something like "option -a not recognized"
		sys.exit(2)

	test_folder = ""
	update_screenshots_mode = False  # False - run test, True - update screenshots

	for (opt, arg) in options:
		if opt in ("-p", "--test_folder_path"):
			# path to a folder with documents and settings
			test_folder = arg
		elif opt in ("-u", "--update"):
			# update standard screenshots instead of running the test
			update_screenshots_mode = True
		else:
			pass

	if not os.path.exists(test_folder):
		print "Invalid input path to the test folder or the -p key is missing."
		raise SystemExit(1)

	set = Settings(test_folder)
	set.read_settings()
	document_file_extension = set.get_parameter("doc_ext")
	Screenshot.set_extension(set.get_parameter("screenshot_ext"))
	GlobalDelay.set(set.get_float_parameter("delay"))
	app_path = set.get_parameter("app_path_to_test")
	app_path_standard = set.get_parameter("app_path_standard")  # to create standard screenshots

	test_doc_folder = test_folder + "documents"
	if not os.path.exists(test_doc_folder):
		print "Invalid path to test documents."
		raise SystemExit(1)

	if not os.path.exists(app_path):
		print "Invalid or missing path to the application under test."
		raise SystemExit(1)

	if not os.path.exists(app_path_standard):
		print "Invalid or missing path to the application for screenshots."
		raise SystemExit(1)

	document_list = []
	for file in os.listdir(test_doc_folder):
		if file.endswith(document_file_extension):
			document_list.append(test_doc_folder + os.sep + file)

	number_of_docs = len(document_list)

	if update_screenshots_mode == True:
		app_path = app_path_standard  # take screenshots of the standard application

	the_app = App(app_path)
	open_the_app(app_path, the_app)

	test = 0
	failed = 0
	while (test < number_of_docs):
		try:
			doc = Document(document_list[test], app_path, update_screenshots_mode)
		except OSError as msg:
			print msg
			test += 1
			continue
		doc.open()

		if update_screenshots_mode == False:
			# testing
			if not doc.check():
				print "Failed", doc.get_document_name()
				failed += 1
		else:
			# updating screenshots mode
			doc.update_standard_screenshot()

		doc.close()
		test += 1

	if update_screenshots_mode == False:
		print("Tests total: {0}  Failed: {1}".format(number_of_docs, failed))
	else:
		# updating screenshots mode
		print("\nScreenshots total: {0}".format(number_of_docs))

	the_app.close()

# end def main

# ========================================================================================
# __main__
# ========================================================================================

if __name__ == '__main__':
	main()

