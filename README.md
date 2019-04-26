# Duden.de search workflow for Alfred #

A workflow for [Alfred 3][alfred].

Search the definitive German dictionary at [Duden.de][duden] with auto-suggest.

![Workflow in action][demo]


## Download and installation ##

Download the Workflow from the [GitHub releases page][releases] and double-click
the `Duden-Search-XXX.alfredworkflow` file to install.


## Usage ##

Default keyword is `duden`. Enter your query after that.

Actioning a result with `RETURN` will open the full results page at duden.de in
your browser. Pressing `⌘` on a result will show the URL in its subtitle.

You can also assign a Hotkey (keyboard shortcut) that will look up the currently
selected text in any application.


## Feedback ##

If you have a feature request, bug report or other query, you can get in touch
using the [GitHub issue tracker][issues] or [the Alfred Forum page][forum].


## Licensing, thanks ##

The code of this workflow is released under the [MIT licence][mit].

This workflow is based on the following libraries (also released under the MIT licence):

- The legendary [Beautiful Soup][bs] by [Leonard Richardson][lenny],
- the extremely awesome [html5lib][h5l] by [James Graham][jgraham] & co. and
- the not entirely useless [Alfred-Workflow][aw] by [me][deanishe].


[alfred]: http://www.alfredapp.com/
[aw]: http://www.deanishe.net/alfred-workflow/index.html
[bs]: http://www.crummy.com/software/BeautifulSoup/
[mit]: http://opensource.org/licenses/MIT
[h5l]: https://github.com/html5lib/html5lib-python
[deanishe]: https://github.com/deanishe/
[duden]: http://www.duden.de/woerterbuch
[releases]: https://github.com/deanishe/alfred-duden/releases/latest
[demo]: https://raw.githubusercontent.com/deanishe/alfred-duden/master/demo.gif "Workflow in action"
[issues]: https://github.com/deanishe/alfred-duden/issues
[forum]: http://www.alfredforum.com/topic/4707-duden-dictionary-search-with-auto-suggest/
[lenny]: http://www.crummy.com/self/
[jgraham]: https://github.com/jgraham
