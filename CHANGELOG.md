1.3.1, 2026-10-23
-----------------

* Restructure the README around installation from the catalog.

1.3.0, 2026-10-22
-----------------

* Add optional UV, radiation, particulate, CO2 and soil moisture output.
* Escape station strings and use the WeeWX 5 installer.

Upcoming
--------

*   Fixed a warning due to the use of `is` comparison with a literal instead of `==`

1.2
---

*   Using ISO8601 for the default timestamp format. For existing functionality change the `timestamp_fmt` option to
    `human`. 

1.1
---

*   Smaller JSON file to be generated, `current_minimal.json`. No computed or archived values.

1.0 
---

*   Pulled the JSON template in from the failed pull request