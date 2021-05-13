# import io
# import os
# import sys
# import subprocess
# import wave
# import aifc
# import math
# import audioop
# import collections
# import json
# import base64
# import threading
# import platform
# import stat
# import hashlib
# import hmac
# import time
# import uuid

# from urllib.parse import urlencode
# from urllib.request import Request, urlopen
# from urllib.error import URLError, HTTPError

# # class WaitTimeoutError(Exception): pass


# # class RequestError(Exception): pass


# # class UnknownValueError(Exception): pass


# # class AudioSource(object):
# #     def __init__(self):
# #         raise NotImplementedError("this is an abstract class")

# #     def __enter__(self):
# #         raise NotImplementedError("this is an abstract class")

# #     def __exit__(self, exc_type, exc_value, traceback):
# #         raise NotImplementedError("this is an abstract class")

# # class Microphone(AudioSource):
# #     """
# #     Creates a new ``Microphone`` instance, which represents a physical microphone on the computer. Subclass of ``AudioSource``.
# #     This will throw an ``AttributeError`` if you don't have PyAudio 0.2.11 or later installed.
# #     If ``device_index`` is unspecified or ``None``, the default microphone is used as the audio source. Otherwise, ``device_index`` should be the index of the device to use for audio input.
# #     A device index is an integer between 0 and ``pyaudio.get_device_count() - 1`` (assume we have used ``import pyaudio`` beforehand) inclusive. It represents an audio device such as a microphone or speaker. See the `PyAudio documentation <http://people.csail.mit.edu/hubert/pyaudio/docs/>`__ for more details.
# #     The microphone audio is recorded in chunks of ``chunk_size`` samples, at a rate of ``sample_rate`` samples per second (Hertz). If not specified, the value of ``sample_rate`` is determined automatically from the system's microphone settings.
# #     Higher ``sample_rate`` values result in better audio quality, but also more bandwidth (and therefore, slower recognition). Additionally, some CPUs, such as those in older Raspberry Pi models, can't keep up if this value is too high.
# #     Higher ``chunk_size`` values help avoid triggering on rapidly changing ambient noise, but also makes detection less sensitive. This value, generally, should be left at its default.
# #     """
# #     def __init__(self, device_index=None, sample_rate=None, chunk_size=1024):
# #         assert device_index is None or isinstance(device_index, int), "Device index must be None or an integer"
# #         assert sample_rate is None or (isinstance(sample_rate, int) and sample_rate > 0), "Sample rate must be None or a positive integer"
# #         assert isinstance(chunk_size, int) and chunk_size > 0, "Chunk size must be a positive integer"

# #         # set up PyAudio
# #         self.pyaudio_module = self.get_pyaudio()
# #         audio = self.pyaudio_module.PyAudio()
# #         try:
# #             count = audio.get_device_count()  # obtain device count
# #             if device_index is not None:  # ensure device index is in range
# #                 assert 0 <= device_index < count, "Device index out of range ({} devices available; device index should be between 0 and {} inclusive)".format(count, count - 1)
# #             if sample_rate is None:  # automatically set the sample rate to the hardware's default sample rate if not specified
# #                 device_info = audio.get_device_info_by_index(device_index) if device_index is not None else audio.get_default_input_device_info()
# #                 assert isinstance(device_info.get("defaultSampleRate"), (float, int)) and device_info["defaultSampleRate"] > 0, "Invalid device info returned from PyAudio: {}".format(device_info)
# #                 sample_rate = int(device_info["defaultSampleRate"])
# #         finally:
# #             audio.terminate()

# #         self.device_index = device_index
# #         self.format = self.pyaudio_module.paInt16  # 16-bit int sampling
# #         self.SAMPLE_WIDTH = self.pyaudio_module.get_sample_size(self.format)  # size of each sample
# #         self.SAMPLE_RATE = sample_rate  # sampling rate in Hertz
# #         self.CHUNK = chunk_size  # number of frames stored in each buffer

# #         self.audio = None
# #         self.stream = None

# class Recognizer(AudioSource):
#     def __init__(self):
#         """
#         Creates a new ``Recognizer`` instance, which represents a collection of speech recognition functionality.
#         """
#         self.energy_threshold = 300  # minimum audio energy to consider for recording
#         self.dynamic_energy_threshold = True
#         self.dynamic_energy_adjustment_damping = 0.15
#         self.dynamic_energy_ratio = 1.5
#         self.pause_threshold = 0.8  # seconds of non-speaking audio before a phrase is considered complete
#         self.operation_timeout = None  # seconds after an internal operation (e.g., an API request) starts before it times out, or ``None`` for no timeout

