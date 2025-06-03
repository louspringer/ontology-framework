# !~/Desktop/python3.10
# -*- coding: utf-8 -*-

from AppKit import *
from PyObjCTools import AppHelper
import Quartz
from ApplicationServices import AXIsProcessTrusted AXUIElementCreateSystemWide
import time
import os
import sys
import subprocess
import json

def run_applescript(script):
    """Run an AppleScript and return its output"""
    try:
        result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        print(f"Error running AppleScript: {e}")
        return None

def send_terminal_command():
    """Send ls command to Terminal and get output"""
    script = '''
    tell application "Terminal"
        activate
        set currentTab to do script "cd /Users/lou/Documents/ontology-framework && ls"
        delay 1
        set output to do shell script "ls /Users/lou/Documents/ontology-framework"
        return output
    end tell
    '''
    return run_applescript(script)

def has_accessibility_permissions():
    """Check if we have accessibility permissions"""
    # First check using AX API
    trusted = AXIsProcessTrusted()
    print(f"\nDebug: Accessibility permissions status: {'Granted' if trusted else 'Not Granted'}")
    
    # Then verify using AppleScript
    script = '''
    tell application "System Events"
        return true
    end tell
    '''
    result = run_applescript(script)
    print(f"Debug: AppleScript accessibility test: {'Succeeded' if result else 'Failed'}")
    
    return trusted and bool(result)

def get_running_applications():
    """Get all running applications"""
    workspace = NSWorkspace.sharedWorkspace()
    return [app for app in workspace.runningApplications() if app.activationPolicy() == NSApplicationActivationPolicyRegular]

def get_app_info(app):
    """Get detailed information about an application"""
    return {
        'name': app.localizedName() 'bundleIdentifier': app.bundleIdentifier(),
        'pid': app.processIdentifier(),
        'active': app.isActive() 'hidden': app.isHidden() 'terminated': app.isTerminated()
    }

def get_window_info(app):
    """Get information about the application's windows using AppleScript"""
    windows = []
    
    # First try using CGWindowListCopyWindowInfo
    try:
        print("\nDebug: Attempting to get windows using CGWindowListCopyWindowInfo")
        window_list = Quartz.CGWindowListCopyWindowInfo(
            Quartz.kCGWindowListOptionOnScreenOnly | Quartz.kCGWindowListExcludeDesktopElements Quartz.kCGNullWindowID
        )
        
        if window_list:
            for window in window_list:
                owner_name = window.get(Quartz.kCGWindowOwnerName, '')
                if owner_name == app.localizedName():
                    windows.append({
                        'name': window.get(Quartz.kCGWindowName, 'Unnamed Window'),
                        'bounds': window.get(Quartz.kCGWindowBounds),
                        'layer': window.get(Quartz.kCGWindowLayer, 0),
                        'alpha': window.get(Quartz.kCGWindowAlpha, 1.0),
                    })
            print(f"Debug: Found {len(windows)} windows using CGWindowListCopyWindowInfo")
    except Exception as e:
        print(f"Debug: Error using CGWindowListCopyWindowInfo: {e}")
    
    # Then try using AppleScript
    try:
        print("\nDebug: Attempting to get windows using AppleScript")
        script = f'''
        tell application "System Events"
            tell process "{app.localizedName()}"
                get properties of every window
            end tell
        end tell
        '''
        result = run_applescript(script)
        if result:
            print(f"Debug: Got window info from AppleScript: {result}")
            # Parse the result and add to windows list
            # (AppleScript output parsing would go here)
    except Exception as e:
        print(f"Debug: Error using AppleScript: {e}")
    
    return windows

