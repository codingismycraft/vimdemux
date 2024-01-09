"""Exposes the functions to run and debug python code in tmux."""

import ast
import enum
import os


def run(fullpath, linenum):
    """Execute the specified file, identified by its full path.

    Parameters
    ----------
    fullpath : str
        The path to the file that needs to be executed. 

    linenum : int
        The line number within the file. 

    Depending on file type and line number specified, execution differs:

    1. If file is a Python script, it's run as is.  

    2. If file is a Python test script, execution depends on the line number:
        
    - If line number corresponds to a test function or method, only that
      specific unit test is run (via pytest).
    - If line number does not correspond to a test function or method, the
      entire suite of tests within the script is run (via pytest).
    """
    filetype = _get_file_type(fullpath) 
    if filetype == _FileType.PYTHON_SCRIPT:
        _run_script(fullpath)
    elif filetype == _FileType.PYTHON_TEST:
        _run_test(fullpath, linenum)
    else:
        print(f"Dont now how to run {fullpath}")


def debug(fullpath, linenum):
    """Initiates a debugging session for the specified Python file.

    Parameters
    ----------
    fullpath : str
        The file path of the Python file (script or test) that should be
        debugged.

    linenum : int
        The line number to start debugging session from.

    Note:
    ----
    The behavior of the debugging session changes based on the type of file and
    the specified line number.

    1. If the file is a Python script, it is debugged taking the line number
    into account.

    2. If the file is a Python unittest:

    - If the line number corresponds to a specific test function or method,
      only that function/method is debugged.

    - If the line number does not correspond to a specific test function or
      method, the entire test suite present in the file is debugged.
        
    A helper function "_get_file_type" is used to determine the type of Python
    file, and based on its return value, either "_debug_script" or
    "_debug_test" is called to start the debugging session.
    """
    filetype = _get_file_type(fullpath) 
    if filetype == _FileType.PYTHON_SCRIPT:
        _debug_script(fullpath)
    elif filetype == _FileType.PYTHON_TEST:
        _debug_test(fullpath, linenum)
    else:
        print(f"Dont now how to debug {fullpath}")

# Private stuff goes after this line.

def _run_script(fullpath):
    """Runs the passed in script as a python program.

    Parameters
    ----------
    fullpath : str
        The path to the file that needs to be executed. 
    """
    dirname = os.path.dirname(fullpath)
    basename = os.path.basename(fullpath)
    cmds = [
        f"cd {dirname}",
        "unset PYTHONBREAKPOINT",
        "clear",
        f"python3.10 {basename} "
    ]

    cmd = ' && '.join(cmds)
    tmux_command = f"tmux select-pane -R && tmux send-keys '{cmd}' 'C-m'"
    os.system(tmux_command)

def _run_test(fullpath, linenum):
    """Executes a specific test or a whole test suite.

    This function is intended for testing files. 

    If the 'linenum' (representing the cursor's position within a Vim session)
    falls within a test method or function, only that specific test is
    executed. 

    If 'linenum' is outside any specific test, the entire test suite is
    executed.

    Parameters:

    fullpath (str): The full path to the test file.
    linenum (int): The line number position of the cursor within a Vim session.
    """
    function_name, function_class = None, None
    function_name = _find_enclosing_function(fullpath, linenum)

    if function_name:
        function_class = _find_enclosing_class(fullpath, linenum)

    if function_name is None:
        # Not inside a test thus we need to run the whole suite.
        # Example of the resulting call:
        # python3.10 -m unittest  test_utils.py
        dirname = os.path.dirname(fullpath)
        basename = os.path.basename(fullpath)
        cmds = [
            f"cd {dirname}",
            "unset PYTHONBREAKPOINT",
            "clear",
            f"python3.10 -m unittest {basename} "
        ]
        cmd = ' && '.join(cmds)
        tmux_command = f"tmux select-pane -R && tmux send-keys '{cmd}' 'C-m'"
        os.system(tmux_command)
    else:
        # Inside a function. Try to run the specific test.
        # Example of the resulting call:
        # python3.10 -m unittest  test_utils.TestClass.test_func
        dirname = os.path.dirname(fullpath)
        basename = os.path.basename(fullpath)
        test_name = basename[:-3]
        if function_class:
            test_name += "."+ function_class
        test_name += "." + function_name
        cmds = [
            f"cd {dirname}",
            "unset PYTHONBREAKPOINT",
            "clear",
            f"python3.10 -m unittest {test_name} "
        ]
        cmd = ' && '.join(cmds)
        tmux_command = f"tmux select-pane -R && tmux send-keys '{cmd}' 'C-m'"
        os.system(tmux_command)


