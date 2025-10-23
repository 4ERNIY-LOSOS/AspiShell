import asyncio
import argparse
import logging
import sys

from dbus_next.aio import MessageBus
from dbus_next.errors import DBusError

SERVICE_NAME = 'com.aspi.shell.Control'
OBJECT_PATH = '/com/aspi/shell'

async def main():
    parser = argparse.ArgumentParser(description="Command-line interface for AspiShell.")
    subparsers = parser.add_subparsers(dest='command', required=True)

    # Команда для левой панели
    parser_toggle_left = subparsers.add_parser('toggle-left-panel', help='Toggle the left panel')

    # Команда для правой панели
    parser_toggle_right = subparsers.add_parser('toggle-right-panel', help='Toggle the right panel')

    args = parser.parse_args()

    retries = 3
    for i in range(retries):
        try:
            bus = await MessageBus().connect()
            introspection = await bus.introspect(SERVICE_NAME, OBJECT_PATH)
            proxy = bus.get_proxy_object(SERVICE_NAME, OBJECT_PATH, introspection)
            interface = proxy.get_interface(SERVICE_NAME)

            if args.command == 'toggle-left-panel':
                await interface.call_toggle_left_panel()
                logging.info("Called ToggleLeftPanel method.")
            elif args.command == 'toggle-right-panel':
                await interface.call_toggle_right_panel()
                logging.info("Called ToggleRightPanel method.")
            
            # If successful, break the loop
            break

        except DBusError as e:
            if "The name is not activatable" in str(e) and i < retries - 1:
                logging.warning("Service not ready, retrying in 1s...")
                await asyncio.sleep(1)
                continue
            else:
                logging.error(f"DBus error: {e}. Is AspiShell running?")
                sys.exit(1)
        except Exception as e:
            logging.error("An unexpected error occurred", exc_info=True)
            sys.exit(1)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    asyncio.run(main())
