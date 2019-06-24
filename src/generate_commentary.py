import json
import os

import encoder
import model
import numpy as np
import sample
import tensorflow as tf
import threading

from gfootball.env import football_env
from gfootball.env import config

from absl import app
from absl import flags
import pyttsx3
from commentary import Commentary

FLAGS = flags.FLAGS
flags.DEFINE_string(
    'home_players', 'keyboard',
    'Comma separated list of home players, single keyboard player by default')
flags.DEFINE_string('env_name', '11_vs_11_easy_stochastic', 'game difficulty')
flags.DEFINE_string('away_players', '', 'List of away players')
flags.DEFINE_string('level', '', 'Level to play')
flags.DEFINE_enum('action_set', 'full', ['default', 'full'], 'Action set')
flags.DEFINE_bool('real_time', True,
                  'If true, environment will slow down so humans can play.')


def threaded_inference(enc, prompt, sess, output, context):
    context_tokens = enc.encode(prompt)
    out = sess.run(output, feed_dict={context: [context_tokens for _ in range(1)]
                                      })[:, len(context_tokens):]
    text = enc.decode(out[0])
    print("=" * 80)
    print('prompt: ' + prompt)
    print('model o/p: ' + text)
    # print('model o/p: ' + str(text.strip().find('.')))
    print("=" * 80)
    tts_engine = pyttsx3.init()
    tts_engine.setProperty('voice', 'english')
    tts_engine.setProperty('rate', 130)
    tts_engine.say(text)
    tts_engine.runAndWait()


def main(_):
    cfg = config.Config({
        'env_name': FLAGS.env_name,
        'action_set': FLAGS.action_set,
        'away_players':
            FLAGS.away_players.split(',') if FLAGS.away_players else '',
        'dump_full_episodes': True,
        'home_players':
            FLAGS.home_players.split(',') if FLAGS.home_players else '',
        'real_time': FLAGS.real_time,
        'render': True
    })
    if FLAGS.level:
        cfg['level'] = FLAGS.level

    model_name = '345M'
    seed = None
    length = 80
    temperature = 1
    top_k = 0
    top_p = 0.0

    enc = encoder.get_encoder(model_name)
    hparams = model.default_hparams()
    with open(os.path.join('models', model_name, 'hparams.json')) as f:
        hparams.override_from_dict(json.load(f))
    gpu_options = tf.GPUOptions(allow_growth=True)
    with tf.Session(graph=tf.Graph(), config=tf.ConfigProto(gpu_options=gpu_options)) as sess:
        context = tf.placeholder(tf.int32, [1, None])
        np.random.seed(seed)
        tf.set_random_seed(seed)
        output = sample.sample_sequence(
            hparams=hparams, length=length,
            context=context,
            batch_size=1,
            temperature=temperature, top_k=top_k, top_p=top_p
        )

        saver = tf.train.Saver()
        ckpt = tf.train.latest_checkpoint(os.path.join('models', model_name))
        saver.restore(sess, ckpt)

        context_tokens = enc.encode('initializing')
        out = sess.run(output, feed_dict={context: [context_tokens for _ in range(1)]
                                          })[:, len(context_tokens):]
        enc.decode(out[0])

        env = football_env.FootballEnv(cfg)
        env.reset(cfg)
        commentary = Commentary()
        try:
            prompt = 'initializing'
            commentary_thread = threading.Thread(target=threaded_inference,
                                                 args=(enc, prompt, sess, output, context))

            while True:
                observation, reward, done, info = env.step(None)
                prompt, interrupt_current_commentary = commentary.process_observation(observation)
                if prompt:
                    if commentary_thread.is_alive():
                        if interrupt_current_commentary:
                            # commentary_thread kill/stop
                            # commentary_thread.start()
                            print('thread alive')
                    else:
                        commentary_thread = threading.Thread(target=threaded_inference,
                                                             args=(enc, prompt, sess, output, context))
                        commentary_thread.start()
                if done:
                    env.reset()
        except KeyboardInterrupt:
            env.write_dump('shutdown')
            exit(1)


if __name__ == '__main__':
    app.run(main)
