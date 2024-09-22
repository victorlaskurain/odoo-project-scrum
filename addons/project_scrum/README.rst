=============
Project Scrum
=============

.. |badge1| image:: https://img.shields.io/badge/licence-AGPL--3-blue.png
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

|badge1|

Description
===========

Create and manage Scrum Sprints inside Odoo. 100% integrated in Odoo's
standard project management addons.

Data Model
----------

The main data model is the Scrum Sprint which mainly holds a set of
tasks to be completed by a development team in the given time frame.

The Scrum Master can add tasks to a sprint and manage them as he
pleases. He can even mix tasks from different projects. The level of
dedication of each team member defined as the % of her time dedicated
to this sprint can be managed on a daily basis if required although
most of the time setting the dedication for the whole sprint in one go
will be more useful.

Access control
--------------

Only members of the Scrum Master group can create and manage
sprints. Project users can view sprint's information but other than
updating the estimation for the delivery of a task they are not
allowed to touch it.

Usage
=====

Main menu
---------

The main access point is the :menuselection: `Project --> Scrum`.

.. image:: project_scrum/static/description/scrum-sprints.png
   :align: center
   :alt: `Project --> Scrum`.

Sprint details form
-------------------

Click on any of the sprints to display it's details. Look at the
different parts of this form in the following sections.

Header details
~~~~~~~~~~~~~~

.. image:: project_scrum/static/description/scrum-sprint-burndown-tab.png
   :align: center
   :alt: `Sprint Burndown`.

Required fields
***************

A sprint has the following required fields:

- The scrum master. This is the user of conhetact for any generic
  sprint related issues. It is also the only user who should be
  allowed to modify any of the properties of the sprint, including of
  course the backlog.
- The begin and end dates. A sprint is always time bounded. The work
  is expected to begin on the initial date, the finalization date will
  be used for demos etc. and thus when computing the burndown chart no
  work is expected to be accomplished on this final date.

The project is not required!?
*****************************

The project is not required. If set, then all the tasks assigned to
this sprint must belong to this set project. Letting it blank allows
the team mixing tasks from different project in the same sprint. This
can be useful for example if you belong to a team that basically does
support work for different projects (let's say, system management and
deployment) but still want to reap benefits of Scrum project
management.

The estimated velocity (factor)
*******************************

100% by default but sadly some lower value is more realistic
usually. This factor let's the burndown chart take into account the
fact that more often that not some of the worker hours will be spent
on things not related to the sprint, or maybe we will have a tendency
to be overly optimistic in hour estimations.

See how different values of this field affect the burndown chart:

.. figure:: project_scrum/static/description/burndown-100.png
   :align: center
   :alt: `Burndown 100% velocity`.

   Perfect efficiency.

All available worker hours expected to be used with perfect efficiency
on the sprint.

The blue line starts at 400 hours. If this is correct we are clearly
undercommitting.

.. figure:: project_scrum/static/description/burndown-50.png
   :align: center
   :alt: `Burndown 50% velocity`.

   50% efficiency.

We expect to burn 50% of the work hours on things outside of the
sprint so the blue line starts at 200 hours.

Seeing how this particular sprint went seems more realistic. Take it
into account for the following planning session!

Tasks and developers tabs
~~~~~~~~~~~~~~~~~~~~~~~~~

Set the backlog of the sprint on the `Tasks` tab and the developers
that will be doing the work on the `Developers` task.

.. image:: project_scrum/static/description/scrum-sprint-tasks-tab.png
   :align: center
   :alt: `Sprint Tasks`.

For each task the list shows:

- Its name.
- The developer assigned as responsible for this task on this
  sprint. Can (but it is not expected to) change over time during the
  sprint. This is the person of contact for any issues regarding this
  particular task. Only developers listed on the `Developers` task can
  be used on this field. Although assigning tasks to developers is
  possible here, using the `Tasks Panel` is likely what you will
  prefer.
- The initial estimation.

.. image:: project_scrum/static/description/scrum-sprint-developers-tab.png
   :align: center
   :alt: `Sprint Developers`.

You must list the developers taking part in this sprint in this tab so
that each of them gets a column on the `Tasks Panel`. You are free to
specify a different dedication level for each developer. The default
value is 100% meaning that this particular developer works full time
for the success of this sprint. Set this field to, say, 50% to let the
application know that only a halve of this particular developer's
working hours will be spent on this sprint (likely because she has
other responsabilities). The dedication will be taken into account in
the burndown chart: lower dedication means lower velocity and thus
lower start height of the reference (blue) line.

The chatbox
~~~~~~~~~~~

One outstanding feature of the sprint form is that the chatbox shows
all the messages logged not only on the sprint but also on any of the
tasks hanging from it.

.. image:: project_scrum/static/description/scrum-sprint-chatbox.png
   :align: center
   :alt: `Sprint Chatbox`.

With this feature the scrum master can see all the sprint related
activity, including of course the estimation changes and any notes, on
the sprint form.

Tasks panel
-----------

.. figure:: project_scrum/static/description/tasks-panel.png
   :align: center
   :alt: `Tasks Panel`.

   The tasks panel

The tasks panel shows a column for each of the developers assigned to
this sprint. Each column shows the tasks for which the said developer
is responsible. The tasks panel has three main use cases:

- It let's the stake holders assign tasks to developers by
  drag&drop. The unassigned tasks, that is, the backlog, are shown on
  the `None` column. You should keep this column sorted by their
  priority. That way, when a developer is done with a task he can just
  assign himself the next one from the top of the stack.
- During daily scrum meeting filter the tasks to show only those "not
  done" to get a clear view of active tasks for each developer.
- During the sprint demos show only those "done" to get a clear view
  of the accomplished work.

Let's now take a look at a single Kanban card:

.. figure:: project_scrum/static/description/tasks-panel-single-kanban.png
   :align: center
   :alt: `Sprint task Kanban card`.

   Detail of a Kanban card

In particular look a the two numbers at the bottom of the card. They
are the remaining hours (13 in this case) and the estimated hours to
finalization (6 in this case).

- Remaining hours: this value is computed by substracting the hours
  logged in timesheets to the initial estimation (the allocated hours)
  of the task. So as time goes by and worked time is logged into
  timesheets this number decreases

- Estimated hours to finalization: this is the last estimation
  registered for this particular task. The `UPDATE ESTIMATION` button
  of the task must be used to update the estimation.

Comparing this two numbers gives a rough progress indicator for each
task: as long as the remaining hours are less than the estimated hours
to finalization we are probably on track for this particular task.


  (usually at least
  once a day, just before the daily meeting) and optionally

How to update a task's estimation
---------------------------------

The developers use the `UPDATE ESTIMATION` button of the task to
update the estimation. This button displays the following wizard if
you are not using task stages:

.. figure:: project_scrum/static/description/update-task.png
   :align: center
   :alt: `Task estimation update wizard`.

   Task estimation update wizard

and this one if you are using task stages:

.. figure:: project_scrum/static/description/update-task-with-stages.png
   :align: center
   :alt: `Task estimation update wizard with stages`.

   Task estimation update wizard with stages

This wizard let's the developers update the estimation, include a
description of the update and even change the stage in one
operation. This is not only easier than doing it in several steps. It
also logs all the information in a single chatbox message instead of
two, three or more.
