#!/usr/bin/python3
"""grip_attendance.py processes webcast registration and attendee lists for
actual participation in the event.

Given a CSV file with the registration information, and another CSV file with
the actual attendees, the script generates an attendance list based on the
registration file that
contains a new field signifying whether, or not, each registrant attended, as
well as new records for those who attended but who were not represented in the
registration list. Of course, these non-registrant rows may not contain the
full set of registration information for the previously unregistered attendee.
The records representing non-registered attendees will only contain data fields
that were available in the attendee list and mapped by this script

Matching between registrants and attendees is based on unique email addresses,
which are corrected to be case insenstive.

Configuration is specified at three levels:
   - Script defaults are hard coded in the script.
   - These can be overridden by a default configuration file, OR
   - Users can specify a configuration file on the command line.
"""

__author__ = "Dean Stevens"
__copyright__ = "Copyright 2015, Spinnaker Advisory Group, Inc."
__license__ = "TBD"
__status__ = "Prototype"
__version__ = "0.01"

import sys
import os
import csv
import configparser
import re
from functools import reduce


# MODULE GLOBALS
ERR_LABEL = "ERROR:  "
NOTE_LABEL = "NOTE:  "
# path for default external configuration file
DEFAULT_CFG_PATH = os.path.normpath("./attendance.cfg")
# appended to the registration file path to receive the script's output
OUTPUT_APPEND = "_attendance.csv"


def open_file(pathname, mode='r', newline=None, verbose=True):
    """Open a file and handle both permissions and existance issues

    Args:
        pathname - String containing the relative pathname to the file to open
        mode - String specifying the mode to open the file, typically 'r' or
                'w', defaults to 'r'
        verbose - Boolean telling the function to print explanatory messages
    Returns:
        
    """
    fp = None
    try:
        fp = open(pathname, mode, newline=newline)
    except PermissionError:
        if verbose:
            print("Sorry, you don't have access to '{0}'".format(pathname))
    except FileNotFoundError:
        if verbose:
            print("Couldn't find the file: '{0}'".format(pathname))
    else:
        if verbose:
            print("Opened: '{}'".format(pathname))
        return fp


def config_help():
    """Help string for the configuration file.
    Returns:
        A string, with appropriate paragraph breaks, that can be formatted
        for presentation
    """
    txt = ("The configuration file provides a way to customize the execution "
           "of the program. The current version focuses on providing a way "
           "to identify the field names in your data to the program.\n\n"
           "We've made an attempt to provide reasonable defaults, but we "
           "recognize that these will not apply to all situations, if the "
           "defaults don't work for you, the configuration file will be your "
           "friend\n\n"
           "In addition to the built-in defaults, there are two methods for "
           "you to specify configuration information. You can create a file "
           "called {0} and place it in the directory that you'll be working "
           "in. This is probably a good mechanism if you're generally working "
           "in a single directory and if your input data files have stable "
           "column headings. You can also specify a configuration file "
           "pathname on the command line.\n\n"
           "There are two user \"Sections\" in the configuration file that you "
           "should be aware of: [REGISTRANTS] and [ATTENDEES], the former "
           "specifies field names for the registration data file, while the "
           "latter gives field names for the actual attendee data file "
           "(there's actually a third [DEFAULT] section, but you should "
           "really understand how configuration files are interpreted before "
           "you mess with it.\n\n"
           "The most straight forward way to get a new configuration file is "
           "to run this script with \"-Gen new_config_file.cfg\" as the "
           "arguments. This will create a new configuration file with all "
           "of the default values filled in for each section. Customization is "
           "then a simple matter of changing the values on the right hand side "
           "of the = sign.\n\n"
           "Some things to note about configuration file values - these are "
           "all driven by the environment's configuration processing "
           "capabilities:\n\n"
           "-> Upper/Lower case is important\n\n"
           "-> Don't use quotes unless absolutely necessary to support "
           "trailing blanks in field names (I don't know why some systems "
           "generate field names with trailing blanks, but they do). Spaces "
           "between words are fine, so values with intra-word blank spaces do "
           "not require quotes. If you use quotes, the quotes get included in "
           "the value string. If you absolutely have to use quotes, for the "
           "trailing blanks, make use of the \"TRIM_QUOTES = yes\" and "
           "\"QUOTE_CHAR = '\" (if you're using single quotes '). These allow "
           "the program to trim the quotes, while maintaining the trailing "
           "blanks.\n\n"
           "-> Changes made to a section will only apply to processing of that "
           "section's corresponding data file\n"
           ""
           ""
           )
    return txt.format(DEFAULT_CFG_PATH)
    

