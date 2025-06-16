from bot.browser import launch_browser
from bot.actions import bruteforce_login

def main():
    playwright, browser, page = launch_browser()
    try:
        bruteforce_login(page, "admin", ["password123", "admin123", "letmein", "123456", "password", "admin", "qwerty", "abc123", "pass"])
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        browser.close()
        playwright.stop()

if __name__ == "__main__":
    main()
