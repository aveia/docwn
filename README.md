# docwn

a tool to download plain html websites, like the
[emacs lisp manual](https://www.gnu.org/software/emacs/manual/html_node/elisp/index.html).
if the site's urls look like filepaths, chances are docwn can download it, otherwise things might go wrong. things might currently go wrong in either case, so beware.

usage like follows. `-o` stands for output dir:

```
python docwn.py -o elisp-manual https://www.gnu.org/software/emacs/manual/html_node/elisp/index.html
```

## changelog

### v0.5

- improve cli args
- add changelog to README.md
- write info file after downloading everything
- misc improvements

### v0.4

- several forgotten fixes and improvements

### v0.3.2

- fix several crashes
- improve log messages

### v0.3.1

- fix handling of some index pages
- fix upper case html tag attributes being ignored
- fix handling of absolute urls
- improve handling of relative url paths
- add support for index.htm pages in addition to index.{php,html}

### v0.3

- fix crash when a download fails
- lift limitation on number of downloaded files
- improve handling of download queue

### v0.2

- fix images not being downloaded
- fix index.html being downloaded twice
- improve log messages
- add option to change output dir

### v0.1

- first release
