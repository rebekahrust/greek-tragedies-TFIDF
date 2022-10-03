# greek-tragedies-TFIDF
December 2016 project analyzing term frequency in extant ancient Greek tragedies
## Introduction
I have modeled my project on a standard basic level NLP project: calculate TF-IDF, convert the word frequencies into vectors, compare the similarities between vectors using both Euclidean distance and cosine similarity, and plot the results. I have relied heavily upon the Classical Language Toolkit, its documentation, and sample code created by Kyle Johnson, Patrick Burns, et al.. The tutorials, code, and methodology of Allen Riddell were very helpful for the vectoring stages. StackOverflow has been immensely helpful throughout.

Using the CLTK and writing the code with python, this particular project will look at the TF-IDF of tragic and comic genres, dramatic authors, individual plays, and individual characters. I will investigate both dramatic genres in order to ask questions about genre differences in characterization. These term frequencies will be converted into vectors, compared using a cosine similarity function, and plotted onto a graph for the benefit of the researcher and reader. The project can be divided into four parts: input, pre- processing, processing, and output.

## Input and Pre-Processing

For the computer to be able to process the texts, the information has to first exist and be in a standardized form. The general steps involved are as follows: downloading the greek corpus from the CLTK, parsing the .xml into a Document Object Model (DOM) structure so that the texts could be traversed and chunked into meaningful sections (such as a play broken down by speaker lines), converting the meaningful .xml files from beta code into unicode, cleaning the text (lemmatizing it, removing punctuation, etc.), and writing these files into a .txt file with a meaningful filename and sorted into a directory structure of which the hierarchy is: author, play, character, chunks of spoken lines, by lines. Included, are files containing total bag-of-words by author, by play, by character. The decision to implement python’s built-in DOM parser proved crucial (though it took many attempts to figure it out and reach a useful point). The DOM added a standard structure that provided me flexibility to easily accommodate my research needs, such as a late decision to track line numbers, and accommodate any future work in another language or with a different kind of text than a play.

## Processing

I used the sklearn document term matrix, but a more specific kind of DTM is TF-IDF. The goal was to convert the various “bag-of-words” into Term Frequency-Inverse Document Frequency (TF-IDF) and vector the documents using scilearn. TF-IDF calculates how important a word is by weighing a word’s value in a document against the frequency of that word in a larger corpus. One outcome of this function is that TF-IDF diminishes the value of “stop-words” on the final bag-of-words. This is a necessary step for this project in particular as the greek lemmatizer is not fully accurate and words, particularly pronouns and the conjugated forms of the verb-to-be, slip through the stops_list. Although in tests I was able to get the TF-IDF working, lack of time has prevented me from implementing this step.6 This point in the project is when the TF-IDF vectoring would be done. My test code is included in the jupyter notebook for reference.

Once the matrix is created and the document vectorized, I can now compare documents vectorized in the same document space with distance functions. The way I am comparing these matrices is through euclidean distance and cosine similarities. Euclidean distance similarity is not normalized and therefore the magnitude of term frequency can skew the distance between documents with similar vocabulary when one is shorter than the other even though they use the same words.7 The cosine similarity function, on the other hand, ‘normalizes’ the magnitude of frequency as it compares the texts as ratios and not as raw frequencies.

## Results

This section is purposefully not titled “conclusions”, because I wish to stress how provisional the results of this project are. First of all, there is the provisional nature of the evidence to take into account. It is a fact of classical scholarship and of Greek drama in particular that the texts we possess do not constitute “Greek drama” but are a fractured view of whatever Greek drama was. Regardless of that fact, the data used is still incomplete as not even all extant Greek drama is included (e.g. there are texts of Euripides which are not open-sourced on Perseus and therefore not available on the CLTK). Euclidean distance and cosine similarity do not themselves give conclusions, but rather are a way for the researcher to engage in a dialogue with the data. Drucker’s warnings to humanists about how misleading charts can be is worth keeping in mind.8 Therefore, the conclusions made are more indicative of than descriptive of potential phenomena in Greek drama. The possibilities are very interesting. The combination of objects to be analyzed are numerous, but here I’ve limited to examples from three levels of analysis: author similarities, play similarities, and character similarities.

### Author Similarities

These two graphs chart the similarities between the four dramatists based upon the “bag-of-words” files of each. These documents (four of them) are then compared resulting in the following:

It is interesting that in both graphs Sophocles is nearer the base line, as scholars in tragedy often consider him the “middle” of the three tragedians so much so that he is often used as a kind of ‘control group’. I shall focus on the cosine similarity graph because, as cosine analyzes ratios, the impact on the data that Euripides has more plays being analyzed and that some plays are longer than others is diminished.

From the cosine graph, we see that Sophocles and Euripides are more similar than Aristophanes and Aeschylus. In fact, Sophocles, Euripides, and Aristophanes are closer to each other than they are to Aeschylus, despite the genre differences. One hypothesis for explaining these results is that Aeschylus (525-456) is of an older generation than the other three dramatists (Sophocles, 497-406; Euripides 489-406; Aristophanes, 446-386) and has a vocabulary peculiar to him as he is fond of forming his own words. Aristophanes too makes up his own words, but he though younger is still more of a contemporary of Sophocles and Euripides. Perhaps genre is not as important a factor in determining word use as age is and therefore perhaps genre differences between tragedy and comedy are not as distinct as generational differences are.

### Play Similarities

There are numerous things to notice about this graph. One is that the plays of Aeschylus’ Oresteia (Agamemnon, Libation Bearers, and Eumenides), the only extant trilogy, are comfortingly grouped very closely together, but the Prometheus Bound is nowhere near other plays by Aeschylus. Word frequency would suggest that the general scholarly view that the Prometheus Bound was not written by Aeschylus is correct. And indeed, if we look at a graph of just Aeschylus’ plays, the Prometheus Bound is the only one with a negative value.

Similarly, the Rhesus, considered not to be written by Euripides by many scholars, is an outlier compared to Euripides’ plays.

It is quite interesting that Sophocles has a closer affinity to Aristophanes than Euripides does as my instinct would be to say that Euripides, because his plays have more lower-class characters, would be closer to Aristophanes.

### Character Similarities

The goal of this project was to look at characterization and how we can use it as a way of exploring questions of genre. One comparison I thought would be interesting was to see whether the characters “Aeschylus” and “Euripides” from Aristophanes Frogs are similar to any of the characters from their respective plays. Does Aristophanes write the speeches of Aeschylus using the actual vocabulary Aeschylus uses? However, as the graph shows, “Aeschylus” and “Euripides” do not seem to share affinities with the plays written by Aeschylus and Euripides. However, another study should be done comparing “Aeschylus” and “Sophocles”with the characters themselves of their plays.
