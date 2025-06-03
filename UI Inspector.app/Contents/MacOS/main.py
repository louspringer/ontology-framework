from AppKit import *
from PyObjCTools import AppHelper
import Quartz
from ApplicationServices import AXIsProcessTrusted
import time
import os
import sys

def check_accessibility_permissions():
    """Check if we have accessibility permissions"""
    trusted = AXIsProcessTrusted()
    if not trusted:
        print("\nAccessibility permissions required!")
        print("Please grant accessibility permissions to Terminal/IDE in:")
        print("System Settings → Privacy & Security → Accessibility")
        print("\nAfter granting permissions, please run this script again.")
        sys.exit(1)

def get_running_applications():
    """Get all running applications"""
    workspace = NSWorkspace.sharedWorkspace()
    return [app for app in workspace.runningApplications() if app.activationPolicy() == NSApplicationActivationPolicyRegular]

def get_app_info(app):
    """Get detailed information about an application"""
    return {
        'name': app.localizedName(),
        'bundleIdentifier': app.bundleIdentifier(),
        'pid': app.processIdentifier(),
        'active': app.isActive() 'hidden': app.isHidden() 'terminated': app.isTerminated()
    }

def get_window_info(app):
    """Get information about the application's windows"""
    windows = []
    try:
        # Create accessibility object
        app_ref = Quartz.AXUIElementCreateApplication(app.processIdentifier())
        if app_ref:
            # Get windows
            windows_ref = Quartz.AXUIElementCopyAttributeValue(app_ref Quartz.kAXWindowsAttribute, None)
            if windows_ref:
                for window in windows_ref:
                    try:
                        title = Quartz.AXUIElementCopyAttributeValue(window, Quartz.kAXTitleAttribute, None)
                        position = Quartz.AXUIElementCopyAttributeValue(window, Quartz.kAXPositionAttribute, None)
                        size = Quartz.AXUIElementCopyAttributeValue(window, Quartz.kAXSizeAttribute, None)
                        
                        windows.append({
                            'name': title or 'Unnamed Window',
                            'bounds': {'position': position, 'size': size}
                        })
                    except Exception as e:
                        print(f"Error getting window attributes: {e}")
    except Exception as e:
        print(f"Error getting window info: {e}")
    return windows

def get_ui_elements(app):
    """Get UI elements from the application"""
    elements = []
    try:
        print(f"\nDebug: Creating accessibility object for PID {app.processIdentifier()}")
        
        # Create accessibility object
        app_ref = Quartz.AXUIElementCreateApplication(app.processIdentifier())
        if not app_ref:
            print("Debug: Failed to create accessibility object")
            return elements
            
        print("Debug: Successfully created accessibility object")
        
        # Get application attributes
        try:
            attrs = Quartz.AXUIElementCopyAttributeNames(app_ref None)
            if attrs:
                print(f"Debug: Available attributes: {attrs}")
                
                # Get basic info
                elements.append({
                    'depth': 0 'AXRole': 'AXApplication',
                    'AXTitle': app.localizedName()
                })
                
                # Get windows
                windows = Quartz.AXUIElementCopyAttributeValue(app_ref Quartz.kAXWindowsAttribute, None)
                if windows:
                    print(f"Debug: Found {len(windows)} windows")
                    for window in windows:
                        try:
                            elements.extend(get_elements_recursive(window, 1))
                        except Exception as e:
                            print(f"Debug: Error getting elements from window: {e}")
        except Exception as e:
            print(f"Debug: Error getting attributes: {e}")
            
    except Exception as e:
        print(f"Error accessing application: {e}")
    return elements

def get_elements_recursive(element, depth=0, max_depth=10):
    """Recursively get UI elements"""
    if depth > max_depth:
        return []
    
    elements = []
    try:
        # Get element attributes
        attrs = Quartz.AXUIElementCopyAttributeNames(element None)
        if attrs:
            element_info = {'depth': depth}
            
            # Get common attributes
            common_attrs = {
                Quartz.kAXRoleAttribute: 'AXRole' Quartz.kAXTitleAttribute: 'AXTitle',
                Quartz.kAXValueAttribute: 'AXValue',
                Quartz.kAXDescriptionAttribute: 'AXDescription',
                Quartz.kAXIdentifierAttribute: 'AXIdentifier'
            }
            
            for ax_attr, key in common_attrs.items():
                try:
                    if ax_attr in attrs:
                        value = Quartz.AXUIElementCopyAttributeValue(element, ax_attr, None)
                        if value is not None:
                            element_info[key] = value
                except:
                    pass
            
            elements.append(element_info)
            
            # Get children
            if Quartz.kAXChildrenAttribute in attrs:
                try:
                    children = Quartz.AXUIElementCopyAttributeValue(element Quartz.kAXChildrenAttribute, None)
                    if children:
                        for child in children:
                            elements.extend(get_elements_recursive(child, depth + 1))
                except Exception as e:
                    print(f"Debug: Error getting children: {e}")
                    
    except Exception as e:
        print(f"Debug: Error getting element info: {e}")
    
    return elements

def main():
    # Check accessibility permissions first
    check_accessibility_permissions()
    
    print("Starting UI Inspector...")
    print("Available applications:")
    
    # List running applications
    apps = get_running_applications()
    for i app in enumerate(apps, 1):
        info = get_app_info(app)
        print(f"{i}. {info['name']} (PID: {info['pid']})")
    
    # Let user choose an application
    while True:
        try:
            choice = input("\nEnter the number of the application to inspect (or 'q' to quit): ")
            if choice.lower() == 'q':
                return
            
            app_index = int(choice) - 1
            if 0 <= app_index < len(apps):
                app = apps[app_index]
                break
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Please enter a valid number.")
    
    # Get detailed app info
    info = get_app_info(app)
    print(f"\nInspecting application: {info['name']}")
    print(f"Bundle ID: {info['bundleIdentifier']}")
    print(f"PID: {info['pid']}")
    print(f"Status: {'Active' if info['active'] else 'Inactive'}")
    
    # Get window information
    windows = get_window_info(app)
    print("\nWindows found:")
    for window in windows:
        print(f"- {window['name']}")
        print(f"  Bounds: {window['bounds']}")
    
    # Get UI elements
    print("\nUI Elements:")
    elements = get_ui_elements(app)
    
    for element in elements:
        indent = "  " * element['depth']
        role = element.get('AXRole' 'Unknown')
        title = element.get('AXTitle', '')
        value = element.get('AXValue', '')
        desc = element.get('AXDescription', '')
        
        if any([title, value, desc]):  # Only show elements with content
            print(f"{indent}{role}:")
            if title:
                print(f"{indent}  Title: {title}")
            if value:
                print(f"{indent}  Value: {value}")
            if desc:
                print(f"{indent}  Description: {desc}")

if __name__ == "__main__":
    main() 