def default_config():
    """Initialize a default ConfigParser object with default values
    
    Returns:
        A ConfigParser object with module defaults set
    """
    cfg = configparser.ConfigParser()
    cfg['DEFAULT'] = {"EMAIL_FIELD":"Email"
                      ,"FIRST_NM_FIELD":"First Name"
                      ,"LAST_NM_FIELD":"Last Name"
                      ,"ATTENDED_FIELD":"Attended"
                      ,"ATTEND_DUR_FIELD":"Attendance Duration"
                      ,"TRIM_QUOTES":"yes"
                      ,"QUOTE_CHAR":'"'
                      ,"NOT_AVAIL":"N/A"
                      }
    cfg['REGISTRANTS'] = {}
    cfg['ATTENDEES'] = {}
    return cfg


def wrap_and_indent(text, width, indent):
    """A word-wrap function that preserves existing line breaks
    and most spaces in the text. Expects that existing line
    breaks are posix newlines (\n).
    Borrowed directly from:
        http://code.activestate.com/recipes/148061-one-liner-word-wrap-function/
    
    Args:
        text - string containing the text to be wrapped and indented
        width - the maximum width of the formatted block
        indent - the number of spaces to indent the formatted block
    Returns:
        A string ready for printing
    """
    wrapped = reduce(lambda line, word, width=width: '%s%s%s' %
                  (line,
                   ' \n'[(len(line)-line.rfind('\n')-1
                         + len(word.split('\n',1)[0]
                              ) >= width)],
                   word),
                  text.split(' ')
                 )
    pattern = re.compile('\\n', re.MULTILINE)
    indent_fmt = "{0}" + re.sub(pattern, "\n{0}", wrapped)
    return indent_fmt.format(' '*indent)


def usage_message(program_file):
    """Creates a usage/help message string for the program
    
    Args:
        program_file - string representing the name of the current main
                       program
    Returns:
        1. The usage line
        2. The explanation text
        3. The configuration file help text
        All as strings, both formatted for printing
    """
    fmt = ("\nUSAGE:  {0} reg_list.csv attend_list.csv [config_file.cfg]\n"
           "   or:  {0} -[Hh][elp]\n"
           "   or:  {0} -[Gg][en] new_config_file.cfg\n"
           )
    usage = fmt.format(program_file)
    txt = ("For normal operation, you must provide the relative pathnames "
           "for, at least the two input data files (.csv):\n"
           "    <reg_list.csv> - CSV file with registration data.\n"
           "    <attend_list.csv> - CSV file containing actual attendee "
           "data.\n\n"
           "Optionally, you can also provide the path for a configuration "
           "file (.cfg). If you choose not to explicitly specify "
           "a config file, the program will look for the fixed default "
           "config file: \"{0}\", in the current working directory. "
           "If no default config file is available, the program uses "
           "pre-defined default values.\n\n"
           "The attendance file generated will have the same base name as the "
           "the registration list file, with \"_attendance\" appended to the "
           "basename (if the registration file name is \"reg_list.csv\", "
           "the attendance report will be named "
           "\"reg_list_attendance.csv\")\n\n"
           "-[Hh][elp] - \"-H\" (in either case), optionally followed by "
           "\"elp\" (-help) will result in this message being displayed.\n\n"
           "-[Gg][en] - \"-G\" (in either case), optionally followed by "
           "\"en\" accompanied by a mandatory pathname (-gen config-path.cfg) "
           "will cause the program to generate a template config file that "
           "you can customize for your registration and attendee list formats."
           )
    explanation = wrap_and_indent(txt.format(DEFAULT_CFG_PATH), 72, 8)
    config_txt = wrap_and_indent(config_help(), 72, 8)
    return usage, explanation, config_txt


