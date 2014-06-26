" ==============================================================
" vim_fanfou - Fanfou client for VIM
" git repository: https://github.com/xiongjia/vim-fanfou.git
" Version: 0.0.1
" Language: Python + Vim script
" Maintainer: LeXiongJia <lexiongjia@gmail.com>
" ==============================================================

" Load this module only once.
if exists('loaded_vimfanfou')
    finish
endif

" Check VIM python runtime
if !has('python')
    echo "Error: Required VIM compiled with +python"
    finish
endif

" Check VIM version
if v:version < 700
    echo "Error: Required VIM version 7+"
    finish
endif

" Set the loaded flag
let loaded_vimfanfou = 1
let s:loaded_vimfanfou_path = expand("<sfile>:h")

" load python modules
function! s:load_py_mod()
python << end_python
# update import path
import sys, vim
sys.path.append(vim.eval("s:loaded_vimfanfou_path"))

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
    "fanfou_http_proxy": VIM.get_val("g:fanfou_http_proxy"),
}
vim_fanfou.VimFanfou.init(cfg)
end_python
endfunction

function! s:init()
    if !exists('s:loaded_py_mod')
        call s:load_py_mod()
    endif
    let s:loaded_py_mod = 1
endfunction

" get Fanfou home timeline
function! s:update_home_timeline()
    call s:init()
python << end_python
from vim_fanfou import vim_fanfou
VIM_FANFOU = vim_fanfou.VimFanfou.get_instance()
VIM_FANFOU.update_home_timeline()
end_python
endfunction

" post status
function! s:post_status()
    call s:init()
    call inputsave()
    redraw
    let mesg = input("Status: ")
    call inputrestore()
python << end_python
from vim_fanfou import vim_fanfou
VIM = vim_fanfou.VIM
VIM_FANFOU = vim_fanfou.VimFanfou.get_instance()
VIM_FANFOU.post_status(VIM.get_val("mesg"))
end_python
endfunction

" refresh
function! s:refresh()
    call s:init()
python << end_python
from vim_fanfou import vim_fanfou
VIM_FANFOU = vim_fanfou.VimFanfou.get_instance()
VIM_FANFOU.refresh()
end_python
endfunction

function! s:login()
    call s:init()
python << end_python
from vim_fanfou import vim_fanfou
VIM_FANFOU = vim_fanfou.VimFanfou.get_instance()
VIM_FANFOU.login()
end_python
endfunction

" Exports VIM commands
if !exists(":FanfouHomeTimeline")
    command FanfouHomeTimeline :call s:update_home_timeline()
endif

if !exists(":FanfouRefresh")
    command FanfouRefresh :call s:refresh()
endif

if !exists(":FanfouPostStatus")
    command FanfouPostStatus :call s:post_status()
endif

if !exists(":FanfouSetAccount")
    command FanfouSetAccount :call s:login()
endif

if !exists(":FanfouSwitchAccount")
    command FanfouSwitchAccount :call s:login()
endif

