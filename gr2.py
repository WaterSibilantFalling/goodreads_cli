#!/usr/bin/env python3



import argparse
import datetime
from pathlib import Path
import regex
import os
import subprocess
import sys
import yappi

prog_name = 'gr'

goodreads_util_path = "/usr/local/bin/goodreads"

rating_cmd        = goodreads_util_path + "  book -r \"{}\" "
b_author_cmd      = goodreads_util_path + "  book -a \"{}\" "
r_dist_cmd        = goodreads_util_path + "  book --rating-dist \"{}\" "
desc_cmd          = goodreads_util_path + "  book -d \"{}\" "
book_id_cmd       = goodreads_util_path + "  book -g \"{}\" "
bname_cmd         = "echo \"{}\" "
# a_top_books_cmd = goodreads_util_path + "  author -b \"{}\" "
# a_all_books_cmd = goodreads_util_path + "  author -B \"{}\" "
# a_about_cmd     = goodreads_util_path + "  author --about \"{}\" "
# a_info_cmd      = goodreads_util_path + "  author --info \"{}\" "
#author_id_cmd    = goodreads_util_path + "  author -g \"{}\" "
# user_id_cmd     = goodreads_util_path + " user -g \"{}\" "
# user_info_cmd   = goodreads_util_path + " user --about \"{}\" "

code_to_cmd =\
    {'r'    :rating_cmd,
     'a'    :b_author_cmd,
     'i'    :book_id_cmd,
     'de'   :desc_cmd,
     'rd'   :r_dist_cmd,
     'b'    :bname_cmd,
     }
     # 'at'   :a_top_books_cmd,
     # 'ab'   :a_all_books_cmd,
     # 'aa'   :a_about_cmd,
     # 'ai'   :a_info_cmd,
     # 'g'    :author_id_cmd,
     # 'u'    :user_id_cmd,
     # 'ua'   :user_info_cmd

# DX is an internal code that represents multiple other codes
DX_desc_codes = ['b','a','r','rd','de']

# -------------------------
def main():
    ''' This program does one of three tasks, depending on what is passed:
        (1) prints a single piece of goodreads data about a book (only, so far)
        (2) renames a directory based on a passed-in pattern (e.g. a/b___r)
        (3) prints some longer block of goodreads info about a book
    '''

    yappi.start()
    args = process_commandline()

    # (1) print single info item
    if len( args['action_code'] ) == 1:
        info = get_gr_data_from_code(
            args['action_code'],
            args['bname_spaces'])
        print(info)
        sys.exit(0)

    # (2) rename the input dir
    elif args['action_code'] == "to":
        orig_path_from_dir_str = find_path_from_subst(args['bname_raw'])
        if orig_path_from_dir_str is not None:
            new_dir_path = path_from_dir_desc_str(args['dir_desc_input_str'],
                                                  args['bname_spaces'],
                                                  orig_path_from_dir_str.parent)
            orig_path_from_dir_str.rename(new_dir_path)
            print("renamed {args['bname_input']} to {new_dir_path}\n")
        else:
            print(f"No dir matching {args['bname_raw']} or \"{args['bname_spaces']}\"")
            print(f" or {args['bname_uscores']} could be found in the directory")
            sys.exit(1)

    # (3) print more detailed info
    elif args['action_code'] in ('de','rd','DX'):
        data = get_gr_data_from_code( args['action_code'], args['bname_spaces'])
        print(data)


    else:
        print("some input error did not get caught")

    func_stats = yappi.get_func_stats()
    func_stats.save('callgrind.out' + datetime.datetime.now().isoformat(), 'CALLGRIND')
    yappi.stop()
    yappi.clear_stats()


