#
# ~/.bashrc
#

# If not running interactively, don't do anything
[[ $- != *i* ]] && return

alias ls='ls --color=auto'
PS1='[\u@\h \W]\$ '
source ~/.profile
export JAVA_HOME="/opt/jre-12.0.2/"


source <(echo "(navi widget zsh)")
source /home/usagitoneko/.config/broot/launcher/bash/br
