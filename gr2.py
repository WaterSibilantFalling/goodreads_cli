#!/usr/bin/env python3



import argparse
import regex
import os
import sys

prog_name = 'gr'

goodreads_util_path = "/usr/local/bin/goodreads"

rating_cmd      = goodreads_util_path + "book -r \"{}\" "
b_author_cmd      = goodreads_util_path + "book -a \"{}\" "
r_dist_cmd      = goodreads_util_path + "book --rating-dist \"{}\" "
desc_cmd        = goodreads_util_path + "book -d \"{}\" "
book_id_cmd     = goodreads_util_path + "book -g \"{}\" "
# a_top_books_cmd = goodreads_util_path + "author -b \"{}\" "
# a_all_books_cmd = goodreads_util_path + "author -B \"{}\" "
# a_about_cmd     = goodreads_util_path + "author --about \"{}\" "
# a_info_cmd      = goodreads_util_path + "author --info \"{}\" "
#author_id_cmd   = goodreads_util_path + "author -g \"{}\" "
# user_id_cmd     = goodreads_util_path + "user -g \"{}\" "
# user_info_cmd   = goodreads_util_path + "user --about \"{}\" "

code_to_cmd =\
    {'r'    :rating_cmd,
     'a'    :b_author_cmd,
     'i'    :book_id_cmd,
     'de'   :desc_cmd,
     'rd'   :r_dist_cmd,
     # 'at'   :a_top_books_cmd,
     # 'ab'   :a_all_books_cmd,
     # 'aa'   :a_about_cmd,
     # 'ai'   :a_info_cmd,
     # 'g'    :author_id_cmd,
     # 'u'    :user_id_cmd,
     # 'ua'   :user_info_cmd
     }



# -------------------------
def main():

    args = process_commandline()

    # print some info
    if len( args.action_code ) == 1:
        info = get_gr_data_from_code(
            args.action_code,
            args.bname_spaces)
        print(info)

    # rename the input dir
    elif args.action_code == "to":
        orig_path_from_dir_str = find_path_from_subst( args.bname_input)
        new_dir_path = path_from_dir_desc_str( args, dir_desc_input_str)
        orig_path_from_dir_str.rename(new_dir_path)

    # print more detailed info
    elif args.action_code in ('de','rd'):
        data = get_gr_data_from_code( args.action_code, bname_spaces)

    else:
        print("some input error did not get caught")



# -------------------------
def process_commandline():

    basic_help = f'''
    Usage:

        {prog_name} Some_booK_name
        {prog_name} x   Some_book_name

        {prog_name} yy  "Some book name"
        {prog_name} yy  "Some authors name"
        {prog_name} yy  Some_authors_name

        {prog_name} to  x/x__x      Some_booK_name

        where x is:
            b       for     The_books_name (underscore-separated)
            r       for     book's rating
            a       for     book's author
            i       for     book's id

        and yy is:
            de      for     description of the book
            rt      for     the books rating distribution
            at      for     author's top books
            ab      for     all an author's books
            aa      for     about the author
            ai      for     info about the author

    NOTE: if 'to' is used, the directory matching the book's name will be renamed

    '''

    a=15

    # --- read in the commandline arguments

    # args.bname_input
    # args.action_code
    # args.dir_desc_input_str
    # then
    # args.bname_uscores
    # args.bname_spaces

    if len(sys.argv) > 4 or len(sys.argv) <2:
        print(basic_help)
        sys.exit(1)

    book_substr = sys.argv[:1]

    parser = argparse.ArgumentParser(basic_help)

    # error
    if len(sys.args) < 2:
        print(basic_help)
        sys.exit(1)
    # gr "a Book Title"
    if len(sys.args) == 2:
        parser.add_argument(
            "bname_input",
            help="A substring of the books name, with spaces or underscores"
        )
    # gr x some_book_substring
    if len(sys.argv) == 3:
        parser.add_argument(
            'action_code',
            choices=['r','a','i','g','u','de','rd','at','ab','aa','ai','ua'],
            action='store',
            nargs=1
        )
        parser.add_argument(
            "bname_input",
            help="A substring of the books name, with spaces or underscores"
        )
    # gr to a/b__r
    if len(sys.argv) == 4:
        parser.add_argument(
            'action_code',
            choices=['to'],
            action='store',
            nargs=1
        )
        parser.add_argument(
            'dir_desc_input_str',
            action='store',
            help=" a/b__r : becomes Author_name/book_name___4.12",
            nargs=1
        )
        parser.add_argument(
            "bname_input",
            help="A substring of the books name, with spaces or underscores"
        )
        # error:
        if len(sys.argv) > 4:
            print(basic_help)
            sys.exit(1)

    args = parser.parse_args()

    # --- check the commandline argument

    args.bname_uscores = to_underscores(args.bname_input)
    args.bname_spaces = to_spaces(args.bname_uscores)

    # if args.action_code in ['r','a',
    if not check_book_substr_with_gr( args ):
        print(f'No book matching {args.bname_input} \"{args.bname_spaces}\"')
        print("could be found by goodreads")
        sys.exit(1)


    if not check_book_substr_in_dir( args ):
        print(f'No dir matching {args.bname_input} or \"{args.bname_spaces}\"')
        print(f" or {args.bname_uscores} could be found in the directory")
        sys.exit(1)



