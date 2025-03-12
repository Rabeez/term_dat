# Term DAT

*Terminal Data Analysis Tool*

## Usage

```
Usage: term_dat [OPTIONS]

Start the TUI application with optional script execution and plot mode.

Options:
-s, --script PATH  Path to script file for execution
-p, --plot TEXT    Plot mode: 'ascii' (default) or 'window'
--help             Show this message and exit.
```

## Features

- Load CSV files
- Explore table columns in UI
- Execute basic data analysis functions on tables
- Store history as scripts
- Load saved scripts on startup
- Visually explore pipeline of analysis steps
- Export pipeline of analysis as graph visualization
- Render plots as ASCII in the TUI, or as OS window
- Export plot as image

## Learning outcomes

- CLI development in python
- TUI development in python
- ASCII plots
- Robust filesystem logic (treat this app as a standalone install-able)
- Building single executable
