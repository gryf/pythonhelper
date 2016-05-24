" File: pythonhelper.vim
" Author: Michal Vitecek <fuf-at-mageo-dot-cz>
" Author: Roman Dobosz <gryf@vimja.com>
" Version: 0.85
" Last Modified: 2016-05-24
"
" Overview
" --------
" This Vim script helps you find yourself in larger Python source files. It
" displays the current Python class, method or function the cursor is placed
" on in the status line. It's smarter than Yegappan Lakshmanan's taglist.vim
" because it takes indentation and comments into account in order to determine
" what identifier the cursor is placed on.
"
" Requirements
" ------------
" This script needs only VIM compiled with the Python interpreter. It doesn't
" rely on the exuberant ctags utilities. You can determine whether your VIM
" has Python support by issuing command :ver and looking for +python or
" +python3 in the list of features.
"
" Installation
" ------------
" 1. Make sure your Vim has the Python feature enabled (+python). If not, you
"    will need to recompile it with the --with-pythoninterp option passed to
"    the configure script
" 2. Copy the pythonhelper.vim script to the $HOME/.vim/plugin directory, or
"    install it in some other way (vim-addon-manager, pathogen, ...)
" 3. Add '%{TagInStatusLine()}' to the statusline in your vimrc. You can also
"    use %{TagInStatusLineTag()} or %{TagInStatusLineType()} for just the tag
"    name or tag type respectively.
" 4. Run Vim and open any Python file.

" VIM functions {{{
let g:pythonhelper_python = 'python'
let s:plugin_path = expand('<sfile>:p:h', 1)

function! s:PHLoader()

    if !exists('g:pythonhelper_py_loaded')
        if has('python')
            exe 'pyfile ' . s:plugin_path . '/pythonhelper.py'
        elseif has('python3')
            let g:pythonhelper_python = 'python3'
            exe 'py3file ' . s:plugin_path . '/pythonhelper.py'
        else
            echohl WarningMsg|echomsg
                        \ "PythonHelper unavailable: "
                        \ "requires Vim with Python support"|echohl None
            finish
        endif
        let g:pythonhelper_py_loaded = 1
    else
        echohl "already loaded"
    endif
endfunction


function! PHCursorHold()
    " only Python is supported {{{
    if (!exists('b:current_syntax') || (b:current_syntax != 'python'))
        let w:PHStatusLine = ''
        let w:PHStatusLineTag = ''
        let w:PHStatusLineType = ''
        return
    endif
    " }}}

    " call Python function findTag() with the current buffer number and change
    " status indicator
    execute g:pythonhelper_python . ' PythonHelper.find_tag(' . expand("<abuf>") .
                \ ', ' . b:changedtick . ')'
endfunction


function! PHBufferDelete()
    " set the PHStatusLine etc for this window to an empty string
    let w:PHStatusLine = ""
    let w:PHStatusLineTag = ''
    let w:PHStatusLineType = ''

    " call Python function deleteTags() with the current buffer number and
    " change status indicator
    execute g:pythonhelper_python . ' PythonHelper.delete_tags(' . expand("<abuf>") . ')'
endfunction


function! TagInStatusLine()
    " return value of w:PHStatusLine in case it's set
    if (exists("w:PHStatusLine"))
        return w:PHStatusLine
    " otherwise just return an empty string
    else
        return ""
    endif
endfunction


function! TagInStatusLineTag()
    " return value of w:PHStatusLineTag in case it's set
    if (exists("w:PHStatusLineTag"))
        return w:PHStatusLineTag
    " otherwise just return an empty string
    else
        return ""
    endif
endfunction


function! TagInStatusLineType()
    " return value of w:PHStatusLineType in case it's set
    if (exists("w:PHStatusLineType"))
        return w:PHStatusLineType
    " otherwise just return an empty string
    else
        return ""
    endif
endfunction


function! PHPreviousClassMethod()
    call search('^[ \t]*\(class\|def\)\>', 'bw')
endfunction


function! PHNextClassMethod()
    call search('^[ \t]*\(class\|def\)\>', 'w')
endfunction


function! PHPreviousClass()
    call search('^[ \t]*class\>', 'bw')
endfunction


function! PHNextClass()
    call search('^[ \t]*class\>', 'w')
endfunction


function! PHPreviousMethod()
    call search('^[ \t]*def\>', 'bw')
endfunction


function! PHNextMethod()
    call search('^[ \t]*def\>', 'w')
endfunction

" }}}

" event binding, Vim customization {{{

" load Python code
call s:PHLoader()

" autocommands
autocmd CursorHold * call PHCursorHold()
autocmd CursorHoldI * call PHCursorHold()
autocmd BufDelete * silent call PHBufferDelete()

" period of no activity after which the CursorHold event is triggered
if (exists("g:pythonhelper_updatetime"))
    let &updatetime = g:pythonhelper_updatetime
endif

" }}}

" vim:foldmethod=marker
