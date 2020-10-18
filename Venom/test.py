from selenium import webdriver

capabilities = {
    "browserName": "Chrome",
    "browserVersion": "",
    "selenoid:options": {
        "enableVNC": True,
        "enableVideo": False
    }
}

driver = webdriver.Remote(
    command_executor="http://selenoid-uri:4444/wd/hub",
    desired_capabilities=capabilities)
