# Windows Packaging

The production target is Python 3.13.7 on Windows. Build and installer validation must run on a Windows test machine.

Planned artifacts:

- GameNet Server service executable
- Operator App executable
- Client Agent/UI executable and Windows service wrapper
- Configuration, logs, data, and backup directories

Before packaging, run the full test suite and create a database backup. Do not run kiosk or lockdown tests on a production PC.