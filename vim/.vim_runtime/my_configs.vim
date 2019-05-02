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
