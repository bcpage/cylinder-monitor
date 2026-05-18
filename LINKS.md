# Quick Links — Personal Reference

## GitHub
- [Repository](https://github.com/bcpage/cylinder-monitor)
- [Actions / CI](https://github.com/bcpage/cylinder-monitor/actions)

## Live App
- [cylinder-monitor PWA](https://bcpage.github.io/cylinder-monitor/)

## Codespace
- [VS Code (github.dev)](https://bug-free-space-disco-95jpxwvvgjvcr56.github.dev/)
- [JupyterLab — analysis notebook](https://bug-free-space-disco-95jpxwvvgjvcr56-8888.app.github.dev/lab/tree/analysis/cylinder_analysis.ipynb)

> Codespace URLs are instance-specific — update if GitHub assigns a new Codespace.

## Back to Working — Startup Checklist

After any VS Code reload or Codespace restart:

1. Open Codespace in browser — VS Code loads
2. Terminal 1: `claude` — starts Claude Code
3. Terminal 2: `jupyter lab --no-browser --port=8888`
4. Click the port 8888 popup — JupyterLab opens in a browser tab
5. In JupyterLab: open `analysis/cylinder_analysis.ipynb`
6. Kernel → Restart Kernel and Run All Cells

**What survives a reload:** everything — files, installed packages, Codespace state.
**What survives a full restart:** same — packages live in `~/.local`, not wiped on restart.
**What requires a rebuild:** only if you manually trigger devcontainer rebuild — rare.
