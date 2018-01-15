#!/bin/bash
{ python.exe "$@" 2<&1 1>&3 | cat 1>&2; } 3>&1 | cat
