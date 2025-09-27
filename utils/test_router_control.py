import sys
import os
import json

# Add the utils directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all required imports are available"""
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException
        print("✓ All Selenium imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_config_loading():
    """Test configuration loading functionality"""
    try:
        # Test creating a sample config file
        test_config = {
            "router_ip": "192.168.1.1",
            "username": "test_user",
            "password": "test_pass"
        }

        with open("test_config.json", "w") as f:
            json.dump(test_config, f)

        # Test loading config
        from enhanced_router_control import TPLinkWAN2Controller
        controller = TPLinkWAN2Controller(config_file="test_config.json")

        assert controller.config["router_ip"] == "192.168.1.1"
        assert controller.config["username"] == "test_user"
        assert controller.config["password"] == "test_pass"

        # Clean up
        os.remove("test_config.json")

        print("✓ Configuration loading test successful")
        return True
    except Exception as e:
        print(f"✗ Configuration loading test failed: {e}")
        # Clean up if file exists
        if os.path.exists("test_config.json"):
            os.remove("test_config.json")
        return False

def test_controller_initialization():
    """Test controller initialization"""
    try:
        from enhanced_router_control import TPLinkWAN2Controller
        controller = TPLinkWAN2Controller(
            router_ip="192.168.1.1",
            username="test_user",
            password="test_pass"
        )

        assert controller.config["router_ip"] == "192.168.1.1"
        assert controller.config["username"] == "test_user"
        assert controller.config["password"] == "test_pass"

        print("✓ Controller initialization test successful")
        return True
    except Exception as e:
        print(f"✗ Controller initialization test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Testing Enhanced Router Control Script...")
    print("=" * 50)

    tests = [
        test_imports,
        test_config_loading,
        test_controller_initialization
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} failed with exception: {e}")
            failed += 1

    print("=" * 50)
    print(f"Tests completed: {passed} passed, {failed} failed")

    if failed == 0:
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())