#         self.phrase_threshold = 0.3  # minimum seconds of speaking audio before we consider the speaking audio a phrase - values below this are ignored (for filtering out clicks and pops)
#         self.non_speaking_duration = 0.5  # seconds of non-speaking audio to keep on both sides of the recording

#     def adjust_for_ambient_noise(self, source, duration=1):
#         """
#         Adjusts the energy threshold dynamically using audio from ``source`` (an ``AudioSource`` instance) to account for ambient noise.
#         Intended to calibrate the energy threshold with the ambient energy level. Should be used on periods of audio without speech - will stop early if any speech is detected.
#         The ``duration`` parameter is the maximum number of seconds that it will dynamically adjust the threshold for before returning. This value should be at least 0.5 in order to get a representative sample of the ambient noise.
#         """
#         assert isinstance(source, AudioSource), "Source must be an audio source"
#         assert source.stream is not None, "Audio source must be entered before adjusting, see documentation for ``AudioSource``; are you using ``source`` outside of a ``with`` statement?"
#         assert self.pause_threshold >= self.non_speaking_duration >= 0

#         seconds_per_buffer = (source.CHUNK + 0.0) / source.SAMPLE_RATE
#         elapsed_time = 0

#         # adjust energy threshold until a phrase starts
#         while True:
#             elapsed_time += seconds_per_buffer
#             if elapsed_time > duration: break
#             buffer = source.stream.read(source.CHUNK)
#             energy = audioop.rms(buffer, source.SAMPLE_WIDTH)  # energy of the audio signal

#             # dynamically adjust the energy threshold using asymmetric weighted average
#             damping = self.dynamic_energy_adjustment_damping ** seconds_per_buffer  # account for different chunk sizes and rates
#             target_energy = energy * self.dynamic_energy_ratio
#             self.energy_threshold = self.energy_threshold * damping + target_energy * (1 - damping)
    
#     def listen(self, source, timeout=None, phrase_time_limit=None, snowboy_configuration=None):
#         """
#         Records a single phrase from ``source`` (an ``AudioSource`` instance) into an ``AudioData`` instance, which it returns.
#         This is done by waiting until the audio has an energy above ``recognizer_instance.energy_threshold`` (the user has started speaking), and then recording until it encounters ``recognizer_instance.pause_threshold`` seconds of non-speaking or there is no more audio input. The ending silence is not included.
#         The ``timeout`` parameter is the maximum number of seconds that this will wait for a phrase to start before giving up and throwing an ``speech_recognition.WaitTimeoutError`` exception. If ``timeout`` is ``None``, there will be no wait timeout.
#         The ``phrase_time_limit`` parameter is the maximum number of seconds that this will allow a phrase to continue before stopping and returning the part of the phrase processed before the time limit was reached. The resulting audio will be the phrase cut off at the time limit. If ``phrase_timeout`` is ``None``, there will be no phrase time limit.
#         The ``snowboy_configuration`` parameter allows integration with `Snowboy <https://snowboy.kitt.ai/>`__, an offline, high-accuracy, power-efficient hotword recognition engine. When used, this function will pause until Snowboy detects a hotword, after which it will unpause. This parameter should either be ``None`` to turn off Snowboy support, or a tuple of the form ``(SNOWBOY_LOCATION, LIST_OF_HOT_WORD_FILES)``, where ``SNOWBOY_LOCATION`` is the path to the Snowboy root directory, and ``LIST_OF_HOT_WORD_FILES`` is a list of paths to Snowboy hotword configuration files (`*.pmdl` or `*.umdl` format).
#         This operation will always complete within ``timeout + phrase_timeout`` seconds if both are numbers, either by returning the audio data, or by raising a ``speech_recognition.WaitTimeoutError`` exception.
#         """
#         assert isinstance(source, AudioSource), "Source must be an audio source"
#         assert source.stream is not None, "Audio source must be entered before listening, see documentation for ``AudioSource``; are you using ``source`` outside of a ``with`` statement?"
#         assert self.pause_threshold >= self.non_speaking_duration >= 0
#         if snowboy_configuration is not None:
#             assert os.path.isfile(os.path.join(snowboy_configuration[0], "snowboydetect.py")), "``snowboy_configuration[0]`` must be a Snowboy root directory containing ``snowboydetect.py``"
#             for hot_word_file in snowboy_configuration[1]:
#                 assert os.path.isfile(hot_word_file), "``snowboy_configuration[1]`` must be a list of Snowboy hot word configuration files"

