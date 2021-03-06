import tensorflow as tf
import pickle

# Sentence to be translated

translate_sentence = 'he saw a old yellow truck .'

batch_size = 128


# Load preprocessed data

def load_preprocess():
    """
    Load the Preprocessed Training data and return them in batches of <batch_size> or less
    """

    with open('preprocess.p', mode='rb') as in_file:
        return pickle.load(in_file)


# Load parameters

def load_params():
    """
    Load parameters from file
    """

    with open('params.p', mode='rb') as in_file:
        return pickle.load(in_file)


# Preprocess new sentence

def sentence_to_seq(sentence, vocab_to_int):
    """
    Convert a sentence to a sequence of ids
    :param sentence: String
    :param vocab_to_int: Dictionary to go from the words to an id
    :return: List of word ids
    """

    sentence_lower = sentence.lower()
    sentence_ids = []

    for word in sentence_lower.split():
        if word in vocab_to_int.keys():
            sentence_ids.append(vocab_to_int[word])
        else:
            sentence_ids.append(vocab_to_int['<UNK>'])

    return sentence_ids


# Load data

print('Loading preprocessed data and parameters...')

_, (source_vocab_to_int,
    target_vocab_to_int), (source_int_to_vocab,
                           target_int_to_vocab) = load_preprocess()

load_path = load_params()


# Translate

print('Translating...')

translate_sentence = sentence_to_seq(translate_sentence, source_vocab_to_int)

loaded_graph = tf.Graph()

with tf.Session(graph=loaded_graph) as sess:
    # Load saved model
    loader = tf.train.import_meta_graph(load_path + '.meta')
    loader.restore(sess, load_path)

    input_data = loaded_graph.get_tensor_by_name('input:0')
    logits = loaded_graph.get_tensor_by_name('predictions:0')
    target_sequence_length = loaded_graph.get_tensor_by_name('target_sequence_length:0')
    source_sequence_length = loaded_graph.get_tensor_by_name('source_sequence_length:0')
    keep_prob = loaded_graph.get_tensor_by_name('keep_prob:0')

    translate_logits = sess.run(logits, {input_data: [translate_sentence]*batch_size,
                                         target_sequence_length: [len(translate_sentence)*2]*batch_size,
                                         source_sequence_length: [len(translate_sentence)]*batch_size,
                                         keep_prob: 1.0})[0]

print('Input')
print('  Word Ids:      {}'.format([i for i in translate_sentence]))
print('  English Words: {}'.format([source_int_to_vocab[i] for i in translate_sentence]))

print('\nPrediction')
print('  Word Ids:      {}'.format([i for i in translate_logits]))
print('  French Words: {}'.format(" ".join([target_int_to_vocab[i] for i in translate_logits])))
