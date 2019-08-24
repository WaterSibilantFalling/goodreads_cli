
#!env     python3

import argparse
import regex
import os
import sys

goodreads_util_path = "/usr/local/bin/goodreads"

rating_cmd = goodreads_util_path + "book -r \"{}\" "
author_cmd = goodreads_util_path + "book -a \"{}\" "
r_dist_cmd = goodreads_util_path + "book --rating-dist \"{}\" "
desc_cmd   = goodreads_util_path + "book -d \"{}\" "



# -------------------------
def main():

    args = process_commandline()

    # print the goodreads description of the book
    if 'd' in args.do_this:
        bn_r = formatted_bookname_plus_rating(args.bname_spaces)
        print(bn_r, end = '')          # no \n

    # rename the dir
    if 'rename' in args.do_this:
        rename_dir_to_bname___rating( args )

    # rename the dir to Authors_Name/Books_name___4.12
    if rename_author in args.do_this:
        rename_dir_to_author_bname_rating( args )

    # print goodreads summary if no params
    if desc in args.do_this:
        print_goodreads_overview_of_book( args )


# -------------------------
def process_commandline( ):

    # check excessive args
    # should be:
    #   gr  rn  Some_booK_name
    #   gr  author_rename   "Wind in the Willows"
    # so program name an two (2) other parameters ONLY.

    # - collect commandline arguments
    basic_help = ' '.join((
        f'Usage:\n\n',
        f'{sys.argv[0]}  rn  Some_booK_name\n',
        f'{sys.argv[0]}  author_rename "Wind in the willows"\n\n'))

    parser = argparse.ArgumentParser(basic_help)
    parser.add_argument(
        "do_this",
        choices=['r','d', 'rn','rna','rename','author_rename'],
        action='store',
        nargs=1,
        default='d',
        # required=False,  can't yse for positionals
        help='''
        What to do:
            r       print "The_Books_Real_Name____4.12"
            d       print a goodreads description of the book
            rn      rename to  "The_Books_Real_Name____4.12"
            rename  rename to  "The_Books_Real_Name____4.12"
            rna     rename to  "Authors_Name/The_Books_Real_Name____4.12"
            author_rename   to  "Authors_Name/The_Books_Real_Name____4.12"
        '''
    )
    parser.add_argument(
        "bname_input",
        # required=True,
        help="The book's name with underscores or spaces")
    args = parser.parse_args()

    # - checks
    if len(sys.argv) != 3:
        print("There must be two parameters")
        parser.print_help(sys.stderr)           # help include usage (basic_help)
        sys.exit(1)

    # - modifications
    # Three names: bname_input; bname_spaces; bname_uscores
    args.bname_uscores = args.bname_input.translate(
        str.maketrans(' ,.','___')).replace('/','')
    args.bname_spaces = args.bname_uscores.translate(
        str.maketrans('_',' '))

    if 'rn' in args.do_this:
         args.do_this.append('rename')
    if 'rna' in args.do_this:
        args.do_this.append('author_rename')
    if 'd' in args.do_this:
        args.do_this.append('desc')

    return args

# ---------------------------
def formatted_bookname_plus_rating(
    args
):

    bname = args.bname_spaces
    cmd = rating_cmd.format(bnane)
    rating=os.system(cmd)
    if rating is None or len(rating) == 0:
        print("Can't find a rating for the book \"{bname}\" ")
        exit(1)

    bname_w_rating = f"{args.bname_uscores}___{rating}"

    return bname_w_rating



# ---------------------------
def rename_dir_to_bname___rating(
    args
):
    ''' find the correct dir, and rename it to "The_book_name___4.12"
    '''
    # find the correct dir
    old_dir_name = ""
    for bname in (args.bname_spaces, args.bname_uscores, args.bname_input):
        old_dir_name = find_dir_to_rename( bname )
        if old_dir_name and len(old_dir_name ) > 3:
            break
        else:
            pass
    else:
        print(f"can't find a dir matching {args.bname_input}")
        exit(1)

    # get the new dir name
    new_dir_name = formatted_bookname_plus_rating(args.bname_spaces)

    # rename the dir
    cmd = f"/bin/mv {old_dir_name}   {new_dir_name}"
    os.system(cmd)

    # add the author as a .../.author___author_Name file
    cmd = author_cmd.format(bname)
    author = os.system(cmd)
    if author and len(author) > 3:
        author_uscores = autor.translate(str.maketrans(' ,.','___'))
        cmd = f"/usr/bin/touch {new_dir_name}/.author___{author_uscores}"
        os.system(cmd)
    else:
        print(f"couldn't find the author of that book {args.bname_input}")

    return new_dir_name




# ---------------------------
def rename_dir_to_author_bname___rating(
    args
):
    bname_rating_dir_name = rename_dir_to_bname___rating( args )

    # make an "author_name" dir
    cmd = author_cmd.format(bname)
    author = os.system(cmd)
    if author and len(author) > 3:
        author_uscores = autor.translate(str.maketrans(' ,.','___'))
        cmd = f"/bin/mkdir {author_uscores}"
        os.system(cmd)

    # move the name_rating dir under that
    cmd = f"/bin/mv {bname_rating_dir_name}  {author_uscores}/ "
    os.system(cmd)

    return author_uzoscores



# ---------------------------
def print_goodreads_overview_of_book(
    bname       # type: str
):              # type: bool

    print(bname + "\n")
    # TODO: handle if the book can't be found
    cmd = author_cmd.format(bname)
    os.system(cmd)
    cmd = rating_cmd.format(bname)
    os.system(cmd)
    cmd = r_dist_cmd.format(bname)
    os.system(cmd)
    cmd = desc_cmd.format(bname)
    os.system(cmd)



# ---------------------------
def find_dirs_to_rename(
    bname,       # type: str
):                              # type: str
    ''' try to find a single directory matching the input string
        can be called repeatidly to find the right directory
    '''
    cmd = f"/bin/ls -1bd *{bname}*"
    real_dir_name = os.system(cmd)

    # ok if nothing found
    if real_dir_name is None or len(real_dir_name) < 3:
        return ""

    # multiple found
    if len(real_dir_name.split('\n')) > 1:
        print( "Two or more copies of that dir:\" {bname}\"")
        print("Bye")
        exit(1)

    # single dir found
    return real_dir_name


# ======== main ===========
if __name__ == '__main__':
    main()