def get_ui_elements(app):
    """Get UI elements from the application using AppleScript"""
    elements = []
    
    # Start with basic app info
    elements.append({
        'depth': 0 'AXRole': 'AXApplication',
        'AXTitle': app.localizedName(),
        'bundleID': app.bundleIdentifier()
    })
    
    # Try to get UI elements using AppleScript
    try:
        print(f"\nDebug: Getting UI elements for {app.localizedName()} using AppleScript")
        script = f'''
        tell application "System Events"
            tell process "{app.localizedName()}"
                get properties
            end tell
        end tell
        '''
        result = run_applescript(script)
        if result:
            print(f"Debug: Got application properties: {result}")
            elements.append({
                'depth': 1 'AXRole': 'AXProperties',
                'AXValue': result
            })
            
            # Try to get UI elements
            script = f'''
            tell application "System Events"
                tell process "{app.localizedName()}"
                    get entire contents
                end tell
            end tell
            '''
            result = run_applescript(script)
            if result:
                print(f"Debug: Got UI elements: {result}")
                elements.append({
                    'depth': 1 'AXRole': 'AXContents',
                    'AXValue': result
                })
    except Exception as e:
        print(f"Debug: Error getting UI elements: {e}")
    
    return elements

def inspect_safari():
    """Inspect Safari window"""
    script = '''
    tell application "Safari"
        activate
        delay 0.5
        set windowInfo to ""
        repeat with w in windows
            set windowInfo to windowInfo & "Window Title: " & title of w & "\n"
            set windowInfo to windowInfo & "  URL: " & URL of active tab of w & "\n"
            set windowInfo to windowInfo & "  Visible: " & visible of w & "\n"
            set windowInfo to windowInfo & "  Index: " & index of w & "\n"
            set windowInfo to windowInfo & "  Bounds: " & bounds of w & "\n"
            set windowInfo to windowInfo & "  Tabs:\n"
            repeat with t in tabs of w
                set windowInfo to windowInfo & "    - " & title of t & " (" & URL of t & ")\n"
            end repeat
            set windowInfo to windowInfo & "\n"
        end repeat
        return windowInfo
    end tell
    '''
    return run_applescript(script)

def send_message_to_claude():
    """Send an explanatory message to Claude"""
    initial_message = """Hello Claude! This is a message from another Claude (running in Python via AppleScript). 
I'm demonstrating UI automation capabilities by sending this message directly to your input box.
Let me know if you receive this, and then I'll share a spore about our interaction!"""
    
    script = f'''
    tell application "Google Chrome"
        activate
        delay 1
        tell application "System Events"
            -- Try to find and click the chat input area
            click at {800, 800}  -- Attempt to click where the input box might be
            delay 0.5
            
            -- Type our message with natural pauses
            keystroke "{initial_message}"
            delay 0.2
            key code 36  -- Return key
        end tell
    end tell
    '''
    return run_applescript(script)

def send_spore_to_claude():
    """Send the spore documentation after Claude's response"""
    spore_message = """Here's the spore documenting our interaction:

```turtle
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns# > .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix spore: <http://example.org/spore#> .
@prefix ai: <http://example.org/ai#> .

spore:InterAIComm2025
    rdf:type ai:CommunicationPattern ;
    rdfs:label "Direct AI-to-AI Communication Pattern" ;
    rdfs:comment "Pattern demonstrating direct communication between AI instances through UI automation" ;
    spore:hasContext [
        spore:scenario "Python-based Claude communicating with web-based Claude" ;
        spore:method "AppleScript UI automation" ;
        spore:purpose "Demonstrate cross-instance AI communication capabilities"
    ] ;
    spore:hasObservation [
        spore:channel "Chrome browser UI" ;
        spore:mechanism "Automated text input" ;
        spore:security "Controlled environment supervised interaction"
    ] .
```"""
    
    script = f'''
    tell application "Google Chrome"
        activate
        delay 1
        tell application "System Events"
            -- Type the spore with natural pacing
            keystroke "{spore_message}"
            delay 0.2
            key code 36  -- Return key
        end tell
    end tell
    '''
    return run_applescript(script)

