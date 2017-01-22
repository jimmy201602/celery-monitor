#
# recompile.py
# "safely recompile an untrusted python module.  heh."
# Eli Fulkerson
#
# This script lives at www.elifulkerson.com
#

import sys
import string
from traceback import print_exc, format_exception

class Error:
	"""
	An Error is a string message with a fail/succeed boolean value 
	It can be returned out of a function for display elsewhere and retain
	use for if checks.
	"""

	def __init__(self,message,success=False):
		self.message = message
		self.success = success

	def __call__(self):
		return self.success

	def __str__(self):
		return self.message

def listf(data):
	buffer = ""
	for line in data:
		buffer = buffer + line + "\n"
	return buffer

def recompile( modulename ):
	"""
	first, see if the module can be imported at all...
	"""
	try:
		tmp = __import__(modulename)
	except:
		return Error("Couldn't import module " + modulename)

	"""
    Use the imported module to determine its actual path
    """
	pycfile = tmp.__file__
	modulepath = string.replace(pycfile, ".pyc", ".py")

	"""
    Try to open the specified module as a file
    """
	try:
		code=open(modulepath, 'rU').read()
	except:
		return Error("Error opening file: " + modulepath + ".  Does it exist?")

	"""
    see if the file we opened can compile.  If not, return the error that it gives.
    if compile() fails, the module will not be replaced.
    """
	try:
		compile(code, modulename, "exec")
	except:
		return Error("Error in compilation: " + str(sys.exc_info()[0]) +"\r\n" + listf(format_exception(sys.exc_type, sys.exc_value, sys.exc_traceback)) )
	else:
		"""
        Ok, it compiled.  But will it execute without error?
        """
		try:
			execfile(modulepath)
		except:
			return Error("Error in execution: " + str(sys.exc_info()[0]) +"\r\n" + listf(format_exception(sys.exc_type, sys.exc_value, sys.exc_traceback)) )
		else:
			"""
            at this point, the code both compiled and ran without error.  Load it up
            replacing the original code.
            """

			reload( sys.modules[modulename] )

	return Error("Module successfully recompiled", True)