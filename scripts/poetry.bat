@echo off
set "cmd=podman compose exec django poetry"
%cmd% %*