import tensorflow as tf


def read_vocab(src, tgt):
    vocab_idx_src = tf.contrib.lookup.index_table_from_file(src, num_oov_buckets=1)
    vocab_idx_tgt = tf.contrib.lookup.index_table_from_file(tgt, num_oov_buckets=1)
    vocab_str_src = tf.contrib.lookup.index_to_string_table_from_file(src, default_value='<unk>')
    vocab_str_tgt = tf.contrib.lookup.index_to_string_table_from_file(tgt, default_value='<unk>')
    return vocab_idx_src, vocab_idx_tgt, vocab_str_src, vocab_str_tgt

def one_dataset_loader(src, tgt, hter, vocab_idx_src, vocab_idx_tgt, batch_size):
    src = tf.data.TextLineDataset(src)
    tgt = tf.data.TextLineDataset(tgt)
    hter = tf.data.TextLineDataset(hter)
    src = src.map(lambda string: tf.string_split([string]).values)
    tgt = tgt.map(lambda string: tf.string_split([string]).values)
    hter = hter.map(lambda x: tf.string_to_number(x))
    src = src.map(lambda tokens: vocab_idx_src.lookup(tokens))
    src_len = src.map(lambda tokens: tf.size(tokens))
    tgt = tgt.map(lambda tokens: vocab_idx_tgt.lookup(tokens))
    tgt_len = tgt.map(lambda tokens: tf.size(tokens))
    dataset = tf.data.Dataset.zip({
        "src": src,
        "src_len": src_len,
        "tgt": tgt,
        "tgt_len": tgt_len,
        "hter": hter
    })
    src_pad_id = vocab_idx_src.lookup(tf.constant('<pad>'))
    tgt_pad_id = vocab_idx_tgt.lookup(tf.constant('<pad>'))
    padded_shapes = {
        'src': tf.TensorShape([None]),
        'src_len': [],
        'tgt': tf.TensorShape([None]),
        'tgt_len': [],
        'hter': []
    }
    padding_values = {
        'src': src_pad_id,
        'src_len': tf.constant(0),
        'tgt': tgt_pad_id,
        'tgt_len': tf.constant(0),
        'hter': tf.constant(0.0)
    }
    dataset = dataset.shuffle(buffer_size=10000)
    dataset = dataset.padded_batch(batch_size, padded_shapes=padded_shapes, padding_values=padding_values)
    return dataset


def data_loader(vocab_idx_src, vocab_idx_tgt, args):
    train_dataset = one_dataset_loader(
        src=args.train[0],
        tgt=args.train[1],
        hter=args.train[2],
        vocab_idx_src=vocab_idx_src,
        vocab_idx_tgt=vocab_idx_tgt)
    dev_dataset = one_dataset_loader(
        src=args.dev[0],
        tgt=args.dev[1],
        hter=args.dev[2],
        vocab_idx_src=vocab_idx_src,
        vocab_idx_tgt=vocab_idx_tgt)
    return train_dataset, dev_dataset