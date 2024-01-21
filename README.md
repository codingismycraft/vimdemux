# vimdemux
A Vim plugin integrated with Tmux for easier debugging.

# Requirements

- pytest

```
pip install pytest
```

- pdbpp


```
pip install pdbpp>=0.10.3
```

# Installation

`.vimrc`

```
call vundle#begin()
...
Plugin 'codingismycraft/vimdemux'
call vundle#end()            
```

From vim run the following:
```
:PluginInstall
```

`.pdbrc`

Add the following lines to `~/.pdbrc`

```
import os
filename = os.path.join(os.path.expanduser("~"), ".pdbrc")
alias bs with open(filename, 'a') as pdbrc: pdbrc.write('break ' + __file__ + ':%1\n')
```

# Usage

Open the python code as a left pane in a tmux pane.
Next to the code open another vertical tmux pane.


To run the python script:

```
<leader>r 
```

To debug the python script:

```
<leader>d 
```


# Vagrant Support

To debug under vagrant:

- On the right pane ssh to the guest

- Add the following mapping to the `~/.vimdemux`

`.vimdemux`

```json
{
    "root-mappings": [
        ["<local-full-path>", "<remote-full-path>"]
    ],
}
```

