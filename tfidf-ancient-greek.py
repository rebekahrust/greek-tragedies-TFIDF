import os
import logging
import bleach
import re

from cltk.corpus.utils.formatter import phi5_plaintext_cleanup
from cltk.corpus.utils.formatter import tlg_plaintext_cleanup
from cltk.corpus.greek.beta_to_unicode import Replacer

from cltk.tokenize.sentence import TokenizeSentence
from nltk.tokenize.punkt import PunktLanguageVars

from cltk.stop.greek.stops import STOPS_LIST
from cltk.stem.lemma import LemmaReplacer

from xml.dom.minidom import parse

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
lemmatizer = LemmaReplacer('greek')


def create_dictionary_of_works(perseus_directory_path):
    # Each Author has their own directory entry so the list of authors is equal to the directory list.
    # we remove entries that have a period in them because they are system folders and files we do not want.
    authors = [folder_directory for folder_directory in os.listdir(perseus_directory_path) if
               folder_directory.find('.') == -1]
    greekworks = dict()
    # Now we get the files for each folder(i.e. author).
    for author in authors:
        # We create a dictionary entry for Author.
        greekworks[author] = list()
        # Now we get each file (i.e. individual greek work e.g. a play) in the list of files for that author
        for play in os.listdir(perseus_root + author + '/opensource'):
            # If the file(e.g. a play) ends in _gk.xml then it is a greek xml file which we want
            if play.endswith('_gk.xml'):
                greekworks[author].append(play)
    return (greekworks)


# The following functions are used to process the XML formatted greek plays
#
# <sp>
#    <speaker>*)aqh/na</speaker>
#    <l>a)ei\ me/n, w)= pai= *larti/ou, de/dorka/ se</l>
#    <l n="95">malakai=s a)do/loisi parhgori/ais,</l>
#    <l>...
# </sp>

# main function to process the play
def parseGreekPlay(play):
    # we are only interested in all <sp> tagged elements
    speakers = play.getElementsByTagName("sp")
    return (handleSpeakers(speakers))


def handleSpeakers(speakers):
    # chunking for each <sp>
    global starting_line_number
    global line_number

    speaker_sequence = list()
    for speaker in speakers:
        starting_line_number = line_number + 1
        speaker_sequence.append(handleSpeaker(speaker))
    return (speaker_sequence)


def handleSpeaker(speaker):
    # extract and process the <speaker> info if there is one designated
    try:
        speaker_unicode = handleSpeakerName(speaker.getElementsByTagName("speaker")[0])
    except IndexError:
        speaker_unicode = 'unknown'
        print("========> Speaker is Missing")
    # extract and process the speakers <l> lines
    retvalue = handleLines(speaker.getElementsByTagName("l"))
    retvalue['speaker'] = speaker_unicode
    return (retvalue)


def handleSpeakerName(speaker_name):
    return (clean_text(getText(speaker_name.childNodes)))


def num(s):
    try:
        return int(s)
    except ValueError:
        return float(s)


def handleLines(lines):
    global line_number, starting_line_number

    # build chunk
    chunk = ''
    for line in lines:
        # Check for line number 'n=' attribute found in every 5th <l>
        lineNumber = re.sub('[^0-9]', '', line.getAttribute("n"))
        if lineNumber == "":
            line_number += 1
        else:
            try:
                line_number = int(lineNumber)
            except ValueError:
                print("ERROR: Tried to convert {} to integer".format(lineNumber))
        chunk += str(getText(line.childNodes) + " ")

    # convert to clean UNICODE
    chunk = clean_text(chunk)
    # create dictionary entry
    return (dict(start_line=starting_line_number, end_line=line_number, text=chunk))


def getText(nodelist):
    # Strip the text out of all enclosing nodes
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc)


