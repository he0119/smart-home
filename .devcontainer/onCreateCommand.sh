#!/bin/bash
# https://github.com/microsoft/vscode-python/blob/main/scripts/onCreateCommand.sh

# Install pyenv and Python versions here to avoid using shim.
curl https://pyenv.run | bash
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
# zsh support
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv init -)"' >> ~/.zshrc

export PYENV_ROOT="$HOME/.pyenv"
command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"
# eval "$(pyenv init -)" Comment this out and DO NOT use shim.
source ~/.bashrc

# Install Python via pyenv .
pyenv install 3.11:latest

# Set default Python version to 3.11 .
pyenv global 3.11
