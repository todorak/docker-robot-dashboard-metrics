*** Settings ***
Library    SeleniumLibrary
Library    BuiltIn
Resource   ../resources/common.robot

Documentation    Example Robot Framework tests
Default Tags     smoke

*** Variables ***
${URL}           https://example.com
${BROWSER}       headlesschrome
${TIMEOUT}       10s
#${options}    add_argument("--ignore-certificate-errors"); add_argument("--disable-extensions"); add_argument("--disable-notifications"); add_argument("--no-sandbox"); add_argument("--disable-dev-shm-usage"); add_argument("--disable-gpu"); add_argument("--user-data-dir=/tmp/chrome-${PABOTEXECUTIONPOOLID}")
#${options}    add_argument("--ignore-certificate-errors"); add_argument("--disable-extensions"); add_argument("--disable-notifications"); add_argument("--no-sandbox"); add_argument("--disable-dev-shm-usage"); add_argument("--disable-gpu"); add_argument("--headless")
${options}                          add_argument("--ignore-certificate-errors"); add_argument("--disable-extensions");
...    add_argument("--disable-notifications"); add_argument("--no-sandbox")


*** Test Cases ***
Simple Web Test
    [Documentation]    Basic web test example
    [Tags]    smoke    web    quick
    Open Browser                         ${URL}     ${BROWSER}  options=${options}    alias=MAIN
    Set Log Level                       TRACE
    #Open Browser    ${URL}    ${BROWSER}
    Wait Until Page Contains    Example Domain    timeout=${TIMEOUT}
    Page Should Contain    Example Domain
    Capture Page Screenshot
    Close Browser

API Test Placeholder
    [Documentation]    API test example
    [Tags]    smoke    api
    Log    This is a placeholder for API tests
    Should Be Equal As Strings    OK    OK

Math Test
    [Documentation]    Simple calculation test
    [Tags]    smoke    unit
    ${result}=    Evaluate    2 + 2
    Should Be Equal As Numbers    ${result}    4

String Test
    [Documentation]    String manipulation test
    [Tags]    smoke    unit
    ${text}=    Set Variable    Hello Robot Framework
    Should Contain    ${text}    Robot
    ${length}=    Get Length    ${text}
    Should Be True    ${length} > 0

Slow Test Example
    [Documentation]    Test that takes some time
    [Tags]    slow
    Log    Starting slow test...
    Sleep    2s
    Log    Slow test completed
    Should Be True    True

Conditional Test
    [Documentation]    Test with conditions
    [Tags]    smoke    logic
    ${value}=    Set Variable    5
    Run Keyword If    ${value} > 3    Log    Value is greater than 3
    ...    ELSE    Fail    Value should be greater than 3

Loop Test Example
    [Documentation]    Test with loop
    [Tags]    smoke    loop
    FOR    ${i}    IN RANGE    1    4
        Log    Iteration ${i}
        Should Be True    ${i} > 0
    END

Failing Test Example
    [Documentation]    This test will fail intentionally
    [Tags]    fail    demo
    Log    This test demonstrates a failure
    Should Be Equal    1    2    This will always fail

Random Test
    [Documentation]    This test randomly passes or fails
    [Tags]    smoke    flaky
    ${random}=    Evaluate    random.randint(0, 100)    modules=random
    Should Be True    ${random} > 30    Test failed randomly

*** Keywords ***
# Add custom keywords here if needed
