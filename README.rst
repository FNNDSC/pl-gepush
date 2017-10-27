################################
pl-gepush
################################


Abstract
********

An app to push data of interest to GE cloud service

Run
***

Using ``docker run``
====================

Assign an "input" directory to ``/incoming`` and an output directory to ``/outgoing``

.. code-block:: bash

    docker run -v $(pwd)/in:/incoming -v $(pwd)/out:/outgoing   \
            fnndsc/pl-gepush gepush.py            \
            /incoming /outgoing

This will ...

Make sure that the host ``$(pwd)/out`` directory is world writable!







