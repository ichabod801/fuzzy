"""
fuzzy.py

An implementation of the 3.0 programming language.

Constants:
PARSER: A command line argument parser. (argparse.ArgumentParser)

Classes:
FuzzyDict: A dictionary that uses fuzzy matching. (collections.UserDict)
Interpreter: Intepreter for 3.0 programs. (object)
Lexicon: A natural language mapping for the 3.0 programming language. (object)

Functions:
run_file: Run a single program. (None)
tests: Run the test cases. (None)
"""

import argparse
import bisect
import collections
import os.path

__author__ = """Craig "Ichabod" O'Brien"""
__copyright__ = "Copyright 2020, Craig O'Brien"

__license__ = "GPL v3.0+"
__version__ = "Ace Ice"

PARSER = argparse.ArgumentParser()
PARSER.add_argument('-t', '--test', help = 'run the test scripts.', action = 'store_true')
PARSER.add_argument('-f', '--file', help = 'the path to the file to run.')

class FuzzyDict(collections.UserDict):
	"""
	A dictionary that uses fuzzy matching. (collections.UserDict)

	A FuzzyDict has a set of characters (the chars attribute), which are the only
	characters used for matching keys. So if the chars are just ascii consonants,
	then dude and deed are treated as the same key. Furthermore, keys are 
	considered to match if they match except one character is different. So dude
	and dog are treated as the same key. However, the one character off match only
	works if it is not ambiguous. Obviously, keys for FuzzyDicts should be strings.

	The above is true for using keys to retrieve values. When you assign to a key,
	it assumed to be a new, distinct key. If the strict attribute is set to True,
	trying to assign a key that is a match to a previous key will raise a KeyError.
	If strict is False, the new key will be added as a base key. Any time a key is
	added, any ambiguous fuzzy key will be given the value None. For example, if
	you have the key dog and you add the key box, bg and dx are fuzzy matches for
	both keys, and will both be set to None. Note that a FuzzyDict returns None
	for a key not in the dict, to give a common interface for detecting ambiguous
	or non-existent keys (!! this needs to be changed in the future, so they are
	deleted but remembered, allowing contains to work correctly).

	Attributes:
	base: The base keys (those assinged externally). (set of str)
	chars: The chars relevant to matching keys. (str)
	strict: A flag for strict handling of ambiguous keys. (bool)

	Methods:
	_fuzzies: Returns a generator fo fuzzy matches for a word. (generator)
	_trim: Trims the non-char characters from a string. (str)

	Overridden Methods:
	__init__
	__getitem__
	__setitem__
	"""

	def __init__(self, chars, initial_data = {}, strict = True):
		"""
		Set up the FuzzyDict. (None)

		Parameters
		chars: The chars relevant to matching keys. (str)
		initial_data: The initial data for the dictionary. (dict or list of tuple)
		strict: A flag for strict handling of ambiguous keys. (bool)
		"""
		# Set up fuzzy matching.
		self.chars = chars
		self.strict = strict
		self.base = set()
		# Initialize the base dictionary.
		super(FuzzyDict, self).__init__(initial_data)

	def __getitem__(self, key):
		"""
		Get a value for a given key. (object)

		If the key is not in the FuzzyDict, None is returned.

		Parameters:
		key: The key to get a value for. (str)
		"""
		try:
			return self.data[self._trim(key)]
		except KeyError:
			return None

	def __setitem__(self, key, value):
		"""
		Set a value for a key, and all it's fuzzy matches. (None)

		Parameters:
		key: The key to set a value for. (str)
		value: The value to set the key to. (object)
		"""
		# Get the key.
		key = self._trim(key)
		# Check for a distinct key.
		if key in self.base and self.strict:
			raise KeyError(f'Key conflict in FuzzyDict: {key!r}.')
		# Add the key.
		self.base.add(key)
		self.data[key] = value
		# Add any fuzzy match keys.
		for fuzzed in self._fuzzies(key):
			# Nerf any ambiguous fuzzy match keys.
			if fuzzed in self.data and fuzzed not in self.base:
				self.data[fuzzed] = None
			elif fuzzed not in self.base:
				self.data[fuzzed] = value

	def _fuzzies(self, word):
		"""
		Create a generator of fuzzy matches for a string. (generator)

		Parameters:
		word: The string to generate fuzzy matches for. (str)
		"""
		# Loop through the relevant characters.
		word = self._trim(word)
		for index, old in enumerate(word):
			# Loop through the valid replacement characters.
			for new in self.chars:
				if old != new:
					yield word[:index] + new + word[index + 1:]

	def _trim(self, word):
		"""
		Remove irrelevant characters from a string. (str)

		Parameters:
		word: The string to remove characters from. (str)
		"""
		return ''.join(filter(lambda char: char in self.chars, word))

