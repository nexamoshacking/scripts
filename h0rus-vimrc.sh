#!/usr/bin/env bash
# ============================================
# 🧠 Instalador de configuração moderna do Vim
# Inclui:
# - Tema escuro
# - Ctrl+C / Ctrl+V para copiar/colar linhas ou seleção
# - Ctrl+S / Ctrl+Q para salvar/sair
# - Movimento estilo WASD
# - Atalho "a" para ir para o final da linha
# - Backup automático do .vimrc antigo
# - Sem pisca da tela (visualbell)
# Autor: srhorus
# ============================================

VIMRC="$HOME/.vimrc"
BACKUP="$HOME/.vimrc.bak"

echo "🚀 Instalador de configuração moderna do Vim"
echo "----------------------------------------------"
echo

# Backup do .vimrc antigo
if [ -f "$VIMRC" ]; then
    echo "🗂️  Backup criado em $BACKUP"
    mv "$VIMRC" "$BACKUP"
fi

echo "🧩 Gerando arquivo ~/.vimrc ..."
sleep 1

cat <<'EOF' > "$VIMRC"
" ==========================================
"   🧠 VIM MODERNO — CONFIG BY SRHORUS
" ==========================================

" -----------------------
" BÁSICO E INTERFACE
" -----------------------
set encoding=utf-8
set fileencoding=utf-8
syntax on
set number
set relativenumber
set cursorline
set showmatch
set ruler
set laststatus=2
set title
set mouse=a
set termguicolors
set background=dark

set tabstop=4
set shiftwidth=4
set expandtab
set autoindent
set smartindent
set clipboard=unnamedplus
set scrolloff=5
set wrap
set linebreak
set ignorecase
set smartcase
set incsearch
set hlsearch
set nobackup
set nowritebackup
set noswapfile
set history=1000

" -----------------------
" TEMA (GRUVBOX-STYLE)
" -----------------------
hi Normal       ctermfg=223 ctermbg=235
hi Comment      ctermfg=102
hi Constant     ctermfg=208
hi Identifier   ctermfg=178
hi Statement    ctermfg=215
hi PreProc      ctermfg=173
hi Type         ctermfg=179
hi Special      ctermfg=180
hi Underlined   ctermfg=109
hi Todo         ctermfg=209 ctermbg=237
hi CursorLine   ctermbg=236
hi Visual       ctermbg=238
hi LineNr       ctermfg=241
hi CursorLineNr ctermfg=214
hi StatusLine   ctermfg=223 ctermbg=237
hi StatusLineNC ctermfg=241 ctermbg=236
hi VertSplit    ctermfg=238 ctermbg=238

let mapleader=" "

" -----------------------
" SALVAR / SAIR
" -----------------------
nnoremap <C-s> :w<CR>
inoremap <C-s> <Esc>:w<CR>a
nnoremap <C-q> :q<CR>
inoremap <C-q> <Esc>:q<CR>
nnoremap <leader>w :w<CR>
nnoremap <leader>x :x<CR>
nnoremap <leader>q :q<CR>

" -----------------------
" BUSCA
" -----------------------
nnoremap <leader><space> :nohlsearch<CR>

" -----------------------
" EXPLORER / ARQUIVOS
" -----------------------
nnoremap <leader>e :Ex<CR>

" -----------------------
" SPLITS
" -----------------------
nnoremap <leader>sv :vsplit<CR>
nnoremap <leader>sh :split<CR>
nnoremap <leader>h <C-w>h
nnoremap <leader>j <C-w>j
nnoremap <leader>k <C-w>k
nnoremap <leader>l <C-w>l

" -----------------------
" COPIAR / COLAR
" -----------------------
nnoremap <C-c> "+yy
vnoremap <C-c> "+y
nnoremap <C-v> "+p
vnoremap <C-v> "+p
inoremap <C-v> <C-r>+
cnoremap <C-v> <C-r>+

" -----------------------
" MOVIMENTAÇÃO MODERNA (WASD)
" -----------------------
nnoremap w k
nnoremap s j
nnoremap a h
nnoremap d l
vnoremap w k
vnoremap s j
vnoremap a h
vnoremap d l

nnoremap <C-a> 0
nnoremap <C-d> $
nnoremap <C-w> b
nnoremap <C-s> e

" Atalho para ir para o final da linha
nnoremap A $

silent! unmap <Up>
silent! unmap <Down>
silent! unmap <Left>
silent! unmap <Right>

" -----------------------
" COMENTAR RÁPIDO
" -----------------------
nnoremap <leader>c I# <Esc>
vnoremap <leader>c :s/^/# /<CR>:noh<CR>

" -----------------------
" RECARREGAR CONFIG
" -----------------------
nnoremap <leader>r :source $MYVIMRC<CR>

" -----------------------
" AJUSTES FINAIS (SEM PISCA)
" -----------------------
set showcmd
set showmode
set noerrorbells
set novisualbell
set t_vb=
EOF

echo
echo "✅ Configuração moderna criada com sucesso!"
echo "📂 Arquivo salvo em: $VIMRC"
echo
echo "🧠 Teste no Vim:"
echo "   - Ctrl+S → Salvar"
echo "   - Ctrl+Q → Sair"
echo "   - Ctrl+C → Copiar linha ou seleção"
echo "   - Ctrl+V → Colar"
echo "   - <Leader>e (Space+e) → Explorer"
echo "   - <Leader>sv/sh → Split vertical/horizontal"
echo "   - WASD → mover o cursor (modo gamer 😎)"
echo "   - A → ir para o final da linha"
