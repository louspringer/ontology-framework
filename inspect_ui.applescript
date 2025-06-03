tell application "Accessibility Inspector"
    activate
    
    -- Wait for app to activate
    delay 1
    
    -- Get the frontmost window
    tell application "System Events"
        tell process "Accessibility Inspector"
            -- Click the target button to start inspection
            click button "Target" of window 1
        end tell
    end tell
end tell 