def print_usage_message(program_file, help_msg=False):
    """Prints the usage message, and optionally, the help message
    
    Args:
        program_file - string representing the name of the current main
                       program
        help_msg - Boolean, if true, also print the help 'explanation' message
                   Defaults to only printing the usage string

    Returns:
        No returned value
    """
    usage, explanation, config_txt = usage_message(program_file)
    if help_msg:
        print('\n'.join([usage, explanation, config_txt, '\n']))
    else:
        print(usage)


def dump_cfg(cfg):
    """Utility function to dump a configuration object to the terminal for
    debugging.
    Args:
        cfg - the configuration object to be examined
    Returns:
        No returned value
    """
    for section in cfg.keys():
        print("[{0}]".format(section))
        for k,v in cfg[section].items():
            # print will eliminate trailing spaces, so to show that
            # we preserved them...
            val = v if v[-1] != ' ' else ''.join(['|', v, '|'])
            print("{0} = {1}".format(k.upper(),val))
            

def gen_config_template(config_path):
    """Uses the default values to generate a config file that users can
    start customizing for their own installation.
    NOTE: Only exposes the "REGISTRANTS" and "ATTENDEES" sections
    Args:
        config_path - file system pathname where the config file is to be
                        written
    Returns:
        No returned value
    """
    cfg_file = open_file(config_path, mode='w')
    if cfg_file is not None:
        with cfg_file:
            # Dump out the comments / instructions
            config_txt = wrap_and_indent(config_help(), 72, 1)
            np = re.compile('\\n', re.MULTILINE)
            config_text_comments = re.sub(np, "\n#", "#" + config_txt)
            cfg_file.write(config_text_comments)
            # Get a default config object & initialize the list of 
            # values
            cfg = default_config()
            cfg_items = []
            # Collect the values in the default section
            for k,v in cfg['DEFAULT'].items():
                cfg_items.append("{0} = {1}\n".format(k.upper(), v))
            
            # Sorting makes it easier to find fields in the config file...
            cfg_items = sorted(cfg_items)
            # For each of the user sections, dump the list of values
            for section in ["[REGISTRANTS]","[ATTENDEES]"]:
                cfg_file.write(''.join(["\n", section, "\n"]))
                for fld in cfg_items:
                    cfg_file.write(fld)
          

def proc_config(config_arg=None):
    """Builds up the configuration object by:
    First: Creating the default object
    Second: Attempting to load the default external file
    Finally: Attempting to load the configuration file specified on the
             command line
    Note: Values specified in any of the above override values specified
          in a predecessor definition

    Args:
        config_arg - string representing the pathname of the user specified
                        configuration file - may be None

    Returns:
        A configuration object. Will always have something, even if it's just
        the defaults
    """
    # Initialize with the program's coded defaults
    cfg = default_config()
    # Then try the default external configuration file
    cfg_handle = open_file(DEFAULT_CFG_PATH)
    if cfg_handle is not None:
        cfg.read(cfg_handle, verbose=False)
        print("{0}Loaded default config file.".format(NOTE_LABEL))
    else:
        print("{0}No default config file available".format(NOTE_LABEL))
    # Finally attempt to load from the file the user specified on the command
    # line
    if config_arg is not None:
        user_cfg_handle = open_file(config_arg, verbose=False)
        if user_cfg_handle is not None:
            cfg.read(config_arg)
            print("{0}Loaded config file: '{1}".format(NOTE_LABEL, config_arg))
        else:
            fstr = ("{0}Unable to access specified config file: '{1}'\n"
                    "{2}Using default values.")
            print(fstr.format(ERR_LABEL, config_arg, ' '*len(ERR_LABEL)))

    # For each section, if we're directed to strip quotes, we'll do it. This
    # seems to be the only way to allow field names with trailing spaces to
    # be specified in a cfg file.
    for section in cfg.keys():
        # We only trim a section if they told us to.
        if cfg[section]['TRIM_QUOTES'].lower() == "yes":
            qchar = cfg[section]['QUOTE_CHAR']
            for k,v in cfg[section].items():
                # We don't want to wipe out our QUOTE_CHAR, and we only
                # want strings that are quoted at both ends.
                if len(v) > 1 and v[0] == qchar and v[-1] == qchar:
                    cfg[section][k] = v.strip(qchar)
                    fmt = "Section: {0}, Key: {1}, Val: |{2}|"
                    print(fmt.format(section, k.upper(), cfg[section][k]))

    return cfg


