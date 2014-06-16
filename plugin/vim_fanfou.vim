" vim fanfou client

" Load this module only once.
if exists('loaded_vimfanfou')
    finish
endif

" Check vim python runtime
if !has('python')
    echo "Error: Required vim compiled with +python"
    finish
endif

" Check vim version
if v:version < 700
    echo "Error: Required vim version 7+"
    finish
endif

" Set the loaded flag
let loaded_mytestplugin = 1

" update import path
python import sys, vim
python sys.path.append(vim.eval('expand("<sfile>:h")'))

" Startup vim_fanfou
" TODO: load consumer_key from config file
python << end_python
import vim_fanfou, vim
cfg = {
    "consumer_key": "",
    "consumer_secret": "",
    "auth_cache": ".fanfou_auth_cache",
}
vim_fanfou.vim_fanfou.vim_fanfou_init(cfg)
end_python

function! TestFunc()
python << end_python

import vim_fanfou

end_python
endfunction