# -------------------------
def process_commandline():

    basic_help = f'''
    Usage:

        {prog_name} Some_booK_name
        {prog_name} x   Some_book_name

        {prog_name} yy  "Some book name"
        {prog_name} yy  "Some authors name"             [ Not implemented']
        {prog_name} yy  Some_authors_name               [ Not implemented']

        {prog_name} to  x/x__x      Some_booK_name

        where x is:
            b       for     The_books_name (underscore-separated)
            r       for     book's rating
            a       for     book's author
            i       for     book's id

        and yy is:
            de      for     description of the book
            rd      for     the books rating distribution
            at      for     author's top books          [ Not implemented']
            ab      for     all an author's books       [ Not implemented']
            aa      for     about the author            [ Not implemented']
            ai      for     info about the author       [ Not implemented']

    NOTE: if 'to' is used, the directory matching the book's name will be renamed

    '''

    # --- read in the commandline arguments

    # args['bname_raw']            /dir/a/b/My. Book - name!
    # args['bname_input']          My. Book - name!
    # args['action_code']          'r'   or  'to'
    # args['dir_desc_input_str']   a/b___r
    # then
    # args['bname_uscores']        My__Book___name
    # args['bname_spaces']         My  Book   name

    if len(sys.argv) > 4 or len(sys.argv) <2:
        print(basic_help)
        sys.exit(1)

    book_substr = sys.argv[-1]

    parser = argparse.ArgumentParser(basic_help)

    # error
    if len(sys.argv) < 2:
        print(basic_help)
        sys.exit(1)
    # gr "a Book Title"
    if len(sys.argv) == 2:
        parser.add_argument(
            "bname_raw",
            type=str,
            help="A substring of the books name, with spaces or underscores"
        )
    # gr x some_book_substring
    if len(sys.argv) == 3:
        parser.add_argument(
            'action_code',
            choices=['r','a','i','g','u','de','rd','at','ab','aa','ai','ua'],
            action='store',
            type=str,
            nargs=1
        )
        parser.add_argument(
            "bname_raw",
            type=str,
            help="A substring of the books name, with spaces or underscores"
        )
    # gr to a/b__r
    if len(sys.argv) == 4:
        parser.add_argument(
            'action_code',
            choices=['to'],
            action='store',
            type=str,
            nargs=1
        )
        parser.add_argument(
            'dir_desc_input_str',
            type=str,
            action='store',
            help=" a/b__r : becomes Author_name/book_name___4.12",
            nargs=1
        )
        parser.add_argument(
            "bname_raw",
            type=str,
            help="A substring of the books name, with spaces or underscores"
        )
        # error:
        if len(sys.argv) > 4:
            print(basic_help)
            sys.exit(1)

    args = parser.parse_args()
    
    # convert to a dict of strings
    args = vars(args)
    for k,v in args.items():
        if type(v) is list:
            args[k] = v[0]

    args['bname_input'] = regex.search(r"[^/]*$", args['bname_raw']).group(0)
    args['bname_uscores'] = to_underscores(args['bname_input'])
    args['bname_spaces'] = to_spaces(args['bname_uscores'])

    # default: a full desc of the book: code = DX
    if 'action_code' not in args:
        args['action_code'] = 'DX'

    if not check_book_substr_with_gr(args['bname_spaces']):
        print(f"No book matching {args['bname_raw']} \"{args['bname_spaces']}\"")
        print("could be found by goodreads")
        sys.exit(1)

    return args


# ======== primary functions ==============================


# ---------------------------
def get_gr_data_from_code(
    code,       # str
    source_str
):
    ''' collectz the correct info based on the command
        RE: book names: the version with spaces should be used
        The data is passed back to the caller to be printed
    '''

    this_data = ""
    if code != 'DX':
        cmd_str = code_to_cmd[code].format(source_str)
        cmd_to_run = subprocess.Popen(cmd_str,
                shell=True,
                stdout=subprocess.PIPE).stdout
        this_data = cmd_to_run.read().decode()
        this_data = this_data.strip()

    elif code == 'DX':
        for c in DX_desc_codes:
            cmd_str = code_to_cmd[c].format(source_str)
            cmd_to_run = subprocess.Popen(cmd_str, 
                    shell=True, 
                    stdout=subprocess.PIPE).stdout
            this_data += f"{cmd_to_run.read().decode()}\n"
    else:
        print(f"Could not get any goodreads data for the string {code} in" 
                + f"relation to {source_str}")
        sys.exit(1)

    return this_data