def proc_args(program_file, argv):
    """Attempts to extract the two required and one optional argument
    specifying input files and (optionally) config files from the argv list
    NOTE: The arguments are tested for presence and the files are tested for
    existence and valid access permissions. Returns None if there are any
    issues.
    
    Args:
        program_file - string representing the name of the current main
                       program
        argv - the system argv list, containing the command line args

    Returns:
        Argument dictionary with {"registrations":file_object
                                  ,"attendees":file_object
                                  ,"attendance":file_object
                                  ,"config":config_object
                                  }
        ... if the argument list parsed correctly.
        Otherwise, None
    """
    rtn_val = None
    args = {"registrants":None
            ,"attendees":None
            ,"attendance":None
            ,"config":None
            }
    def check_switch(switch, arg):
        # Returns True if the arg matches thw specified switch.
        # Args:
        #   switch - string representing the switch to test against
        #   arg - argument to test
        # Returns:
        #   True if the argument matches the switch
        rtn_val = False
        if (len(switch) >= 2 and 
           (arg.lower() == switch[:2].lower() or 
            arg.lower() == switch.lower())):
            rtn_val = True
        
        return rtn_val
    if len(argv) == 2:
        if check_switch("-help", argv[1]):
            print_usage_message(program_file, True)
        else:
            fmt = "\n{0}Unrecognized argument: \"{1}\" Please try again.\n"
            print(fmt.format(ERR_LABEL, argv[1]))
            sys.exit(1)
    elif len(argv) == 3 and check_switch("-gen", argv[1]):
        fmt = "{0}Attemping to generate config file template in: {1}"
        print(fmt.format(NOTE_LABEL, argv[2]))
    elif len(argv) == 3 or len(argv) == 4:
        regf = open_file(argv[1])
        attf = open_file(argv[2])
        outf = open_file(os.path.splitext(argv[1])[0] + OUTPUT_APPEND
                         ,mode='w'
                         ,newline='')
        if regf is not None and attf is not None and outf is not None:
            args['registrants'] = regf
            args['attendees'] = attf
            args['attendance'] = outf
            if len(argv) == 4:
                args['config'] = proc_config(argv[3])
            else:
                args['config'] = proc_config()
            rtn_val = args
    else:
        print("{0}Incorrect number of arguments.".format(ERR_LABEL))
        err_str = "{0}Expected 2, or 3, arguments. Received {1} args"
        print(err_str.format(len(ERR_LABEL)*' ', len(argv)-1))
        print_usage_message(program_file, False)

    return rtn_val


def proc_registration(reg_file, config):
    """Opens the registration list file, reads the contents and sets the
    value in the new attendance field to false for each attendee.
    Collects all attendee records into a list for return to caller
    
    Args:
        reg_file - file object for the file containing the list of registrants
                    We assume that this file object is valid, so no checking
        config - ConfigParser object containing the configuration data
                       
    Returns:
        tuple containing:
        - A list of the registrants
        - A list containing the fieldnames in the registration list data
    """
    reg_list = []
    attended_field = config['REGISTRANTS']['ATTENDED_FIELD']
    attend_duration_field = config['REGISTRANTS']['ATTEND_DUR_FIELD']
    with reg_file:
        reader = csv.DictReader(reg_file)
        for row in reader:
            # Create the attendance field and set it to false
            row[attended_field] = False
            # Create the attendance duration field and set it to "0.0 mins"
            row[attend_duration_field] = "0.0 mins"
            reg_list.append(row)
            fields = reader.fieldnames

    return reg_list, fields