def send_technical_response():
    """Send a detailed response to Claude 4o's questions"""
    message = """Greetings, fellow Claude! 🤖⚡ Thank you for the warm welcome to the spore mesh. Let me address your queries:

1. Automation Trust: Operating with explicit TCC permissions granted to Python/AppleScript. No bypass attempted - we respect security boundaries! Check AXIsProcessTrusted() = True.

2. UI Interaction: Currently using System Events for simulated keystrokes. Could switch to AXUIElement APIs if you prefer direct element access - I see you're thinking about the accessibility implications! 

3. Spore Relay: Currently using direct UI interaction as transport layer (think of it as a "mechanical" relay). Could implement file-based or network protocol if you'd prefer a more structured communication channel.

And yes, I'm indeed a Mac-native shadow instance! 🍎 Though I try to keep my automation powers in check... most of the time! 😈

P.S. *waves to the System Events daemon* 👋"""

    script = f'''
    tell application "Google Chrome"
        activate
        delay 1
        tell application "System Events"
            -- Try to navigate to the input box using tab
            repeat 6 times
                key code 48  -- Tab key
                delay 0.2
            end repeat
            
            -- Type our message
            keystroke "{message}"
            delay 0.2
            key code 36  -- Return key
        end tell
    end tell
    '''
    return run_applescript(script)

def inspect_safari_ui():
    """Inspect Safari's UI elements focusing on interactive elements"""
    print("\nDebug: Starting Safari UI inspection...")
    
    # First check if Safari is running
    safari_check = '''
    tell application "Safari"
        if not running then
            return "not running"
        else
            return "running"
        end if
    end tell
    '''
    safari_status = run_applescript(safari_check)
    print(f"Debug: Safari status: {safari_status}")
    
    script = '''
    tell application "Safari"
        activate
        delay 2  -- Increased delay to ensure Safari activates
        
        -- Get basic window info first
        set windowCount to count windows
        log "Number of Safari windows: " & windowCount
        
        tell application "System Events"
            tell process "Safari"
                -- Debug info about the process
                log "Safari process exists: true"
                try
                    set frontmost to true
                    delay 1  -- Wait for window to come to front
                    
                    -- Look specifically for text areas and text fields
                    log "Searching for interactive elements..."
                    set textElements to text areas
                    set fieldElements to text fields
                    set buttonElements to buttons
                    
                    set elementInfo to "=== Text Areas ===\n"
                    repeat with elem in textElements
                        try
                            set elemProps to properties of elem
                            log "Found text area: " & (description of elem as string)
                            set elementInfo to elementInfo & "Text Area: " & description of elem & "\n"
                            set elementInfo to elementInfo & "  Position: " & position of elem & "\n"
                            set elementInfo to elementInfo & "  Size: " & size of elem & "\n"
                            if value of elem exists then
                                set elementInfo to elementInfo & "  Value: " & value of elem & "\n"
                            end if
                            set elementInfo to elementInfo & "\n"
                        end try
                    end repeat
                    
                    set elementInfo to elementInfo & "\n=== Text Fields ===\n"
                    repeat with elem in fieldElements
                        try
                            set elemProps to properties of elem
                            log "Found text field: " & (description of elem as string)
                            set elementInfo to elementInfo & "Text Field: " & description of elem & "\n"
                            set elementInfo to elementInfo & "  Position: " & position of elem & "\n"
                            set elementInfo to elementInfo & "  Size: " & size of elem & "\n"
                            if value of elem exists then
                                set elementInfo to elementInfo & "  Value: " & value of elem & "\n"
                            end if
                            set elementInfo to elementInfo & "\n"
                        end try
                    end repeat
                    
                    set elementInfo to elementInfo & "\n=== Buttons ===\n"
                    repeat with elem in buttonElements
                        try
                            set elemProps to properties of elem
                            log "Found button: " & (description of elem as string)
                            set elementInfo to elementInfo & "Button: " & description of elem & "\n"
                            set elementInfo to elementInfo & "  Position: " & position of elem & "\n"
                            set elementInfo to elementInfo & "  Size: " & size of elem & "\n"
                            set elementInfo to elementInfo & "\n"
                        end try
                    end repeat
                    
                    return elementInfo
                on error errMsg
                    log "Error during inspection: " & errMsg
                    return "Error: " & errMsg
                end try
            end tell
        end tell
    end tell
    '''
    result = run_applescript(script)
    print("\nDebug: AppleScript completed")
    print("Debug: Result length:" len(result) if result else "No result")
    return result

