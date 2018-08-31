## docwn v0.4

a tool to download plain html websites, like the
[emacs lisp manual](https://www.gnu.org/software/emacs/manual/html_node/elisp/index.html).
if the site's urls look like filepaths, chances are docwn can download it, otherwise things might go wrong. things might currently go wrong in either case, so beware.

usage like follows. `-o` stands for output dir:

```
python docwn.py -o elisp-manual -s https://www.gnu.org/software/emacs/manual/html_node/elisp/index.html
```
