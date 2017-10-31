################################
pl-gepush
################################


Abstract
********

An app to push data of interest to GE cloud service


Preconditions
*************

This plugin requires input and output directories as a precondition.


Run
***

Using ``docker run``
====================

Assign an "input" directory to ``/incoming`` and an output directory to ``/outgoing``

.. code-block:: bash

    docker run -v /tmp/input:/incoming -v /tmp/output:/outgoing   \
            local/pl-gepush gepush.py --prefix demo-upload --contentType text/plain  \
            /incoming /outgoing


This will push a copy of each file/folder in the container's ``/incoming`` to GE cloud
storage and prefix the copy with the ``prefix`` text (in this case "demo-upload"). Some
metadata files will be written to the container's ``/outgoing`` directory.

Make sure that the host ``/tmp/input`` directory is world readable and ``/tmp/output``
directory is world writable!







