import sys
import logging
from aspi_shell.ui.shell import AspiShellApp
from aspi_shell.utils.logging import setup_logging
from aspi_shell.utils.config import config_manager

if __name__ == "__main__":
    setup_logging()
    logging.info("Starting AspiShell...")
    config_manager.load()
    logging.info("Configuration loaded.")
    app = AspiShellApp()
    sys.exit(app.run(sys.argv))