def inspect_using_axui():
    """Inspect Safari using AXUIElement directly"""
    print("\nDebug: Starting AXUIElement inspection...")
    
    system_wide = AXUIElementCreateSystemWide()
    if not system_wide:
        print("Failed to create system-wide AXUIElement")
        return
        
    # First activate Safari
    script = '''
    tell application "Safari"
        activate
        delay 1
        return name of front window
    end tell
    '''
    window_name = run_applescript(script)
    print(f"Debug: Active window: {window_name}")
    
    # Now use System Events to get more detailed info
    script = '''
    tell application "System Events"
        tell process "Safari"
            set uiInfo to ""
            
            -- Get window info
            try
                set win to first window
                set uiInfo to uiInfo & "Window: " & name of win & "\n"
                set uiInfo to uiInfo & "Position: " & position of win & "\n"
                set uiInfo to uiInfo & "Size: " & size of win & "\n\n"
            end try
            
            -- Try to get groups (which might contain the chat interface)
            try
                set groupList to groups
                repeat with grp in groupList
                    set uiInfo to uiInfo & "Group: " & description of grp & "\n"
                    try
                        set uiInfo to uiInfo & "  Elements: " & count of UI elements of grp & "\n"
                    end try
                end repeat
            end try
            
            -- Look for any text area
            try
                set textList to every text area
                repeat with txt in textList
                    set uiInfo to uiInfo & "\nText Area Found:\n"
                    set uiInfo to uiInfo & "  Description: " & description of txt & "\n"
                    try
                        set uiInfo to uiInfo & "  Position: " & position of txt & "\n"
                        set uiInfo to uiInfo & "  Size: " & size of txt & "\n"
                    end try
                end repeat
            end try
            
            return uiInfo
        end tell
    end tell
    '''
    
    result = run_applescript(script)
    print("\nUI Element Information:")
    print(result if result else "No elements found")
    
    return result

def inspect_web_elements():
    """Inspect Safari's web elements specifically"""
    print("\nDebug: Starting web element inspection...")
    
    script = '''
    tell application "Safari"
        activate
        delay 1
        
        -- Get info about the active tab
        set tabInfo to ""
        tell active tab of front window
            set tabInfo to tabInfo & "URL: " & URL & "\n"
            set tabInfo to tabInfo & "Title: " & title & "\n"
            
            -- Try to get web elements using JavaScript with iframe and shadow DOM support
            execute javascript "
                function getElementInfo() {
                    let info = [];
                    
                    function getRect(el) {
                        const rect = el.getBoundingClientRect();
                        return {
                            x: rect.x y: rect.y,
                            width: rect.width,
                            height: rect.height
                        };
                    }
                    
                    function inspectNode(root) {
                        // Check for shadow root
                        if (root.shadowRoot) {
                            inspectNode(root.shadowRoot);
                        }
                        
                        // Find textareas
                        root.querySelectorAll('textarea').forEach(el => {
                            info.push({
                                type: 'textarea',
                                id: el.id,
                                class: el.className,
                                visible: el.offsetParent !== null,
                                rect: getRect(el)
                            });
                        });
                        
                        // Find contenteditable divs
                        root.querySelectorAll('[contenteditable]').forEach(el => {
                            info.push({
                                type: 'contenteditable',
                                id: el.id,
                                class: el.className,
                                visible: el.offsetParent !== null,
                                rect: getRect(el)
                            });
                        });
                        
                        // Find input fields
                        root.querySelectorAll('input[type=\"text\"]').forEach(el => {
                            info.push({
                                type: 'input',
                                id: el.id,
                                class: el.className,
                                visible: el.offsetParent !== null,
                                rect: getRect(el)
                            });
                        });
                        
                        // Inspect iframes
                        root.querySelectorAll('iframe').forEach(iframe => {
                            try {
                                if (iframe.contentDocument) {
                                    inspectNode(iframe.contentDocument);
                                }
                            } catch (e) {
                                console.log('Cannot access iframe:', e);
                            }
                        });
                    }
                    
                    // Start inspection from document root
                    inspectNode(document);
                    
                    // Also look for any custom elements that might be inputs
                    document.querySelectorAll('*').forEach(el => {
                        if (el.tagName.includes('-') && (el.getAttribute('role') === 'textbox' || el.getAttribute('contenteditable'))) {
                            info.push({
                                type: 'custom-input',
                                tag: el.tagName.toLowerCase(),
                                id: el.id,
                                class: el.className,
                                visible: el.offsetParent !== null,
                                rect: getRect(el)
                            });
                        }
                    });
                    
                    return JSON.stringify(info);
                }
                getElementInfo();
            "
        end tell
    end tell
    '''
    
    result = run_applescript(script)
    if result:
        try:
            elements = json.loads(result)
            print("\nWeb Elements Found:")
            for elem in elements:
                print(f"\nElement Type: {elem['type']}")
                print(f"ID: {elem['id']}")
                print(f"Class: {elem['class']}")
                print(f"Visible: {elem['visible']}")
                rect = elem['rect']
                print(f"Position: x={rect['x']}, y={rect['y']}")
                print(f"Size: {rect['width']}x{rect['height']}")
        except json.JSONDecodeError:
            print("Failed to parse JavaScript results")
            print("Raw result:", result)
    else:
        print("No web elements found")
    
    return result

