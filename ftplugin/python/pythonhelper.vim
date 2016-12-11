" File: pythonhelper.vim
" Author: Michal Vitecek <fuf-at-mageo-dot-cz>
" Author: Roman Dobosz <gryf@vimja.com>
" Version: 1.1
" License: 3-clause BSD license
" Last Modified: 2016-12-10

" VIM functions {{{
let s:plugin_path = expand('<sfile>:p:h', 1)


function! s:SetPython(msg)
    if !exists('g:_python')
        if has('python')
            let g:_python = {'exec': 'python', 'file': 'pyfile'}
        elseif has('python3')
            let g:_python = {'exec': 'python3', 'file': 'py3file'}
        else
            echohl WarningMsg|echomsg a:msg|echohl None
            finish
        endif
    endif
endfunction


function! s:PHLoader()
    if !exists('g:pythonhelper_py_loaded')
        call s:SetPython("PythonHelper unavailable: "
                    \ . "requires Vim with Python support")
        execute g:_python['file'] . ' ' . s:plugin_path . '/pythonhelper.py'
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
    execute g:_python['exec'] . ' PythonHelper.find_tag(' . expand("<abuf>") .
                \ ', ' . b:changedtick . ')'
endfunction


function! PHBufferDelete()
    " set the PHStatusLine etc for this window to an empty string
    let w:PHStatusLine = ""
    let w:PHStatusLineTag = ''
    let w:PHStatusLineType = ''

    " call Python function deleteTags() with the current buffer number and
    " change status indicator
    execute g:_python['exec'] . ' PythonHelper.delete_tags(' . expand("<abuf>") . ')'
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
