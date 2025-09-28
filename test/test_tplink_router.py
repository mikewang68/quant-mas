#!/usr/bin/env python3

import sys
from tplinkrouterc6u import TplinkRouterProvider

def test_router_connection():
    # Router configuration
    ROUTER_IP = "192.168.1.1"
    USERNAME = "wangdg68"
    PASSWORD = "wap951020ZJL"

    print(f"Testing connection to TP-Link router at {ROUTER_IP}")
    print(f"Username: {USERNAME}")

    try:
        # Try to get a client for the router
        print("Attempting to connect to router...")
        router = TplinkRouterProvider.get_client(f'http://{ROUTER_IP}', PASSWORD, USERNAME)
        print(f"Successfully created router client: {type(router)}")

        # Try to authorize
        print("Attempting to authorize...")
        router.authorize()
        print("Authorization successful!")

        # Try to get firmware info
        print("Getting firmware info...")
        firmware = router.get_firmware()
        print(f"Firmware info: {firmware}")

        # Try to get status
        print("Getting router status...")
        status = router.get_status()
        print(f"Router status: {status}")

        # Logout
        router.logout()
        print("Logged out successfully")

        return True

    except Exception as e:
        print(f"Error connecting to router: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_router_connection()
    sys.exit(0 if success else 1)