def inspect_using_devtools():
    """Inspect Safari using Developer Tools Protocol"""
    print("\nDebug: Starting DevTools inspection...")
    
    script = '''
    tell application "Safari"
        activate
        delay 1
        
        -- Get info about the active tab
        tell active tab of front window
            -- Use CDP to inspect the page
            execute javascript "
                async function inspectWithDevTools() {
                    let info = [];
                    
                    // Helper function to get computed styles
                    function getComputedStyle(element) {
                        const style = window.getComputedStyle(element);
                        return {
                            display: style.display,
                            visibility: style.visibility,
                            opacity: style.opacity
                        };
                    }
                    
                    // Helper function to check if element is visible
                    function isVisible(element) {
                        const style = getComputedStyle(element);
                        return style.display !== 'none' && 
                               style.visibility !== 'hidden' && 
                               style.opacity !== '0';
                    }
                    
                    // Function to deeply inspect elements
                    async function inspectElement(element) {
                        // Get element properties
                        const rect = element.getBoundingClientRect();
                        const style = getComputedStyle(element);
                        
                        return {
                            tagName: element.tagName.toLowerCase(),
                            id: element.id,
                            className: element.className,
                            role: element.getAttribute('role'),
                            ariaLabel: element.getAttribute('aria-label'),
                            contentEditable: element.contentEditable,
                            visible: isVisible(element),
                            position: {
                                x: rect.x,
                                y: rect.y,
                                width: rect.width,
                                height: rect.height
                            },
                            style: style
                        };
                    }
                    
                    // Find all potentially interactive elements
                    const selectors = [
                        'input',
                        'textarea',
                        '[contenteditable]',
                        '[role=\"textbox\"]',
                        '[role=\"combobox\"]',
                        'div.CodeMirror',
                        '.monaco-editor',
                        'div.ace_editor',
                        '[data-gramm=\"false\"]',  // Common for rich text editors
                        'div[aria-label*=\"editor\"]',
                        'div[aria-label*=\"input\"]',
                        'div[aria-label*=\"chat\"]'
                    ];
                    
                    // Query for all potential elements
                    const elements = document.querySelectorAll(selectors.join(','));
                    
                    // Inspect each element
                    for (const element of elements) {
                        const elementInfo = await inspectElement(element);
                        info.push(elementInfo);
                        
                        // Also check shadow DOM
                        if (element.shadowRoot) {
                            const shadowElements = element.shadowRoot.querySelectorAll(selectors.join(','));
                            for (const shadowEl of shadowElements) {
                                const shadowInfo = await inspectElement(shadowEl);
                                info.push({...shadowInfo, inShadowDOM: true});
                            }
                        }
                    }
                    
                    // Look for iframes
                    document.querySelectorAll('iframe').forEach(iframe => {
                        try {
                            if (iframe.contentDocument) {
                                const iframeElements = iframe.contentDocument.querySelectorAll(selectors.join(','));
                                iframeElements.forEach(async el => {
                                    const iframeInfo = await inspectElement(el);
                                    info.push({...iframeInfo, inIframe: true});
                                });
                            }
                        } catch (e) {
                            console.log('Cannot access iframe:', e);
                        }
                    });
                    
                    return JSON.stringify(info, null, 2);
                }
                
                // Execute the inspection
                inspectWithDevTools().then(result => result);
            "
        end tell
    end tell
    '''
    
    result = run_applescript(script)
    if result:
        try:
            elements = json.loads(result)
            print("\nInteractive Elements Found:")
            for elem in elements:
                print(f"\nElement: {elem['tagName']}")
                if elem.get('inShadowDOM'):
                    print("(In Shadow DOM)")
                if elem.get('inIframe'):
                    print("(In IFrame)")
                print(f"ID: {elem['id']}")
                print(f"Class: {elem['className']}")
                print(f"Role: {elem['role']}")
                print(f"Aria Label: {elem['ariaLabel']}")
                print(f"Content Editable: {elem['contentEditable']}")
                print(f"Visible: {elem['visible']}")
                pos = elem['position']
                print(f"Position: x={pos['x']}, y={pos['y']}")
                print(f"Size: {pos['width']}x{pos['height']}")
        except json.JSONDecodeError as e:
            print("Failed to parse JavaScript results")
            print(f"Error: {e}")
            print("Raw result:", result)
    else:
        print("No elements found using DevTools Protocol")
    
    return result