# Convert Beta Code to Unicode
def clean_text(text_to_clean):
    r = Replacer()
    upper_case_beta_code_test = bleach.clean(text_to_clean, strip=True).upper()
    # If we don't get rid of periods and semicolons before lemmatizing, there will be some words that won't properly be lemmatized.
    upper_case_beta_code_test = upper_case_beta_code_test.replace(".", " ")
    upper_case_beta_code_test = upper_case_beta_code_test.replace(";", " ")
    unicode_converted = r.beta_code(upper_case_beta_code_test)
    # Lemmatize
    lemmatized_unicode = lemmatizer.lemmatize(unicode_converted.lower(), return_string=True)
    # Sentence Tokenization
    tokenizer = TokenizeSentence('greek')
    tokenized_lemmatized_unicode = tokenizer.tokenize_sentences(lemmatized_unicode)
    # Stopword Filtering
    # This removes words that are so common, they'll appear in every text and therefore are not useful for determining the unique semantics of a play.
    p = PunktLanguageVars()
    punkt_tokenized_lemmatized_unicode = p.word_tokenize(lemmatized_unicode)
    no_stops_list_punkt_tokenized_lemmatized_unicode = [w for w in punkt_tokenized_lemmatized_unicode if
                                                        not w in STOPS_LIST]
    # Text Cleanup. Get rid of all punctuation as some may have still come through the lemmatizing process.
    no_punc_no_stops_list_punkt_tokenized_lemmatized_unicode = phi5_plaintext_cleanup(
        ' '.join(no_stops_list_punkt_tokenized_lemmatized_unicode), rm_punctuation=True, rm_periods=True)
    no_punc_no_stops_list_punkt_tokenized_lemmatized_unicode = tlg_plaintext_cleanup(
        no_punc_no_stops_list_punkt_tokenized_lemmatized_unicode, rm_punctuation=True, rm_periods=False)
    no_punc_no_stops_list_punkt_tokenized_lemmatized_unicode = no_punc_no_stops_list_punkt_tokenized_lemmatized_unicode.replace(
        "·", " ")

    return (no_punc_no_stops_list_punkt_tokenized_lemmatized_unicode)


def write_converted_play(author, playname, tmp_directory, converted_play):
    # Now we can write out converted play
    # Genre/Author/Play/Speaker-start-stop-Lines

    # Create Vocabulary for play
    plays_words = ""

    # Create variable to track speaker files created
    speakers_files = list()

    # Create dictionary to keep track of each speakers words
    speakers_words = {}

    # Create tmp folder if not there
    tmp_file_exist = os.path.isdir(tmp_directory)
    if tmp_file_exist is True:
        pass
    else:
        os.mkdir(tmp_directory)

    # Create author folder if not there
    author_path = tmp_directory + author
    author_path_pres = os.path.isdir(author_path)
    if author_path_pres is True:
        pass
    else:
        os.mkdir(author_path)

    # Loop through play and create speaker folder and create text file for each chunk of lines for speaker
    for actors_line in converted_play:
        # See if 'speaker' folder exists
        # Create speaker folder if not there
        speaker_path = author_path + "/" + str(actors_line['speaker'])
        speaker_path_pres = os.path.isdir(speaker_path)
        if speaker_path_pres is True:
            pass
        else:
            print("Create Directory-> {}".format(speaker_path))
            os.mkdir(speaker_path)

        # Create filename to write to using author-play-speaker-start-stop-lines
        uni_write = speaker_path + '/' + playname + "_" + str(actors_line['speaker']) + "_" + str(
            actors_line['start_line']) + "_" + str(actors_line['end_line']) + ".txt"
        # Add filename to list of files created for play
        speakers_files.append(uni_write)

        # Add to list of all words for speaker
        speakers_words.setdefault(actors_line['speaker'], []).append(actors_line['text'])

        # Write file
        print("\tWriting: {}".format(uni_write))
        with open(uni_write, 'w') as uni_write:
            plays_words += actors_line['text'] + " "
            uni_write.write(actors_line['text'])

    # Write out list of speaker filenames created for play
    # Write file
    fn_speaker_file = author_path + '/' + playname + "_files.txt"
    print("Writing speaker files list: {}".format(fn_speaker_file))
    with open(fn_speaker_file, 'w') as fn_speaker_file:
        fn_speaker_file.write('\n'.join(speakers_files))

    # Write out list of lines for each speaker into one file
    # Iterate through dictionary
    for theSpeaker, theLines in speakers_words.items():
        print("Writing {} vocabulary this.".format(theSpeaker))
        fn_speaker_vocabulary = author_path + "/" + str(theSpeaker) + "/" + playname + "_" + str(
            theSpeaker) + "_vocab.txt"
        with open(fn_speaker_vocabulary, 'w') as fn_speaker_vocabulary:
            fn_speaker_vocabulary.write(' '.join(theLines))

    fn_speaker_lines = speaker_path
    return (plays_words)

def read_file(string):
    opened=open(string)
    read=opened.read()
    closed=opened.close()
    return(read)