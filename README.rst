pyinsteon - Python Insteon Package
==================================

|Build status| |GitHub release| |PyPI|

This is a Python package to interface with an Insteon Modem. It has been
tested to work with most USB or RS-232 serial based devices such as the
`2413U <https://www.insteon.com/powerlinc-modem-usb>`__,
`2412S <https://www.insteon.com/powerlinc-modem-serial>`__,
`2448A7 <http://www.insteon.com/usb-wireless-adapter>`__ and Hub models
`2242 <https://www.insteon.com/support-knowledgebase/2014/9/26/insteon-hub-owners-manual>`__
and `2245 <https://www.insteon.com/insteon-hub/>`__. Other models have
not been tested but the underlying protocol has not changed much over
time so it would not be surprising if it worked with a number of other
models. If you find success with something, please let us know.

This **pyinsteon** package was created primarily to support an INSTEON
platform for the `Home Assistant <https://home-assistant.io/>`__
automation platform but it is structured to be general-purpose and
should be usable for other applications as well.

Requirements
------------

-  Python 3.8 3.9, 3.10 or 3.11
-  Posix or Windows based system
-  Some form of Insteon PLM or Hub
-  At least one Insteon device

Installation
------------

You can, of course, just install the most recent release of this package
using ``pip``. This will download the more recent version from
`PyPI <https://pypi.python.org/pypi/pyinsteon>`__ and install it to
your host.

::

    pip install pyinsteon

If you want to grab the the development code, you can also clone this
git repository and install from local sources:

::

    cd pyinsteon
    pip install .

.. |Build status| image:: https://dev.azure.com/pyinsteon/pyinsteon/_apis/build/status/pyinsteon.pyinsteon?branchName=main
   :target: https://dev.azure.com/pyinsteon/pyinsteon/_build/latest?definitionId=1&branchName=main
.. |GitHub release| image:: https://img.shields.io/github/release/pyinsteon/pyinsteon.svg
   :target: https://github.com/pyinsteon/pyinsteon/releases
.. |PyPI| image:: https://img.shields.io/pypi/v/pyinsteon.svg
   :target: https://pypi.python.org/pypi/pyinsteon