# --------------------------------
def path_from_dir_desc_str(
    desc_in_str,
    item_name,
    base_path 
):
    ''' convert a___x/b___r into Authors_Name___XXXxxxx/Book_title___4.12
    each letter (a, b, x) in the desc_in_str is converted into goodreads
    data, and then subbed back into the desc_in_str.
    Only single letter codes - single item data - are allowed
    '''
    out_str = desc_in_str
    str_parts = regex.split("[ _/]+", desc_in_str)
    len_so_far = 0
    for code in str_parts:
        if len(code) == 1:          # good
            data = get_gr_data_from_code(code, item_name)
            if data:
                data_uscore = to_underscores(data)  # so can form a dir path
                code_locn = out_str.find(code, len_so_far)
                out_str = out_str[:code_locn] + data_uscore + out_str[code_locn+1:]
                len_so_far += len(data_uscore) + 1
            else:                   # bad
                print("couldn't find goodreads data for the '{}' in \"{}\" ".format(code, desc_in_str))
                sys.exit(1)
        else:                       # bad
            print( "error in your dir pattern description \"{}\""
                  .format(desc_in_str))
            sys.exit(1)

    # make path
    out_path = base_path / out_str
    return out_path


# ======== service functions ==============================

# -------------------------
def check_book_substr_with_gr(
    book_name
):  # type: bool

    trial_rating_cmd = rating_cmd.format(book_name)
    cmd = subprocess.Popen(trial_rating_cmd, shell=True, stdout=subprocess.PIPE).stdout
    trial_rating = cmd.read().decode().rstrip()
    found_gr_book = (bool(trial_rating is not None) and (bool(len(trial_rating)>0)) and bool(float(trial_rating)>0))

    return found_gr_book


# -------------------------
def check_book_substr_in_dir(
    args
):              # type: bool

    real_dir_name = ""
    for bname in (args['bname_spaces'], args['bname_uscores'], args['bname_input']):
        real_dir_name = find_path_from_subst( bname )
        if real_dir_name and len(real_dir_name ) > 3:
            break
        else:
            pass
    else:
        return False

    return real_dir_name


# ---------------------------
def find_path_from_subst(
    in_str: str
):
    ''' try to find a single directory matching the input string
        can be called repeatidly to find the right directory
        returns a pathlib path object
        returns None if the dir/path cannot be found.

        some_string        a/dir/some_string
        some string        a/dir/some string
        some, string       a/dir/some, string

        if no '/':
            find a match as pwd/*inputstring*
            then as pwd/*input string*

        if '/'
            find match as inputstring*

    '''
    # strip trailing '/' - else confusion
    in_str = in_str.rstrip('/')


    if in_str.find('/') == -1:
        cwd = os.getcwd()
        test_dir = f"{cwd}/*{in_str}*"
        real_dir_path = _path_if_test_dir_exist( test_dir )
        if real_dir_path is not None:
            return real_dir_path

        # try again, with spaces in the dir name
        in_str_spaces = to_spaces( in_str )
        test_dir = f"{cwd}/*{in_str_spaces}*"
        return _path_if_test_dir_exist( test_dir )

    # if a '/' in the dir_str
    elif in_str.find('/') != -1:
        test_dir = f"{in_str}*"
        real_dir_path = _path_if_test_dir_exist( test_dir )
        return real_dir_path

    # error, unreachable
    else:
        return None




# -------------------------------------
def _path_if_test_dir_exist(dir_str):

    # multiple lines in dir_str
    if len(dir_str.split('\n')) > 1:
        print("Error: two or more dirs match \" {dir_str}\"")
        return None
        # print("bye")
        # exit(1)

    p = Path(dir_str)
    q = Path(p.parent).glob(p.name)  # activate any trailing '*' glob char
    r = sorted(q)                    # converts generator (q) to a list
    if len(r) > 1:
        print("Error: two or more dirs match \" {dir_str}\"")
        return None
    dir_path = Path(r[0])

    # ok if nothing found
    if not dir_path.exists() or not dir_path.is_dir():
        dir_path = None

    # single dir found
    return dir_path


# ---------------------------
def to_underscores(
    in_str,
):
    ''' does NOT change '.' to underscores '''
    in_str_uscores = in_str.translate(str.maketrans(' ,;:','____'))
    return in_str_uscores

def to_spaces(
    in_str,
):
    str_uscores = to_underscores(in_str)
    str_spaces  = str_uscores.translate(str.maketrans('_',' '))
    return str_spaces




# ======== main ===========
if __name__ == '__main__':
    main()



