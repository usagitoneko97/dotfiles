"" ==> Personal Preference	
" ----------------------------------	
vnoremap <leader>r "hy:%s/<C-r>h//gc<left><left><left>	
 " window navigation	
nnoremap <a-h> gT	
nnoremap <a-l> gt	
 " set relative number 	
:set number relativenumber	
 :augroup numbertoggle	
:  autocmd!	
:  autocmd BufEnter,FocusGained,InsertLeave * set relativenumber	
:  autocmd BufLeave,FocusLost,InsertEnter   * set norelativenumber	
:augroup END

" Set 10 lines to the cursor - when moving vertically using j/k	" Set 7 lines to the cursor - when moving vertically using j/k
set so=5

" easy system clipboard copy/paste	
noremap <leader>y "*y	
noremap <leader>yy "*Y	
noremap <leader>p "*p	
noremap <leader>P "*P

" jk as esc 
inoremap jk <Esc>`^

nnoremap <CR> } 
nnoremap K { 
:autocmd CmdwinEnter * nnoremap <CR> <CR>
:autocmd BufReadPost quickfix nnoremap <CR> <CR>

set timeoutlen=250
" When shortcut files are updated, renew bash and vifm configs with new material:
autocmd BufWritePost ~/.config/bmdirs,~/.config/bmfiles !shortcuts

autocmd filetype perl nnoremap <leader>r <Esc>:w<CR>:!clear;perl %<CR>
autocmd filetype tcl nnoremap <leader>r <Esc>:w<CR>:!clear;tclsh %<CR>
autocmd filetype python nnoremap <leader>r <Esc>:w<CR>:!clear;python %<CR>