def _debug_script(fullpath):
    """Debugs the passed in script as a python program.

    Parameters:

    fullpath (str): The full path to the test file.
    """
    dirname = os.path.dirname(fullpath)
    basename = os.path.basename(fullpath)
    cmds = [
        f"cd {dirname}",
        "unset PYTHONBREAKPOINT",
        "clear",
        f"python3.10 -m ipdb {basename} "
    ]

    cmd = ' && '.join(cmds)
    tmux_command = f"tmux select-pane -R && tmux send-keys '{cmd}' 'C-m'"
    os.system(tmux_command)

def _debug_test(fullpath, linenum):
    """Executes a specific test or a whole test suite.

    This function is intended for testing files. 

    If the 'linenum' (representing the cursor's position within a Vim session)
    falls within a test method or function, only that specific test is
    executed. 

    If 'linenum' is outside any specific test, the entire test suite is
    executed.

    Parameters:

    fullpath (str): The full path to the test file.
    linenum (int): The line number position of the cursor within a Vim session.
    """
    function_name, function_class = None, None
    function_name = _find_enclosing_function(fullpath, linenum)

    if function_name:
        function_class = _find_enclosing_class(fullpath, linenum)

    if function_name is None:
        # Not inside a test thus we need to run the whole suite.
        # Example of the resulting call:
        # python3.10 -m unittest  test_utils.py
        dirname = os.path.dirname(fullpath)
        basename = os.path.basename(fullpath)
        cmds = [
            f"cd {dirname}",
            "export PYTHONBREAKPOINT=ipdb.set_trace",
            "clear",
            f"python3.10 -m unittest {basename} "
        ]
        cmd = ' && '.join(cmds)
        tmux_command = f"tmux select-pane -R && tmux send-keys '{cmd}' 'C-m'"
        os.system(tmux_command)
    else:
        # Inside a function. Try to run the specific test.
        # Example of the resulting call:
        # python3.10 -m unittest  test_utils.TestClass.test_func
        dirname = os.path.dirname(fullpath)
        basename = os.path.basename(fullpath)
        test_name = basename[:-3]
        if function_class:
            test_name += "."+ function_class
        test_name += "." + function_name
        cmds = [
            f"cd {dirname}",
            "export PYTHONBREAKPOINT=ipdb.set_trace",
            "clear",
            f"python3.10 -m unittest {test_name} "
        ]
        cmd = ' && '.join(cmds)
        tmux_command = f"tmux select-pane -R && tmux send-keys '{cmd}' 'C-m'"
        os.system(tmux_command)

class _FileType(enum.Enum):
    """Enumeration to descibe the type of a python script."""
    UNKNOWN = 0
    PYTHON_SCRIPT = 1
    PYTHON_TEST = 2


def _get_file_type(fullpath):
    """Returns the file type.

    Parameters:

    fullpath (str): The full path to the test file.
    """
    dirname = os.path.dirname(fullpath)
    basename = os.path.basename(fullpath)
    if basename.endswith(".py"):
        p = basename[:-3]
        if p.startswith("test") or p.endswith("test"):
            return _FileType.PYTHON_TEST
        else:
            return _FileType.PYTHON_SCRIPT
    else:
        return _FileType.UNKNOWN


def _find_enclosing_class(filename, lineno):
    """Returns the name of the class that enclosed the linenum.

    Parameters:

    fullpath (str): The full path to the test file.
    linenum (int): The line number position of the cursor within a Vim session.

    Returns: 
        Either the name of the enclosing class or None.
    """
    with open(filename, "r") as source:
        tree = ast.parse(source.read(), filename)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            if node.lineno <= lineno <= (node.lineno + node.body[-1].lineno):
                return str(node.name)
    return None


def _find_enclosing_function(filename, lineno):
    """Returns the name of the function that enclosed the linenum.

    Parameters:

    fullpath (str): The full path to the test file.
    linenum (int): The line number position of the cursor within a Vim session.

    Returns: 
        Either the name of the enclosing function or None.
    """
    with open(filename, "r") as source:
        tree = ast.parse(source.read(), filename)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if node.lineno <= node.lineno + lineno <= (node.lineno + node.body[-1].lineno):
                return str(node.name)
    return None

# Uncomment the following to run tests.
# if __name__ == '__main__':
#     # Self tests.
#     #current_dir = os.path.dirname(os.path.realpath(__file__))
#     # fullpath = os.path.join(current_dir, "test", "test_utils.py" )
#     # debug(fullpath , 13)
# 
#     #fullpath = os.path.join(current_dir, "test", "say_hello.py" )
#     fullpath = "/home/john/samples/junk.py"
#     debug(fullpath, 2)
# 
