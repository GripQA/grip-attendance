grip-attendance.py
=========================

Introduction / Description
----------------------

Grip QA's grip-attendance.py tool allows you to easily track and report on
the attendance at your event.

The program matches individuals from the actual attendee report to the
individuals who registered for your event. It generates a new list, based on
the registration list, that shows which registrants attended the event,
which ones did not attend and which attendees did not register (assuming
that you allow un-registered individuals to participate in your events.

We've generally used this tool for tracking the engagement with our
webcasts, but it should be applicable to any event that provides you with a
registration list and an attendee list, both in CSV format.

Command Line Usage
----------------------

USAGE:  grip-attendance.py reg_list.csv attend_list.csv [config_file.cfg]
   or:  grip-attendance.py -[Hh][elp]
   or:  grip-attendance.py -[Gg][en] new_config_file.cfg

Help Text
----------------------

For normal operation, you must provide the relative pathnames for, at
least the two input data files (.csv):
    <reg_list.csv> - CSV file with registration data.
    <attend_list.csv> - CSV file containing actual attendee data.

Optionally, you can also provide the path for a configuration file
(.cfg). If you choose not to explicitly specify a config file, the
program will look for the fixed default config file: "attendance.cfg",
in the current working directory. If no default config file is
available, the program uses pre-defined default values.

The attendance file generated will have the same base name as the the
registration list file, with "_attendance" appended to the basename (if
the registration file name is "reg_list.csv", the attendance report will
be named "reg_list_attendance.csv")

* -[Hh][elp] - "-H" (in either case), optionally followed by "elp" (-help)
will result in this message being displayed.

* -[Gg][en] - "-G" (in either case), optionally followed by "en"
accompanied by a mandatory pathname (-gen config-path.cfg) will cause
the program to generate a template config file that you can customize
for your registration and attendee list formats.
The configuration file provides a way to customize the execution of the
program. The current version focuses on providing a way to identify the
field names in your data to the program.

Configuration File
----------------------

We've made an attempt to provide reasonable defaults, but we recognize
that these will not apply to all situations, if the defaults don't work
for you, the configuration file will be your friend

In addition to the built-in defaults, there are two methods for you to
specify configuration information. You can create a file called
attendance.cfg and place it in the directory that you'll be working in.
This is probably a good mechanism if you're generally working in a
single directory and if your input data files have stable column
headings. You can also specify a configuration file pathname on the
command line.

There are two user "Sections" in the configuration file that you should
be aware of: [REGISTRANTS] and [ATTENDEES], the former specifies field
names for the registration data file, while the latter gives field names
for the actual attendee data file (there's actually a third [DEFAULT]
section, but you should really understand how configuration files are
interpreted before you mess with it.

The most straight forward way to get a new configuration file is to run
this script as:

    grip-attendance.py -Gen new_config_file.cfg

where "new_config_file.cfg" is the pathname for the generated configuration
file. This will create a new configuration file with all of the default values
filled in for each section. Customization is then a simple matter of 
changing the values on the right hand side of the = sign.

Some things to note about configuration file values - these are all
driven by the environment's configuration processing capabilities:

* Upper/Lower case is important

* Changes made to a section will only apply to processing of that
section's corresponding data file

* Don't use quotes unless absolutely necessary to support trailing
blanks in field names (I don't know why some systems generate field
names with trailing blanks, but they do). Spaces between words are fine,
so values with intra-word blank spaces do not require quotes. If you use
quotes, the quotes get included in the value string. If you absolutely
have to use quotes, for the trailing blanks, make use of the following
directives in the config file (if you're using single quotes'). These allow
the program to trim the quotes, while maintaining the trailing blanks:

    TRIM_QUOTES = yes
    QUOTE_CHAR = '


Installation
----------------------

Grip Attendance currently supports [Python 3.x](https://www.python.org/downloads/).

We recommend installing with pip, which should be bundled with Python3.
However, if it's missing, pip can be installed from
[pip](https://pip.pypa.io/en/latest/).

The most straightforward install, if Python3 is your default environment is:

    pip install grip-attendance

If you have multiple versions of Python on your machine, the above will use
your default Python version. If your default is not set to Python3, you might
want to try:

    pip3 install grip-attendance

Another alternative is to try:

    python3 -m pip install grip-attendance

If you're upgrading:

    python3 -m pip install --upgrade grip-attendance

This will install the `grip-attendance` executable on your search path,
except for some MS-Windows installations.

For MS-Windows, I had to manually add:

    ;C:\Python34;C:\Python34\Scripts;

to the PATH environment variable (before the corresponding entries for
Python27) to get pip to work correctly.

If you don't have pip, you can install the program  manually by cloning
the code and running the install script:

    git clone git@github.com:GripQA/grip-attendance.git
    cd grip-attendance
    python setup.py install

Of course, you can always simply grab the 'grip-attendance.py' file (see
below for a discussion of downloading single files from GitHub) and
place it in a directory that's on your search path.

Important Files
----------------------

Many of the files in the repo are related to infrastructure and supporting
the pip distribution. The important files are:

* grip-attendance.py - the program file
* grip_registration.csv - sample event registration list
* grip_attendees.csv - sample event attendee list
* grip_sample.cfg - sample configuration file to support the above lists
* README.md & README.txt - two versions of the README, one for GitHub and one
for easier reading in a local repo.
* LICENSE - text of the Apache License used for this project

If you're downloading the program with pip, the repo URL is:

    https://github.com/GripQA/grip-attendance

The above mentioned files can be downloaded as part of a clone, or individual
files can be downloaded by following the instructions at:
http://stackoverflow.com/a/13593430/3363628  Note that different browsers and
operating systems may have different methods for downloading single files.

Support
----------------------

If you have any questions, problems, or suggestions, please submit an
[issue](../../issues) or contact us at support@grip.qa.

License & Copyright
----------------------

Copyright 2015 Grip QA

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