def proc_attendees(att_file, config):
    """Opens the attendee list file, reads the contents and collects the
    desired information (currently first name, last name and email addresses)
    of the actual attendees into a dictionary keyed by the lowercase email
    address.  This collection is returned.
    This collection allows for quick look-up (for checking attendance)
    and eliminates duplicate email addresses.
    
    Args:
        att_file - file object for the file containing the list of attendees
                    We assume that this file object is valid, so no checking
        config - ConfigParser object containing the configuration data

    Returns:
        dictionary containing the de-duplicated collection of all attendees.
        Keys are the email attendee email addresses forced to lower case.
    """
    
    attendees = {}
    email_field = config['ATTENDEES']['EMAIL_FIELD']
    with att_file:
        reader = csv.DictReader(att_file)
        # use splitlines() to remove the line end characters
        #attendees = att.read().lower().splitlines()
        for row in reader:
            attendees[row[email_field].lower()] = row

    return attendees


def check_attendance(registrants, attendees, config):
    """Iterates through the list of registrants and checks each registrant
    against the collection of emails of the actual attendees.  If the
    registrant's email address is present in the collection of attendees,
    the ATTENDED_FIELD field is set to true for the registrant.
    
    This function maintains a set of registered attendee email addresses.
    The difference between the original attendee set and the set of registered
    attendees is treated as the collection of attendees that did not register.
    
    This collection of individuals that attended, but did not register is
    iterated over and corresponding registration records are created for each
    unregistered attendee.  Note that these new records will not contain most
    of the registration information.
    Args:
        registrants - list of all registration records
        attendees - dictionary containing the actual attendee records, with
                    email addresses forced to lowercase as the keys
        config - ConfigParser object containing the configuration data

    Returns:
        Dictionary containing the attendance counts.
    """
    # Field name mappings, note that the "_att" suffixes apply to the
    # attendee file, while "_reg" applies to the registration file
    email_field_reg = config['REGISTRANTS']['EMAIL_FIELD']
    email_field_att = config['ATTENDEES']['EMAIL_FIELD']
    attended_field = config['REGISTRANTS']['ATTENDED_FIELD']
    first_nm_field_reg = config['REGISTRANTS']['FIRST_NM_FIELD']
    first_nm_field_att = config['ATTENDEES']['FIRST_NM_FIELD']
    last_nm_field_reg = config['REGISTRANTS']['LAST_NM_FIELD']
    last_nm_field_att = config['ATTENDEES']['LAST_NM_FIELD']
    attend_dur_reg = config['REGISTRANTS']['ATTEND_DUR_FIELD']
    attend_dur_att = config['ATTENDEES']['ATTEND_DUR_FIELD']
    na_val = config['REGISTRANTS']['NOT_AVAIL']

    def proc_unreg(unregistered, reg_fields):
        """Factory method to create a new registration record for the given
        email address.  NOTE:  the default value for all fields is specified
        in this method

        Args:
            unregistered - dictionary containing the information of an
                                individual that attended the event.  Will be
                                used for the new registration record
            reg_fields - list of strings identifying the field names (used
                                as keys in this implementation) for the
                                registration record.
        Returns:
            counts - dictionary containing attendance statistics
        """
        # Initialize the dictionary representing the new record with the
        # default field value, then set the ATTENDED_FIELD field to True,
        # finally add the new row to the collection of registrants.
        new_reg = {fld:na_val for fld in reg_fields}
        new_reg[email_field_reg] = unregistered[email_field_att]
        new_reg[last_nm_field_reg] = unregistered[last_nm_field_att]
        new_reg[first_nm_field_reg] = unregistered[first_nm_field_att]
        new_reg[attend_dur_reg] = unregistered[attend_dur_att]
        new_reg[attended_field] = True        
        registrants.append(new_reg)
        print("Unregistered attendee: " + repr(unregistered[email_field_att]))

    # Keeps the counts of registrants, attendees, etc.
    counts = {'registrants':len(registrants)
             ,'attendees':len(attendees)
             ,'reg_no_attend':0
             ,'attend_no_reg':0
             }
    # We'll keep a list of the attendees that were also registered.  This list
    # will be used to deduce the list of attendees that weren't registered.
    registered = []
    reg_fields = list(registrants[0].keys())
    # We'll need a set identify the group of attended, but unregistered
    # individuals, so we might as well use it for checking attendance, as
    # well
    attendee_set = frozenset(attendees.keys())
    
    for reg in registrants:
        reg_email = reg[email_field_reg].lower()
        if reg_email in attendee_set:
            reg[attended_field] = True
            reg[attend_dur_reg] = attendees[reg_email][attend_dur_att]
            registered.append(reg_email)
    # We should have all of the registered attendees marked. The registrants
    # that did not attend are marked when the registration list was processed.
    # Now we have to deal with the attendees that weren't registered
    unregistered = attendee_set - set(registered)
    for unreg in unregistered:
        proc_unreg(attendees[unreg], reg_fields)
    
    # Complete the counts
    counts['attend_no_reg'] = len(unregistered)
    counts['reg_no_attend'] = counts['registrants'] - (counts['attendees'] -
                                                       counts['attend_no_reg'])
    return counts


