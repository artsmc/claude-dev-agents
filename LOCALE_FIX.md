# WSL Locale Warning Fix

## Problem

You're seeing this warning on every bash command:
```
/bin/bash: warning: setlocale: LC_ALL: cannot change locale (en_US.UTF-8)
```

## Root Cause

- Windows WSL passes `en_US.UTF-8` locale to Linux
- This locale is not generated in the Debian/Ubuntu system
- Bash complains during initialization (before any profile scripts run)
- The system IS correctly using `C.UTF-8` (which works fine)

## Why It's Harmless

- All programs are using `C.UTF-8` correctly (verified)
- Python, scripts, and tools work properly
- Only the warning message is annoying - functionality is unaffected

## Solutions

### Option 1: Generate the Locale (Requires Sudo)

```bash
sudo locale-gen en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8
```

### Option 2: Use the Wrapper Script (No Sudo)

We've created `/home/artsmc/.claude/bin/run-quiet` that filters the warning:

```bash
~/.claude/bin/run-quiet python3 script.py
```

### Option 3: Redirect stderr (Quick Fix)

```bash
your-command 2>/dev/null
# OR filter just the locale warning
your-command 2>&1 | grep -v "setlocale: LC_ALL"
```

### Option 4: Update WSL Config (Permanent Fix)

On Windows, create/edit `C:\Users\YourUsername\.wslconfig`:

```ini
[wsl2]
localeGeneration = true
```

Then restart WSL:
```powershell
wsl --shutdown
```

## Current State

- `.bashrc`, `.bash_profile`, and `.profile` are configured to use `C.UTF-8`
- `import_phases.py` script sets locale internally (no warnings in Python output)
- Wrapper scripts are available at `~/.claude/bin/`

## Verification

Check your current locale:
```bash
locale
```

Should show all values set to `C.UTF-8`.
