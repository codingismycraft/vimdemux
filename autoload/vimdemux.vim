let s:plugin_path = expand('<sfile>:p:h')
let s:path_was_added = 0

python3 << endpython

import os
import sys
import vim


def preparePythonPath():
    """Adds the path of the related code to the python path.

    The path is added only once since we rely on a script scoped
    variable (path_was_added) as the import guard.
    """
    was_added = int(vim.eval("s:path_was_added"))
    if not was_added:
        path = vim.eval("s:plugin_path")
        path = os.path.dirname(path)
        sys.path.insert(0, path)
        vim.command("let s:path_was_added = 1")

endpython

function! vimdemux#RunIt()
let git_info = "n/a" 
python3 << endpython
preparePythonPath()
import vimdemux.utils as utils
import vim
import os
fullpath = vim.eval(""" expand('%:p') """)
linenum = int(vim.eval(""" line(".") """)) 
utils.run(fullpath, linenum)
endpython
return git_info
endfunction


function! vimdemux#DebugIt()
let git_info = "n/a" 
python3 << endpython
preparePythonPath()
import vimdemux.utils as utils
import vim
import os
fullpath = vim.eval(""" expand('%:p') """)
linenum = int(vim.eval(""" line(".") """)) 
utils.debug(fullpath, linenum)
endpython
return git_info
endfunction
