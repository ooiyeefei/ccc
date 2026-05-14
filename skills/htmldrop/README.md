# htmldrop - Share HTML as Hosted Links

Share any HTML file and get a hosted URL instantly. Powered by Surge.sh.

---

## Installation

```bash
# Add the ccc marketplace (if not already added)
/plugin marketplace add ooiyeefei/ccc

# Install the skills collection
/plugin install ccc-skills@ccc
```

## Prerequisites

```bash
# Install the htmldrop CLI
npm install -g htmldrop

# Initialize (creates Surge account + picks your subdomain)
htmldrop init
```

Requires Node.js >= 18.

## Quick Start

After installing, just ask Claude Code:

```
"Share this HTML file"
"Publish report.html"
"Get me a link for this"
"Make this shareable"
```

Or use the command directly:

```
/share report.html
```

Claude Code will push the file and return a shareable URL.

## Features

- **Instant sharing**: One command to publish any HTML file
- **Zero cost**: Hosted on Surge.sh for free
- **Password protection**: Optionally restrict access with a password
- **Works with generated HTML**: Claude Code can create an HTML report/spec and share it in one step
- **List published files**: See all your shared files and their URLs

## Password Protection

To share a file with restricted access:

```
"Share spec.html but password-protect it"
```

Claude Code will ask for a password (or generate one), push the file, and give you both the URL and the password to share with recipients.

## How It Works

1. `htmldrop` wraps Surge.sh for static file hosting
2. Authentication is stored in `~/.netrc` (managed by Surge)
3. Configuration lives in `~/.htmldrop/config.json`
4. Files are published to your chosen subdomain on surge.sh

## License

MIT
