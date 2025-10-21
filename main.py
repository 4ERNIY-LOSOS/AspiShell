import sys
from aspi_shell.shell import AspiShellApp

if __name__ == "__main__":
    app = AspiShellApp()
    sys.exit(app.run(sys.argv))
