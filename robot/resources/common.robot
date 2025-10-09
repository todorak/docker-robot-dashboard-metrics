*** Settings ***
Documentation    Common keywords and variables for all tests
Library          SeleniumLibrary
Library          BuiltIn

*** Variables ***
# Default timeouts
${DEFAULT_TIMEOUT}     10s
${SHORT_TIMEOUT}       5s
${LONG_TIMEOUT}        30s

# Browser settings
${BROWSER}             headlesschrome
${SELENIUM_SPEED}      0.0

# Common URLs
${BASE_URL}            https://example.com

*** Keywords ***
Open Browser To URL
    [Documentation]    Opens browser to specified URL
    [Arguments]    ${url}=${BASE_URL}    ${browser}=${BROWSER}
    Open Browser    ${url}    ${browser}
    Maximize Browser Window
    Set Selenium Speed    ${SELENIUM_SPEED}

Close All Browsers And Clean
    [Documentation]    Closes all browsers and cleans up
    Close All Browsers

Wait And Click Element
    [Documentation]    Waits for element and clicks it
    [Arguments]    ${locator}    ${timeout}=${DEFAULT_TIMEOUT}
    Wait Until Element Is Visible    ${locator}    timeout=${timeout}
    Click Element    ${locator}

Wait And Input Text
    [Documentation]    Waits for element and inputs text
    [Arguments]    ${locator}    ${text}    ${timeout}=${DEFAULT_TIMEOUT}
    Wait Until Element Is Visible    ${locator}    timeout=${timeout}
    Input Text    ${locator}    ${text}

Take Screenshot On Failure
    [Documentation]    Takes screenshot when test fails
    Run Keyword If Test Failed    Capture Page Screenshot
