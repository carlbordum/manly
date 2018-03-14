# manly
manly is a compliment to man pages.
It's a lot like [explainshell](https://explainshell.com) (don't worry, that is explain-shell, not explains-hell).

Use manly, when you want to know how flags modify a commands' behaviour.

Let's say your good friend has a funky alias in [his dotfiles](https://github.com/8Banana/dotfiles/blob/master/__Myst__/.zshrc): `alias alert="notify-send -i terminal -t 5 'Alert from Terminal!'"`.
manly to the rescue:

``` bash
$ manly notify-send -it

notify-send - a program to send desktop notifications
=====================================================

      -t, --expire-time=TIME
              The duration, in milliseconds, for the notification to  appear  on  screen.
              (Ubuntu's Notify OSD and GNOME Shell both ignore this parameter.)

      -i, --icon=ICON[,ICON...]
              Specifies an icon filename or stock icon to display.

```

Short and sweet!


## Installation
manly requires Python 3.

    $ pip install manly

and you can always remove it with

    $ pip uninstall manly


## Develop with me :)

```bash
$ git clone https://github.com/Zaab1t/manly
$ cd manly
$ python manly.py
```
