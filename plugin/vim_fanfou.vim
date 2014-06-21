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

" Startup vim_fanfou
" TODO: load consumer_key from config file
python << end_python
# update import path
import sys, vim
sys.path.append(vim.eval('expand("<sfile>:h")'))

# import vim_fanfou.py and startup it
from vim_fanfou import vim_fanfou
VIM = vim_fanfou.VIM
VIM.set_vim_mod(vim)
cfg = {
    "consumer_key": VIM.get_val("g:fanfou_consumer_key"),
    "consumer_secret": VIM.get_val("g:fanfou_consumer_secret"),
    "auth_cache": VIM.get_val("g:fanfou_auth_cache"),
    "log_file": VIM.get_val("g:fanfou_log_file"),
    "log_level": VIM.get_val("g:fanfou_log_level"),
    "buf_name": VIM.get_val("g:fanfou_buf_name"),
}
vim_fanfou.VimFanfou.init(cfg)
end_python

" get Fanfou home timeline
function! s:update_home_timeline()
python << end_python
from vim_fanfou import vim_fanfou
VIM_FANFOU = vim_fanfou.VimFanfou.get_instance()
VIM_FANFOU.update_home_timeline()
end_python
endfunction

function! s:refresh()
python << end_python
from vim_fanfou import vim_fanfou
VIM_FANFOU = vim_fanfou.VimFanfou.get_instance()
VIM_FANFOU.refresh()
end_python
endfunction

" VIM commands
if !exists(":FanfouHomeTimeline")
    command FanfouHomeTimeline :call s:update_home_timeline()
endif
if !exists(":FanfouRefresh")
    command FanfouRefresh :call s:refresh()
endif

