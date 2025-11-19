---
role: user-documentation
summary: |
  User-facing help for websh. Quick start, full command cheatsheet, examples.
---

# websh Help

A Unix-like shell for the web. Navigate URLs like directories, query pages with familiar commands.

## Quick Start

```
websh                                # start the shell
ls                                   # shows suggested sites
go hn                                # go to Hacker News (preset bookmark)
ls | head 5                          # first 5 links
grep "AI"                            # search for text
follow 1                             # click the 2nd link
cat .title                           # extract text by selector
back                                 # go back
```

## Starter Bookmarks

websh comes with bookmarks for interesting public sites:

| Shortcut | Site |
|----------|------|
| `go hn` | Hacker News |
| `go lobsters` | Lobsters |
| `go tildes` | Tildes |
| `go wiby` | Wiby (indie search) |
| `go marginalia` | Marginalia (indie search) |
| `go wiki` | Wikipedia |
| `go sourcehut` | Sourcehut |
| `go arena` | Are.na |

Add your own with `bookmark <name>`.

---

## Command Cheatsheet

### Navigation

| Command | Description |
|---------|-------------|
| `cd <url>` | Go to URL |
| `cd -` | Go to previous URL |
| `cd ~` | Go to start (clear navigation) |
| `pwd` | Show current URL |
| `back` / `forward` | Navigate history |
| `follow <n>` | Follow nth link |
| `follow "text"` | Follow link containing text |
| `refresh` | Re-fetch current page |
| `chroot <url>` | Restrict navigation to URL prefix |

### Query & Extract

| Command | Description |
|---------|-------------|
| `ls` | List all links |
| `ls -l` | List with URLs |
| `ls <selector>` | List elements matching selector |
| `cat <selector>` | Extract text content |
| `grep <pattern>` | Search/filter by pattern |
| `grep -i` | Case-insensitive |
| `grep -v` | Invert match |
| `stat` | Show page metadata |
| `source` | View raw HTML |
| `dom` | Show DOM tree |

### Prefetching

| Command | Description |
|---------|-------------|
| `prefetch` | Show crawl status |
| `prefetch on/off` | Enable/disable eager crawl |
| `prefetch <url>` | Manually prefetch a URL |
| `prefetch --depth <n>` | Set prefetch depth |
| `crawl <url>` | Explicit deep crawl |
| `queue` | Show crawl queue |

### Search & Discovery

| Command | Description |
|---------|-------------|
| `find <pattern>` | Recursive search/crawl |
| `find -depth <n>` | Crawl n levels deep |
| `locate <term>` | Search all cached pages |
| `tree` | Show site structure |
| `which <link>` | Resolve redirects |

### Text Processing

| Command | Description |
|---------|-------------|
| `head <n>` | First n items |
| `tail <n>` | Last n items |
| `sort` | Sort output |
| `sort -r` | Reverse sort |
| `uniq` | Remove duplicates |
| `wc` | Count lines/words |
| `wc --links` | Count links |
| `cut -f <n>` | Extract field |
| `tr` | Transform characters |
| `sed 's/a/b/'` | Stream edit |

### Comparison

| Command | Description |
|---------|-------------|
| `diff <url1> <url2>` | Compare two pages |
| `diff -t 1h` | Compare to 1 hour ago |
| `diff --wayback <date>` | Compare to Wayback snapshot |

### Monitoring

| Command | Description |
|---------|-------------|
| `watch <url>` | Monitor for changes |
| `watch -n 30` | Poll every 30 seconds |
| `watch --notify` | System notification on change |
| `ping <url>` | Check if site is up |
| `traceroute <url>` | Show redirect chain |
| `time <cmd>` | Measure execution time |

### Jobs & Background

| Command | Description |
|---------|-------------|
| `<cmd> &` | Run in background |
| `ps` | Show running tasks |
| `jobs` | List background jobs |
| `fg %<n>` | Bring job to foreground |
| `bg %<n>` | Continue in background |
| `kill %<n>` | Cancel job |
| `wait` | Wait for all jobs |

