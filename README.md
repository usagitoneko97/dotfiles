My dotfiles powered by GNU stow. Make sure `stow` is installed in the system to use the dotfiles.

## Adding/modifying dotfiles
Adding or modifying dotfiles will not involve stow at all. Simply modify the content of dotfiles and commit/push.

Stow command can be run with arguments of any folder presented here.
When running `stow <dir>`, stow looked in the folder `<dir>`, and symlink the content of `<dir` *one folder* above the `stow` command was run, or simply use `-t` arg.

## Installing
By using stow, you can choose which dots to install. E.g.:
```bash
stow x vim -t ~/
```