# --------------------------
def path_from_dir_desc_str(
    args,
    desc_in_str
):
    ''' convert a___x/b into Authors_Name___XXXxxxx/Book_title___4.12
    each letter (a, b, x) in the desc_in_str is converted into goodreads
    data, and then subbed back into the desc_in_str
    '''
    out_str = desc_in_str
    str_parts = regex.split("[ _/]+", desc_in_str)
    for code in str_parts:
        if len(code) == 1:
            data = get_gr_data_from_code(code)
            if data:
                data_uscore = to_underscores(data)
                out_str = regex.sub(code, data_uscore, out_str)
            else:
                print("couldn't find goodreads data for the '{}' in \"{}\" ").format(code, desc_in_str)
                sys.exit(1)
        else:
            print( "error in your dir pattern description \"{}\""
                  ).format(desc_in_str)
            sys.exit(1)

    # make path
    out_path = Path(out_str)
    return out_path



# -------------------------
def check_book_substr_with_gr(
    args
):  # type: bool

    trial_rating = rating_cmd.format(args.bname_spaces)
    found_gr_book =  (bool(trial_rating is not None) and bool(int(trial_rating)>0))

    return found_gr_book


# -------------------------
def check_book_substr_in_dir(
    args
):              # type: bool

    real_dir_name = ""
    for bname in (args.bname_spaces, args.bname_uscores, args.bname_input):
        real_dir_name = find_path_from_subst( bname )
        if real_dir_name and len(real_dir_name ) > 3:
            break
        else:
            pass
    else:
        return False

    return True



# ---------------------------
def find_path_from_subst(
    bname,       # type: str
):                              # type: str
    ''' try to find a single directory matching the input string
        can be called repeatidly to find the right directory
        returns a pathlib Path object
    '''
    cmd = f"/bin/ls -1bd *{bname}*"
    real_dir_name = os.system(cmd)

    # multiple found
    if len(real_dir_name.split('\n')) > 1:
        print( "Two or more dirs match \" {bname}\"")
        print("Bye")
        exit(1)

    real_dir_path = Path(real_dir_name)

    # ok if nothing found
    if not real_dir_path.exists() or not real_dir_path.is_dir():
        real_dir_path = None

    # single dir found
    return real_dir_path


# ---------------------------
def get_gr_data_from_code(
    code,       # str
    source_str
):
    ''' collectz the correct info based on the command
        RE: book names: the version with spaces should be used
        The data is passed back to the caller to be printed
    '''

    # combinded : only 'de' 'description'
    if code == 'de':
        if not args:
            print("Error in get_gr_data_from_code")
            sys.exit(1)
        bname = source_str
        author = b_author_cmd.format(source_str)
        rating = rating_cmd.format(source_str)
        r_dist = r_dist_cmd.format(source_str)
        desc = desc_cmd.format(source_str)

        data_str = f'{bname}\nBy\t{author}\n\n{rating}\n{r_dist}\n\n\n{desc}\n'
    else:
        cmd = code_to_cmd(code).format(source_str)
        data_str = os.system(cmd)

    return data_str



# ---------------------------
def to_underscores(
    in_str,
):
    in_str_uscores = in_str.translate(str.maketrans(' ,.','___'))
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