class Interpreter(object):
	"""
	Intepreter for 3.0 programs. (object)

	The parse method converts the raw code to a tree structure of statements,
	functions, and values in polish notation. The execute method (using the various
	exec_foo and func_foo methods) executes the parsed code.

	Attributes:
	current_program: The program currently being executed. (list)
	lexicon: The current map of statements & functions being used. (Lexicon)
	pointer: The index of the line currently being executed. (int)
	programs: The parsed code for each program. (dict of str: list)
	returns: The stack of locations for executed go statements (list of int)
	variables: The values of variables in the current execution (dict of str: str)

	Class Attributes:
	args: The number of args for each function. (dict of str: int)

	Methods:
	evaluate: Determine the value of an expression. (str)
	exec_assign: Assign a value to a variable. (None)
	exec_calculate: Print a number. (None)
	exec_exit: End the program. (None)
	exec_go: Go to the specified line of the program. (None)
	exec_if: Handle conditional execution. (None)
	exec_print: Print a word. (None)
	exec_return: Return to just after the last go. (None)
	execute: Execute the parsed program. (None)
	func_add: Add two expressions. (str)
	func_and: Get the logical and of two expressions. (str)
	func_concatenate: Combine two expressions sequentially. (str)
	func_divide: Divide two expressions. (str)
	func_equal: Test if two expressions are equal numerically. (str)
	func_false: False constant. (str)
	func_greater: Test if one expression is greater than another. (str)
	func_left: Return length characters from the left of text. (str)
	func_less: Test if one expression is less than another. (str)
	func_modulus: Get the remainder of one expression divided by another. (str)
	func_multiply: Get the product of two expressions. (str)
	func_not: Logically negate an expression. (str)
	func_or: Get the logical or of two expressions. (str)
	func_period: Period constant. (str)
	func_power: Calculate one expression raised to another. (str)
	func_right: Return length characters from the right of text. (str)
	func_space: Space constant. (str)
	func_subtract: Get the difference of two expressions. (str)
	func_true: True constant. (str)
	handle_function: Use the correct method to execute the given function. (str)
	parse: Parse the raw code into statement calls and expression trees. (None)
	parse_args: Parse the arguments for a statement or function. (None)

	Overridden Methods:
	__init__
	"""

	args = {'add': 2, 'and': 2, 'assign': 2, 'calculate': 1, 'concatenate': 2, 'divide': 2, 'equal': 2,
		'exit': 0, 'false': 0, 'go': 1, 'greater': 2, 'if': 1, 'input': 1, 'left': 2, 'less': 2, 
		'modulus': 2, 'more': 2, 'multiply': 2, 'not': 1, 'or': 2, 'period': 0, 'power': 2, 'print': 1, 
		'return': 0, 'right': 2, 'space': 0, 'subtract': 2, 'true': 0}

	def __init__(self, language = 'english'):
		"""
		Set up the interpreter. (None)

		Parameters:
		language: The language to use for the lexicon. (str)
		"""
		# Set the provided attributes.
		self.lexicon = Lexicon(language)
		# Set the default attributes.
		self.programs = {}

	def evaluate(self, expression):
		"""
		Determine the value of an expression. (str)

		Parameters:
		expression: An expression to evaluate. (list or str)
		"""
		# Lists are calls to other functions.
		if isinstance(expression, list):
			value = self.handle_function(expression)
		# Otherwise check for a variable reference.
		elif self.variables[expression] is not None:
			value = self.variables[expression]
		# Otherwise just return the string.
		else:
			value = expression
		return value

	def exec_assign(self, target, value):
		"""
		Assign a value to a variable. (None)

		Parameters:
		target: The variable name. (str)
		value: The value to assign. (str)
		"""
		value = self.evaluate(value)
		self.variables[target] = value

	def exec_calculate(self, value):
		"""
		Print a number. (None)

		Parameters:
		value: The word to print as a number. (str)
		"""
		value = self.evaluate(value)
		print(self.lexicon.num(value))

	def exec_exit(self):
		"""
		End the program. (None)
		"""
		# Move the pointer past the end of the program.
		self.pointer = len(self.current_program)

	def exec_go(self, target):
		"""
		Go to the specified line of the program. (None)

		Note that the target line is mod the length of the program.

		Paramters:
		target: The line to go to as a word. (str)
		"""
		#print('go', target, end = ' ')
		# Get the target and force it within the program.
		target = self.evaluate(target)
		target = int(self.lexicon.num(target) - 1) % len(self.current_program)
		# Store and make the jump.
		self.returns.append(self.pointer)
		self.pointer = target

	def exec_if(self, value):
		"""
		Handle conditional execution. (None)

		3.0 use do-if-true for conditionals.

		Parameters:
		value: The value checked for truth. (str)
		"""
		value = self.evaluate(value)
		if not self.lexicon.num(value):
			self.pointer += 1

	def exec_print(self, value):
		"""
		Print a word. (None)

		Parameters:
		value: The word to print. (str)
		"""
		value = self.evaluate(value)
		print(value)

	def exec_return(self):
		"""
		Return to just after the last go. (None)
		"""
		if self.returns:
			self.pointer = self.returns.pop()

	def execute(self, name):
		"""
		Execute the parsed program. (None)

		If the program hasn't been parsed, nothing happens.
		"""
		# Set the intial program state.
		self.pointer = 0
		self.returns = []
		self.variables = self.lexicon.variables.copy()
		self.current_program = self.programs[name]
		# Loop through the program lines.
		while True:
			# Get the current line and advance the pointer.
			line = self.current_program[self.pointer]
			#print(self.pointer, line)
			self.pointer += 1
			# Execute the current line.
			execer = getattr(self, f'exec_{line[0]}')
			execer(*line[1:])
			# Check for exiting the program.
			if self.pointer >= len(self.current_program):
				break

	def func_add(self, x, y):
		"""
		Add two expressions. (str)

		Parameters:
		x: The first expression to add. (str or list)
		y: The second expression to add. (str or list)
		"""
		# Evaluate the expressions.
		x = self.evaluate(x)
		y = self.evaluate(y)
		# Add the results.
		return self.lexicon.word(self.lexicon.num(x) + self.lexicon.num(y))

	def func_and(self, left, right):
		"""
		Get the logical and of two expressions. (str)

		Evaluates the two expressions and returns the left word, or the right word
		if it is the only one that is false. A word is true if it's number is non-zero.

		Parameters:
		left: The first expression to and. (str or list)
		right: the second expression to and. (str or list)
		"""
		# Evaluate the expressions as numbers.
		left = self.evaluate(left)
		right = self.evaluate(right)
		x, y = self.lexicon.num(left), self.lexicon.num(right)
		# Return the leftmost false value, or the leftmost value.
		if x and y:
			return left
		elif x:
			return right
		else:
			return left

	def func_concatenate(self, left, right):
		"""
		Combine two expressions sequentially. (str)

		For example, 'concatenate foo bar' resolves to 'foobar'.

		Parameters:
		left: The first expression to combine. (str or list)
		right: the second expression to combine. (str or list)
		"""
		# Evaluate the expressions.
		left = self.evaluate(left)
		right = self.evaluate(right)
		# Combine them as strings.
		return left + right

	def func_divide(self, left, right):
		"""
		Divide two expressions. (str)

		Paramters:
		left: The dividend. (str or list)
		right: The divisor. (str or list)
		"""
		# Evaluate the expressions.
		left = self.evaluate(left)
		right = self.evaluate(right)
		# Return the quotient.
		return self.lexicon.word(self.lexicon.num(x) / self.lexicon.num(y))

	def func_equal(self, left, right):
		"""
		Test if two expressions are equal numerically. (str)

		Parameters:
		left: The first expression to check. (str or list)
		right: the second expression to check. (str or list)
		"""
		# Evaluate the expressions numerically.
		left = self.evaluate(left)
		right = self.evaluate(right)
		x, y = self.lexicon.num(left), self.lexicon.num(right)
		# Return 1 or 0 depending on their equality.
		if x == y:
			return 'ace'
		else:
			return 'bozo'

	def func_false(self):
		"""
		False constant. (str)
		"""
		return 'bozo'

	def func_greater(self, left, right):
		"""
		Test if one expression is greater than another. (str)

		Parameters:
		left: The first expression to check. (str or list)
		right: the second expression to check. (str or list)
		"""
		# Evaluate the expressions numerically.
		left = self.evaluate(left)
		right = self.evaluate(right)
		x, y = self.lexicon.num(left), self.lexicon.num(right)
		# Return 1 or 0 depending on their relative size.
		if x > y:
			return 'ace'
		else:
			return 'bozo'

	def func_input(self, prompt):
		"""
		Get input from the user. (str)

		Parameters:
		prompt: Text to prompt the user with. (str)
		"""
		return input(f'{prompt}? ')

	def func_left(self, text, length):
		"""
		Return length characters from the left of text. (str)

		Parameters:
		text: The expression creating the text. (str or list)
		length: The expression determining how many characters to take. (str or list)
		"""
		# Evaluate the expressions.
		text = self.evaluate(text)
		length = self.evaluate(length)
		# Modulus the number of characters to take.
		length = self.lexicon.int(length) % (len(text) + 1)
		return text[:length]

	def func_less(self, left, right):
		"""
		Test if one expression is less than another. (str)

		Parameters:
		left: The first expression to check. (str or list)
		right: the second expression to check. (str or list)
		"""
		# Evaluate the expressions as numbers.
		left = self.evaluate(left)
		right = self.evaluate(right)
		x, y = self.lexicon.num(left), self.lexicon.num(right)
		# Return 1 or 0 depending on their relative size.
		if x < y:
			return 'ace'
		else:
			return 'bozo'

	def func_modulus(self, x, y):
		"""
		Get the remainder of one expression divided by another. (str)

		Paramters:
		x: The dividend. (str or list)
		y: The divisor. (str or list)
		"""
		# Evaluate the expressions. 
		x = self.evaluate(x)
		y = self.evaluate(y)
		# Get the modulus of the results.
		return self.lexicon.word(self.lexicon.num(x) % self.lexicon.num(y))

	def func_multiply(self, x, y):
		"""
		Get the product of two expressions. (str)

		Parameters:
		x: The first expression to multiply. (str or list)
		y: The second expression to multiply. (str or list)
		"""
		# Evaluate the expressions.
		x = self.evaluate(x)
		y = self.evaluate(y)
		# Multiply the results.
		return self.lexicon.word(self.lexicon.num(x) * self.lexicon.num(y))

	def func_not(self, value):
		"""
		Logically negate an expression. (str)

		Parameters:
		value: The expression to negate. (str or list)
		"""
		# Evaluate the expression.
		value = self.evaluate(value)
		# Reduce it's truth value to 1 or 0.
		if value:
			return 'ace'
		else:
			return 'bozo'

	def func_or(self, left, right):
		"""
		Get the logical or of two expressions. (str)

		Evaluates the two expressions and returns the left word, or the right word
		if it is the only one that is true. A word is true if it's number is non-zero.

		Parameters:
		left: The first expression to or. (str or list)
		right: The second expression to or. (str or list)
		"""
		# Evaluate the expressions as numbers.
		left = self.evaluate(left)
		right = self.evaluate(right)
		x, y = self.lexicon.num(left), self.lexicon.num(right)
		# Return the left most true, or the left most.
		if x:
			return left
		elif y:
			return right
		else:
			return left

	def func_period(self):
		"""
		Period constant. (str)
		"""
		return '.'

	def func_power(self, x, y):
		"""
		Calculate one expression raised to another. (str)

		Parameters:
		x: The expression to raise to a power. (str or list)
		y: The expression of the power to raise to. (str or list)
		"""
		# Evaluate the expressions.
		x = self.evaluate(x)
		y = self.evaluate(y)
		# Get the difference.
		return self.lexicon.word(self.lexicon.num(x) ** self.lexicon.num(y))

	def func_right(self, text, length):
		"""
		Return length characters from the right of text. (str)

		Parameters:
		text: The expression creating the text. (str or list)
		length: The expression determining how many characters to take. (str or list)
		"""
		# Evaluate the expressions.
		text = self.evaluate(text)
		length = self.evaluate(length)
		# Modulus the number of characters to take.
		length = self.lexicon.int(length) % (len(text) + 1)
		return text[length:]

	def func_space(self):
		"""
		Space constant (str)
		"""
		return ' '

	def func_subtract(self, x, y):
		"""
		Get the difference of two expressions. (str)

		Parameters:
		x: The expression to subtract from. (str or list)
		y: The expression to subtract. (str or list)
		"""
		# Evaluate the expressions.
		x = self.evaluate(x)
		y = self.evaluate(y)
		# Get the difference.
		return self.lexicon.word(self.lexicon.num(x) - self.lexicon.num(y))

	def func_true(self):
		"""
		True constant. (str)
		"""
		return 'ace'

	def handle_function(self, call):
		"""
		Use the correct method to execute the given function. (str)

		Paramters:
		call: A function and it's argument(s). (list of str)
		"""
		function, *args = call
		funcer = getattr(self, f'func_{function}')
		return funcer(*args)

	def parse(self, path):
		"""
		Parse the raw code into statement calls and expression trees. (str)

		The return value is the name the parsed program was stored under.

		Parameters:
		path: The system path to the 3.0 code file. (str)
		"""
		# Read the code into a stack.
		with open(path) as code_file:
			raw_code = code_file.read().lower().split()
		raw_code.reverse()
		# Loop through the words in the stack.
		name = os.path.basename(path)
		self.programs[name] = []
		while raw_code:
			word = raw_code.pop()
			# Force the first word into a statement.
			statement = self.lexicon.tight(word)
			line = [statement]
			try:
				# Get the correct number of arguments.
				self.parse_args(line, raw_code)
			except IndexError:
				# End the program if there are not enough arguments.
				line = ['exit']
			# Store the full line.
			self.programs[name].append(line)
		return name

	def parse_args(self, line, raw_code):
		"""
		Parse the arguments for a statement or function. (None)

		Modifies the line parameter in place.

		Paramters:
		line: The current line of the program. (list of str)
		raw_code: The words of the raw code as a stack. (list of str)
		"""
		# For each argument required by the statement.
		for arg_count in range(self.args[line[0]]):
			# Grab the argument.
			arg = raw_code.pop()
			# Parse it further if it is a function.
			function = self.lexicon.functions[arg]
			if function is not None:
				line.append([function])
				self.parse_args(line[-1], raw_code)
			else:
				line.append(arg)

