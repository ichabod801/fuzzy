3.0 is an esoteric programming language, and fuzzy.py is an implementation of that language in Python.

## fuzzy.py

To run a 3.0 program with fuzzy.py, use -f or --file:

    python fuzzy.py -f tests/fib.txt

The main object of interest created by fuzzy.py is the Intepreter, which has a parse method for converting text to code, and an execute method for running parsed code:

    inter = fuzzy.Interpreter()
    name = inter.parse('tests/fib.txt')
    inter.execute(name)

The Interpreter object stores parsed code in the programs attribute. The return value of the parse method is the key to the programs attribute for the parsed program, which you then pass to execute.

## The 3.0 Language

3.0 is a simple procedural language using Polish notation and fuzzy matching. This allows for a high degree of customization in how the program is written. It also allows for any English text (and more) to be interpretted and run as a computer program. Note that for a randomly selected piece of English text, the resulting computer program will probably have nothing to do with the meaning of the English text.

### Basic Syntax

The basic format of a line of 3.0 code is:

    statement [expression [expression]]

That is, a statement followed by zero, one, or two expressions. The number of expressions is determined by the statement, and there are no optional expressions. So what is a line of 3.0 code is determined by the words themselves, not by line feeds or semi-colons.

The format of an expression is one of:

    function [expression [expression]]
    token

As with statements, the number of expressions is determined by the function being used. Tokens are sequences of non-whitespace characters. Tokens are interpretted as variables if they fuzzy match a variable name, otherwise they may be intepretted as strings or numbers, depending on the context.

For more detailed documentation, see DOCUMENTATION.md (in progress).

#### Statements

The following statements are available in 3.0:

* assign: Assign a value to a variable. 
* calculate: Display a token as a number.
* exit: End the program.
* go: Move to a different line in the program.
* if: Conditional branching (do if true).
* print: Display a token as a string
* return: Move to just after the last go statement.

#### Functions

The following functions are available in 3.0:

* add (+)
* and (logical)
* concatenate (combine as strings)
* divide (/)
* equal (= comparison)
* greater (> comparison)
* input (from the user)
* left (n characters at the start of a string)
* less (< comparison)
* modulus (%)
* multiply (*)
* not (logical)
* or (logical)
* power (x ** y)
* right (n characters at the end of a string)
* subtract (-)

Tokens are considered to be true if their numeric representation is not 0, and false if it is 0. The numeric representation of a token is based on the lexicon (see below). For standard 3.0, it is base 18 using the consonants from b to w, with y and z counting as decimal points and x counting as a negation. So bozo = 0.0, and ace = 1 (bozo and ace are used for false and true internally). Additionally, Craig = 562 (1 * 18 ** 2 + 13 * 18 + 4) and hypoxia = -5.61111... ((5 + 11/18) * -1).

#### Constants

There are four constants in 3.0:

* false = 'bozo'
* period = '.'
* space = ' '
* true = 'ace'

These are implemented as functions with no arguments.

### Lexicon

3.0 requires a lexicon file to operate. This defines the characters for fuzzy matching and numeric representations, and the aliases used to fuzzy match statements and functions. The current lexicon file is designed to work on English text, and to assign an equal number of words to each of the possible statements (although more to exit than to go, to help limit infinite loops)

You could use a different lexicon file to run 3.0 programs, but they may not work the same. You could have a Spanish lexicon file, and run it on programs written in Spanish. You could write a Klingon lexicon file. You could write a Klingon lexicon file and run it on a program written in German (assuming you are using Romanized Klingon). If not endless, the possibilities are exceedingly large.

#### Characters

There are three sets of characters the lexicon must define:

* digits: The characters to use as digits in numbers.
* decimals: The characters to use as decimals in numbers.
* signs: The characters that change the sign of the number.

In the standard lexicon file, these are defined as:

    digits: bcdfghjklmnpqrstvw
    decimals: yz
    signs: x

All other characters are ignored for both numeric representations and fuzzy matching. Decimal points after the first are ignored. All sign characters are applied, however, so xerox = 13.

#### Aliases

Each function or statement is listed with several possible aliases. Fuzzy matches to any one of the aliases count as a match to that statement. Note that fuzzy matches to a statement do not count unless that statement is listed as an alias for itself. This allows non-English lexicons to ignore the English versions of the base statements.

Also note that if a lexicon does not list any aliases for a given statement or function, that statement or function will never be recognized in any code. This could be used to produce versions of 3.0 with limited instruction sets, but caution is advised.

Here's an example alias listing from the base lexicon file:

    print: print, say, talk, write, dump, pronounce, pointificate

### Fuzzy Matching

When the parser needs a statement, it looks at the numeric value of the next word to parse. It then finds the statement alias that is numerically closest to that word, and uses the statement for that alias.

When the parser looks at an expression, it looks at the relevant characters of the next word (digits, decimals, and signs). If that matches a function alias (allowing for one character to be changed), that function is used. Otherwise, if that matches an assigned variable name (again allowing for one character to be changed), the value of that variable is used. Otherwise the word itself is used. Ambiguous fuzzy matches do not match. 

For example, 'deviate' will be reduced to 'dvt'. This is one character off from 'dvd', the reduction of 'divide', and will match 'divide'. On the other hand, 'decade' (or 'dcd') will not match 'divide', even though it's also one character off of 'dvd'. This is because 'dcd' is also one character off from 'dck', or 'dock', an alias of subtract. Since it is ambiguous as to what it matches, it matches neither one.

### Sample Code

Here is a basic hello world program:

    assign text concatenate hello space
    assign text concatenate text world
    print text

The first line assigns the concatenation of 'hello' and ' ' to the variable text. The second line does the same thing to add 'world' onto the end. The third line prints the value of text ('hello world'). This can all of course be done on one line:

    say fuse hello fuse gap world

The above line uses aliases of the statements and functions. You can go beyond that and use fuzzy matching to obfuscate the code:

    soot avian papanood hello goop ssgn oven mirage venue world toe even

Some of the above words aren't even English, but it prints 'hello world' just the same. Note how 'avian', 'oven', 'venue', and 'even' all refer to the same variable name. Since only the consonants are used, they are all equivalent to 'vn'. Also, while this is three lines of code, you can put it all on one line and 3.0 doesn't notice.

You can also obfuscate in a way that puts patterns or even perhaps beauty into your code:

    video voodoo virago hello gogo
    bombard void depend avid world
    evader evade

Well, some patterns at least, and still 'hello world'. Here is a bit of code to calculate the first few Fibonacci numbers:

    set first ciao
    set second ciao
    set looper coda
    figure first
    figure second
    set hold second
    set second plus first second
    set first hold
    set looper subtract looper ciao
    if looper
    go hoe
    exit

This illustrates one of the tricks in programming in 3.0. The first time I wrote this, the looping variable was named 'loop', not 'looper'. Without vowels, 'loop' is 'lp', but that's one character different than 'gp', so it was matching 'gap', one of the aliases for the space constant.

Beyond various obfuscations, you can also do found code, where you try to find standard English text that produces interesting results. This quote:

    The most difficult thing is the decision to act, the rest is merely tenacity. The fears are paper tigers. You can do anything you decide to do. You can act to change and control your life; and the procedure, the process is its own reward. -Amelia Earhart

produces this output when run as a 3.0 program:

    0
    act,
    do.
    change

'Act, do, change' seems appropriate to the quote. I expect there's better out there, but I haven't found it yet. Hamlet's soliloquy, on the other hand, prints some garbage and asks you 'whether?'.