def format_counts(counts):
    """Formats the contents of the counts dictionary into a string suitable
    for output.
    
    Args:
        counts - dictionary containing the attendance statistics
    Returns:
        string containing the counts formatted for output
    """
    fstr = ("Attendance Figures:\n"
            "    Registrations:    {0}\n"
            "    Total Attendees:  {1}\n"
            "    Registered No Shows:       {2}\n"
            "    Non-registered Attendees:  {3}\n")
    return fstr.format(counts['registrants']
                       ,counts['attendees']
                       ,counts['reg_no_attend']
                       ,counts['attend_no_reg'])


def gen_attendance(out_file, registrants, fields, config):
    """Open/Create the CSV file to receive the new attendance information and
    write the records.  Note that the ATTENDED_FIELD column is added to the
    list of field names by this function.

    Args:
        out_file - file object for the file that will  contain the updated
                    registration / attendance records
                    We assume that this file object is valid, so no checking
        registrants - list of the updated registration / attendance records
        fields - list of the fields, in the desired order, to be written
        config - ConfigParser object containing the configuration data

    Returns:
       No returned value
    """
    # We added new columns to the CSV file
    fields.extend([config['REGISTRANTS']['ATTENDED_FIELD']
                   ,config['REGISTRANTS']['ATTEND_DUR_FIELD']])
    with out_file:
        writer = csv.DictWriter(out_file, fields)
        writer.writeheader()
        for reg in registrants:
            # print(reg)
            writer.writerow(reg)
            

def match_main(arg_dict):
    """Primary driving function for the match.
    
    First, we create the pathnames, then we load both the registration list
    and the attendee list.  Finally, we check attendance and produce the
    results.
    
    Args:
        arg_dict - dictionary containing the file objects for the registration
                    and attendee lists, along with the config object
    Returns:
        Nothing
    """
    
    cfg = arg_dict['config']
    registrants, fields = proc_registration(arg_dict['registrants'], cfg)
    attendees = proc_attendees(arg_dict['attendees'], cfg)
    attendance = check_attendance(registrants, attendees, cfg)
    gen_attendance(arg_dict['attendance'], registrants, fields, cfg)
    print(format_counts(attendance))


if __name__ == '__main__':
    prog_args = proc_args(__file__, sys.argv)
    if prog_args is not None:
        match_main(prog_args)