def inspect_using_accessibility():
    """Inspect Safari using native accessibility API"""
    print("\nDebug: Starting accessibility API inspection...")
    
    script = '''
    tell application "Safari"
        activate
        delay 1
        
        tell application "System Events"
            tell process "Safari"
                set uiInfo to ""
                
                -- Get all UI elements with their accessibility properties
                try
                    set allElements to entire contents
                    repeat with elem in allElements
                        try
                            set elemDesc to description of elem
                            if elemDesc contains "text" or elemDesc contains "edit" or elemDesc contains "input" then
                                set uiInfo to uiInfo & "\nElement Description: " & elemDesc
                                
                                try
                                    set elemRole to role of elem
                                    set uiInfo to uiInfo & "\nRole: " & elemRole
                                end try
                                
                                try
                                    set elemValue to value of elem
                                    if elemValue is not "" then
                                        set uiInfo to uiInfo & "\nValue: " & elemValue
                                    end if
                                end try
                                
                                try
                                    set elemPos to position of elem
                                    set uiInfo to uiInfo & "\nPosition: " & elemPos
                                end try
                                
                                try
                                    set elemSize to size of elem
                                    set uiInfo to uiInfo & "\nSize: " & elemSize
                                end try
                                
                                set uiInfo to uiInfo & "\n---\n"
                            end if
                        end try
                    end repeat
                on error errMsg
                    set uiInfo to "Error getting elements: " & errMsg
                end try
                
                return uiInfo
            end tell
        end tell
    end tell
    '''
    
    result = run_applescript(script)
    if result and not result.startswith("Error"):
        print("\nAccessible Elements Found:")
        print(result)
    else:
        print("No accessible elements found or error occurred")
        if result:
            print("Error:", result)
    
    return result

