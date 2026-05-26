.. _history_page:

Calculation History
===================

.. figure:: ../../../images/screenshots/history_page.png
    :width: 80%
    :alt: AiiDAlab ChemShell Process History Page


This page allows users to search through previously submitted processes and displays
key information such as AiiDA database references and the calculation results. The
first half of the display contains a database search UI component which enables more
tailored search queries, useful if the database is significantly large. By default
it will simply search for all items in the database with the process key (i.e. all
previously submitted workflow/calculation processes) which will include any processes submitted
by the user not just those submitted through the AiiDAlab ChemShell interface. 

Once a process has been selected it becomes visible in the tree view in the second half
of the display. This visualiser mirrors that of the results view when the workflow was
originally submitted via the main ChemShell UI. The main process displays its state and
can be expanded to show a list of associated results objects for the job. Each of these
objects can then be selected and will be shown in the visualiser at the bottom of the page. 
This will either show a dedicated visualiser for the results object or if one is not 
available it will show the AiiDA database reference for the object. Example for different
supported visualisers are discussed in :ref:`node_viewers`\. 
