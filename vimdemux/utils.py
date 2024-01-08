
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
    filetype = _get_file_type(fullpath) 
    if filetype == _FileType.PYTHON_SCRIPT:
        _debug_script(fullpath)
    elif filetype == _FileType.PYTHON_TEST:
        _debug_test(fullpath, linenum)
    else:
        print(f"Dont now how to debug {fullpath}")

# Private stuff goes after this line.

_SEND_IT = "'C-m'" 

def _run_script(fullpath):
    """Runs the passed in script as a python program."""
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
    """Debugs the passed in script as a python program."""
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
    UNKNOWN = 0
    PYTHON_SCRIPT = 1
    PYTHON_TEST = 2

def _get_file_type(fullpath):
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
    with open(filename, "r") as source:
        tree = ast.parse(source.read(), filename)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            if node.lineno <= lineno <= (node.lineno + node.body[-1].lineno):
                return str(node.name)
    return None

def _find_enclosing_function(filename, lineno):
    with open(filename, "r") as source:
        tree = ast.parse(source.read(), filename)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if node.lineno <= node.lineno + lineno <= (node.lineno + node.body[-1].lineno):
                return str(node.name)
    return None

if __name__ == '__main__':
    #run("/home/john/samples/geoloc/junk2.py", 8)
    # run("/home/john/samples/geoloc/test_utils.py", 8)
    debug("/home/john/samples/geoloc/test_utils.py", 13)
    #print(_find_enclosing_class("/home/john/samples/geoloc/test_utils.py",8))
    #function, func_range = find_definition("/home/john/samples/geoloc/test_utils.py",8)
    #print(function, func_range)
    #exit(0)
    #x = "/home/john/samples/geoloc/junk2.py"
    #run(x, 1)