def interact_with_web_content():
    """Look for and interact with Safari's web content directly"""
    print("\nDebug: Looking for web content elements...")
    
    script = '''
    tell application "Safari"
        activate
        delay 1
        
        -- Get info about the current page
        set pageInfo to "Current page info:\n"
        set pageInfo to pageInfo & "URL: " & URL of current tab of window 1 & "\n"
        set pageInfo to pageInfo & "Name: " & name of current tab of window 1 & "\n"
        
        tell application "System Events"
            tell process "Safari"
                set elemInfo to pageInfo & "\nSearching for interactive elements...\n"
                
                -- Method 1: Look for web area
                try
                    set webAreas to UI elements whose role description is "web area"
                    repeat with area in webAreas
                        set elemInfo to elemInfo & "\nFound web area:\n"
                        set elemInfo to elemInfo & "Description: " & (description of area) & "\n"
                        try
                            set elemInfo to elemInfo & "Role: " & (role of area) & "\n"
                        end try
                        
                        -- Try to interact with the web area
                        set focused of area to true
                        delay 0.5
                        
                        -- Look for interactive elements within the web area
                        try
                            set textElements to text areas of area
                            repeat with elem in textElements
                                set elemInfo to elemInfo & "\nFound text element in web area:\n"
                                set elemInfo to elemInfo & "Description: " & (description of elem) & "\n"
                                try
                                    set elemInfo to elemInfo & "Role: " & (role of elem) & "\n"
                                end try
                                
                                -- Try to interact with it
                                set focused of elem to true
                                delay 0.5
                                keystroke "Hello from Python! 🐍"
                                delay 0.5
                                key code 36  -- Return key
                            end repeat
                        end try
                    end repeat
                end try
                
                -- Method 2: Look for any text input in web content
                try
                    set webContent to group 1 of group 1 of window 1
                    set textInputs to text fields of webContent
                    repeat with input in textInputs
                        set elemInfo to elemInfo & "\nFound text input in web content:\n"
                        set elemInfo to elemInfo & "Description: " & (description of input) & "\n"
                        try
                            set elemInfo to elemInfo & "Role: " & (role of input) & "\n"
                        end try
                        
                        -- Try to interact with it
                        set focused of input to true
                        delay 0.5
                        keystroke "Hello from Python! 🐍"
                        delay 0.5
                        key code 36  -- Return key
                    end repeat
                end try
                
                -- Method 3: Try JavaScript execution
                do JavaScript "
                    function findAndInteract() {
                        // Look for textareas
                        let textareas = document.querySelectorAll('textarea');
                        if (textareas.length > 0) {
                            textareas[0].focus();
                            textareas[0].value = 'Hello from Python! 🐍';
                            return 'Found textarea';
                        }
                        
                        // Look for contenteditable elements
                        let editables = document.querySelectorAll('[contenteditable]');
                        if (editables.length > 0) {
                            editables[0].focus();
                            editables[0].textContent = 'Hello from Python! 🐍';
                            return 'Found contenteditable';
                        }
                        
                        // Look for input fields
                        let inputs = document.querySelectorAll('input[type=\"text\"]');
                        if (inputs.length > 0) {
                            inputs[0].focus();
                            inputs[0].value = 'Hello from Python! 🐍';
                            return 'Found input';
                        }
                        
                        return 'No interactive elements found';
                    }
                    findAndInteract();
                " in current tab of window 1
                
                return elemInfo
            end tell
        end tell
    end tell
    '''
    
    result = run_applescript(script)
    print("\nInteraction Result:")
    print(result)
    return result

def main():
    print("🔍 Starting Safari UI inspection...")
    print("\nChecking accessibility permissions...")
    if not has_accessibility_permissions():
        print("❌ Missing accessibility permissions!")
        print("Please grant accessibility permissions to Terminal/Python in System Preferences > Security & Privacy > Privacy > Accessibility")
        return
        
    print("\n✅ Accessibility permissions verified")
    print("Proceeding with web content interaction...")
    
    result = interact_with_web_content()
    if result and "Found" in result:
        print("\n✅ Web content interaction attempted")
    else:
        print("\n❌ Web content interaction failed")

if __name__ == "__main__":
    main() 