class Lexicon(object):
	"""
	A natural language mapping for the 3.0 programming language. (object)

	The chars attribute is equal to decimals + digits + signs. The base attributes
	is equal to len(digits).

	Attributes:
	base: The numeric base for number conversions. (int)
	breaks: The breakpoints for bisecting the statements attribute. (list of float)
	chars: The characters relevant to fuzzy matching. (str)
	statements: The command list for the fuzzy matching of statements. (list of str)
	decimals: The characters indicating a fractional part. (str)
	digits: The characters counting as digits for number conversions. (str)
	functions: The fuzzy matching for functions. (FuzzyDict)
	signs: The characters indicating a change in sign of a number. (str)
	variables: The fuzzy matching for constants. (FuzzyDict)
	tight: Distance based fuzzy matching for statements. (str)

	Class Attributes:
	base_statements: The statements in the parsed language. (set of str)

	Methods:
	add: Add two words. (str)
	conform: Make sure two fractions have the same denominator. (tuple)
	divide: Divide one word by another. (str)
	float: Return a float point version of a word. (float)
	fraction: Return a fraction version of a word. (tuple of int)
	int: Return an integer version of a word. (int)
	num: Return an integer or float version of a word as appropriate. (number)
	mod: Get the remainder of one word divided by another. (str)
	multiply: Get the product of two words. (str)
	subtract: Get the difference of two words. (str)
	word: Convert a fraction into a word. (str)

	Overridden Methods:
	__init__
	"""

	base_statements = set(('assign', 'calculate', 'exit', 'go', 'if', 'print', 'return'))

	def __init__(self, language = 'english'):
		"""
		Read in the lexicon. (None)

		For language, just give the name of the language, not the full file name.
		So, 'english' instead of 'english_lex.txt'.

		Parameters:
		language: The language file to use. (str)
		"""
		# Set updummy values for the attributes.
		self.digits = ''
		self.decimals = ''
		self.signs = ''
		self.chars = ''
		self.base = 0
		commands = []
		# Read through the lexicon file.
		with open(f'{language}_lex.txt') as lex_file:
			for line in lex_file:
				# Ignore blank lines and comments.
				if not line.strip() or line[0] == '(':
					continue
				# Read the information provided.
				key, value = line.strip().lower().split(':')
				key = key.strip()
				# Check for character specifications.
				if key == 'digits':
					self.digits = value.strip()
					self.base = len(self.digits)
				elif key == 'decimals':
					self.decimals = value.strip()
				elif key == 'signs':
					self.signs = value.strip()
				else:
					# Otherwise treat value as aliases for a command.
					for alias in value.split(','):
						# Track by the type of command.
						if key in self.base_statements:
							commands.append((self.num(alias), key))
						else:
							self.functions[alias.strip()] = key
				# Set up derived attributes as soon as possible.
				if not self.chars and self.digits and self.decimals and self.signs:
					self.chars = self.digits + self.decimals + self.signs
					self.functions = FuzzyDict(self.chars)
					self.variables = FuzzyDict(self.chars, strict = False)
		# Set up the bisection for tight matching.
		commands.sort()
		self.statements = []
		self.breaks = []
		for first, second in zip(commands, commands[1:]):
			self.statements.append(first[1])
			self.breaks.append(first[0] + (second[0] - first[0]) / 2)
		self.statements.append(second[1])

	def num(self, word):
		"""
		Return a numeric version of a word. (int or float)

		Parameters:
		word: The word to convert to a fraction. (str)
		"""
		whole = 0
		numerator = 0
		denominator = 1
		sign = 1
		whole_mode = True
		for char in word.lower():
			try:
				if whole_mode:
					whole = whole * self.base + self.digits.index(char)
				else:
					numerator = numerator * self.base + self.digits.index(char)
					denominator *= self.base
			except ValueError:
				if char in self.decimals:
					whole_mode = False
		sign_count = 0
		for char in self.signs:
			sign_count += word.count(char)
		if sign_count % 2:
			sign = -1
		if numerator:
			return (whole + numerator / denominator) * sign
		else:
			return whole * sign

	def tight(self, word):
		"""
		Distance based fuzzy matching for statements. (str)

		Parameters:
		word: The word to convert to a statement. (str)
		"""
		return self.statements[bisect.bisect(self.breaks, self.num(word))]

	def word(self, num):
		whole_part = abs(int(num))
		chars = ''
		while whole_part:
			whole_part, index = divmod(whole_part, self.base)
			chars = self.digits[index] + chars
		if isinstance(num, float):
			frac_part = abs(num - int(num))
			frac_chars = ''
			while frac_part > 1 / self.base ** 5 and len(frac_chars) < 10:
				product = frac_part * 18
				frac_chars += self.digits[int(product)]
				frac_part = product - int(product)
			if frac_chars:
				chars = chars + self.decimals[0] + frac_chars
		if num < 0:
			return chars + self.signs[0]
		else:
			return chars
		

def run_file(path):
	"""
	Run a single program. (None)

	Paramters:
	path: The system path to the file to run. (str)
	"""
	inter = Interpreter()
	name = inter.parse(path)
	try:
		inter.execute(name)
	except KeyboardInterrupt:
		pass

def tests():
	"""
	Run the test cases. (None)
	"""
	# Define the test cases.
	cases = [('hello_plain', 'Hello World'), ('hello_one', 'Hello World on one line'),
		('hello_obfus', 'Hello World obfuscated'), ('hello_pattern', 'Hello beautified'), 
		('fib', 'Fibonacci numbers'), ('earhart', 'Emilia Earhart quote'), ('hamlet', 'Hamlet soliloquy')]
	# For each test case.
	for name, title in cases:
		# Print a title.
		print(f'\n-------------------\n\n{title}')
		# Print the program.
		inter = Interpreter()
		name = inter.parse(f'tests/{name}.txt')
		print()
		print(inter.programs[name])
		print()
		# Run the program.
		try:
			inter.execute(name)
		except KeyboardInterrupt:
			pass
		print()

if __name__ == '__main__':
	args = PARSER.parse_args()
	if args.test:
		tests()
	elif args.file:
		run_file(args.file)