### Environment & Auth

| Command | Description |
|---------|-------------|
| `env` | Show environment |
| `export VAR=val` | Set variable |
| `export HEADER_X=val` | Set request header |
| `export COOKIE_x=val` | Set cookie |
| `unset VAR` | Remove variable |
| `whoami` | Show logged-in identity |
| `login` | Interactive login |
| `logout` | Clear session |
| `su <profile>` | Switch profile |

### Mounting

| Command | Description |
|---------|-------------|
| `mount <api> <path>` | Mount API as directory |
| `mount -t github ...` | Mount GitHub API |
| `mount -t rss ...` | Mount RSS feed |
| `umount <path>` | Unmount |
| `df` | Show mounts and cache usage |
| `quota` | Show rate limits |

### Archives & Snapshots

| Command | Description |
|---------|-------------|
| `tar -c <file> <urls>` | Archive pages |
| `tar -x <file>` | Extract archive |
| `snapshot` | Save timestamped version |
| `snapshot -l` | List snapshots |
| `wayback <url>` | List Wayback snapshots |
| `wayback <url> <date>` | Fetch from Wayback |

### Site Metadata

| Command | Description |
|---------|-------------|
| `robots` | Show robots.txt |
| `sitemap` | Show sitemap.xml |
| `headers` | Show HTTP headers |
| `cookies` | Manage cookies |

### Interaction

| Command | Description |
|---------|-------------|
| `click <selector>` | Click element |
| `submit <form>` | Submit form |
| `type <sel> "text"` | Fill input |
| `scroll` | Trigger infinite scroll |
| `screenshot <file>` | Capture page |

### Scheduling

| Command | Description |
|---------|-------------|
| `cron "<sched>" <cmd>` | Schedule recurring |
| `at "<time>" <cmd>` | Schedule one-time |
| `cron -l` | List scheduled |

### Aliases & Shortcuts

| Command | Description |
|---------|-------------|
| `alias name='cmd'` | Create alias |
| `alias` | List aliases |
| `unalias name` | Remove alias |
| `ln -s <url> <name>` | Create URL shortcut |

### State & History

| Command | Description |
|---------|-------------|
| `history` | Show command history |
| `!!` | Repeat last command |
| `!<n>` | Repeat command n |
| `bookmark <name>` | Save current URL |
| `bookmarks` | List bookmarks |
| `go <name>` | Go to bookmark |

### File Operations

| Command | Description |
|---------|-------------|
| `save <path>` | Save page to file |
| `save --parsed` | Save extracted markdown |
| `tee <file>` | Save while displaying |
| `xargs <cmd>` | Build commands from input |
| `parallel` | Run in parallel |

---

## Pipes & Redirection

```
ls | grep "AI" | head 5              # pipe commands
ls > links.txt                       # write to file
ls >> links.txt                      # append to file
ls | tee links.txt                   # save and display
cd $(wayback https://x.com 2020)     # command substitution
```

---

## Selectors

CSS selectors work with `ls`, `cat`, `click`:

```
cat .article          # class
cat #main             # id
cat article           # tag
cat .post .title      # descendant
cat h1:first          # first match
ls nav a              # links in nav
click button.submit   # button with class
```

---

## Examples

### Browse Hacker News

```
cd https://news.ycombinator.com
ls | head 10                         # top 10 stories
grep "Show HN"                       # filter
follow "Show HN"                     # go to first match
cat .comment | head 20               # read comments
back
```

### Research a topic

```
cd https://en.wikipedia.org/wiki/Unix
cat #mw-content-text | head 50       # intro
ls #toc                              # table of contents
follow "History"
bookmark unix-history
```

### Monitor a page

```
watch https://status.example.com -n 30 --notify
# Polls every 30s, notifies on change
```

### Mount GitHub API

```
mount https://api.github.com /gh
cd /gh/users/torvalds
cat bio
cd /gh/repos/torvalds/linux