#         seconds_per_buffer = float(source.CHUNK) / source.SAMPLE_RATE
#         pause_buffer_count = int(math.ceil(self.pause_threshold / seconds_per_buffer))  # number of buffers of non-speaking audio during a phrase, before the phrase should be considered complete
#         phrase_buffer_count = int(math.ceil(self.phrase_threshold / seconds_per_buffer))  # minimum number of buffers of speaking audio before we consider the speaking audio a phrase
#         non_speaking_buffer_count = int(math.ceil(self.non_speaking_duration / seconds_per_buffer))  # maximum number of buffers of non-speaking audio to retain before and after a phrase

#         # read audio input for phrases until there is a phrase that is long enough
#         elapsed_time = 0  # number of seconds of audio read
#         buffer = b""  # an empty buffer means that the stream has ended and there is no data left to read
#         while True:
#             frames = collections.deque()

#             if snowboy_configuration is None:
#                 # store audio input until the phrase starts
#                 while True:
#                     # handle waiting too long for phrase by raising an exception
#                     elapsed_time += seconds_per_buffer
#                     if timeout and elapsed_time > timeout:
#                         raise WaitTimeoutError("listening timed out while waiting for phrase to start")

#                     buffer = source.stream.read(source.CHUNK)
#                     if len(buffer) == 0: break  # reached end of the stream
#                     frames.append(buffer)
#                     if len(frames) > non_speaking_buffer_count:  # ensure we only keep the needed amount of non-speaking buffers
#                         frames.popleft()

#                     # detect whether speaking has started on audio input
#                     energy = audioop.rms(buffer, source.SAMPLE_WIDTH)  # energy of the audio signal
#                     if energy > self.energy_threshold: break

#                     # dynamically adjust the energy threshold using asymmetric weighted average
#                     if self.dynamic_energy_threshold:
#                         damping = self.dynamic_energy_adjustment_damping ** seconds_per_buffer  # account for different chunk sizes and rates
#                         target_energy = energy * self.dynamic_energy_ratio
#                         self.energy_threshold = self.energy_threshold * damping + target_energy * (1 - damping)
#             else:
#                 # read audio input until the hotword is said
#                 snowboy_location, snowboy_hot_word_files = snowboy_configuration
#                 buffer, delta_time = self.snowboy_wait_for_hot_word(snowboy_location, snowboy_hot_word_files, source, timeout)
#                 elapsed_time += delta_time
#                 if len(buffer) == 0: break  # reached end of the stream
#                 frames.append(buffer)

#             # read audio input until the phrase ends
#             pause_count, phrase_count = 0, 0
#             phrase_start_time = elapsed_time
#             while True:
#                 # handle phrase being too long by cutting off the audio
#                 elapsed_time += seconds_per_buffer
#                 if phrase_time_limit and elapsed_time - phrase_start_time > phrase_time_limit:
#                     break

#                 buffer = source.stream.read(source.CHUNK)
#                 if len(buffer) == 0: break  # reached end of the stream
#                 frames.append(buffer)
#                 phrase_count += 1

#                 # check if speaking has stopped for longer than the pause threshold on the audio input
#                 energy = audioop.rms(buffer, source.SAMPLE_WIDTH)  # unit energy of the audio signal within the buffer
#                 if energy > self.energy_threshold:
#                     pause_count = 0
#                 else:
#                     pause_count += 1
#                 if pause_count > pause_buffer_count:  # end of the phrase
#                     break

#             # check how long the detected phrase is, and retry listening if the phrase is too short
#             phrase_count -= pause_count  # exclude the buffers for the pause before the phrase
#             if phrase_count >= phrase_buffer_count or len(buffer) == 0: break  # phrase is long enough or we've reached the end of the stream, so stop listening

#         # obtain frame data
#         for i in range(pause_count - non_speaking_buffer_count): frames.pop()  # remove extra non-speaking frames at the end
#         frame_data = b"".join(frames)

#         return AudioData(frame_data, source.SAMPLE_RATE, source.SAMPLE_WIDTH)

import queue
q = queue.Queue()
try:
    t = q.get_nowait()
    print(t)
except Exception as e:
    pass