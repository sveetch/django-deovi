.. _intro_history:

=======
History
=======

Version 0.6.2 - 2024/05/01
--------------------------

* Updated to Deovi==0.7.0, this is a breaking changes since previous Deovi dumps won't
  be compatible anymore (you need to dump with Deovi>=0.7.0);
* Fixed requirements for optional ``bigtree`` dependency to ``pandas``;
* Added field ``last_update`` to ``Device`` model;
* Improved model admins with list display, list filters and field search;
* Added validation on device slug from loader and fill title with slug on device
  creation;
* Improved device index and detail to include disk usages;
* Refined device index layout;
* Added new device tree export action to sum sizes of selections;


Version 0.6.1 - 2023/11/06
--------------------------

Fixed missing management command from released package.


Version 0.6.0 - 2023/08/16
--------------------------

* Implemented new features from Deovi version 0.5.2 to 0.6.1;
* Added new requirement for ``bigtree``;
* Added Device directories tree view with basic selection export actions;
* Added Python 3.9 and 3.10 support;


Version 0.5.1 - Unreleased
--------------------------

Implemented new fields from Deovi 0.5.1 collector.


Version 0.5.0 - Unreleased
--------------------------

Enhanced frontend layout with Bootstrap 5.2.x and some themes from Bootswatch. However
only the 'Darkly' theme is enabled and internal layout components have been done
without to bother about using generic theme colors, only 'Darkly'.


Version 0.1.0 - Unreleased
--------------------------

* First commit.
