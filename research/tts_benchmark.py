"""Synthetic qualification fixture only: no news, publishing, secrets or APIs."""
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import resource
import subprocess
import time
import urllib.request

import numpy as np
import onnxruntime as ort
import soundfile as sf
from kokoro_onnx import Kokoro

started = time.monotonic()
assets = {}
for name in ('kokoro-v1.0.int8.onnx', 'voices-v1.0.bin'):
    url = 'https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/' + name
    urllib.request.urlretrieve(url, name)
    assets[name] = hashlib.sha256(Path(name).read_bytes()).hexdigest()
options = ort.SessionOptions()
options.intra_op_num_threads = 4
options.inter_op_num_threads = 1
session = ort.InferenceSession('kokoro-v1.0.int8.onnx', sess_options=options, providers=['CPUExecutionProvider'])
engine = Kokoro.from_session(session, 'voices-v1.0.bin')
paragraphs = []
topics = ('research methods', 'model evaluations', 'data centers', 'open weights', 'industrial robots', 'software engineering', 'regional languages', 'enterprise security')
for index in range(42):
    paragraphs.append(
        f'This is synthetic audio qualification section {index + 1}, about {topics[index % len(topics)]}. '
        'It is not a news report. A daily briefing should distinguish a confirmed announcement from a prediction. '
        'The narration must preserve names, numbers, punctuation, and complete sentences. '
        'OpenAI, NVIDIA, Anthropic, and Google are pronunciation examples. '
        'A figure of twenty percent differs from two percent. The report date follows Berlin time. '
        'This section ends here.'
    )
script = '\n\n'.join(paragraphs)
assert len(script) >= 16612
Path('results').mkdir()
synth_start = time.monotonic()
sample_count = 0
with sf.SoundFile('fixture.wav', mode='w', samplerate=24000, channels=1, subtype='PCM_16') as out:
    for index, paragraph in enumerate(paragraphs):
        samples, rate = engine.create(paragraph, voice='af_heart', speed=1.0, lang='en-us')
        assert rate == 24000 and np.isfinite(samples).all() and len(samples) > 0
        out.write(samples)
        sample_count += len(samples)
        print(json.dumps({'chunk': index + 1, 'audio_seconds': round(sample_count / rate, 2), 'synthesis_seconds': round(time.monotonic() - synth_start, 2)}), flush=True)
synthesis_seconds = time.monotonic() - synth_start
subprocess.run(['ffmpeg', '-v', 'error', '-i', 'fixture.wav', '-ac', '1', '-ar', '44100', '-b:a', '128k', 'fixture.mp3'], check=True)
subprocess.run(['ffmpeg', '-v', 'error', '-xerror', '-i', 'fixture.mp3', '-f', 'null', '-'], check=True)
probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', 'fixture.mp3']))
stream = probe['streams'][0]
assert stream['codec_name'] == 'mp3' and stream['sample_rate'] == '44100' and stream['channels'] == 1
assert int(stream['bit_rate']) == 128000
subprocess.run(['ffmpeg', '-v', 'error', '-i', 'fixture.mp3', '-t', '45', '-c', 'copy', 'results/sample.mp3'], check=True)
report = dict(fixture='synthetic; not a news report or a production edition', characters=len(script), words=len(script.split()), chunks=len(paragraphs), audio_seconds=sample_count/24000, synthesis_seconds=synthesis_seconds, total_seconds=time.monotonic()-started, real_time_factor=synthesis_seconds/(sample_count/24000), max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss, cpu_count=os.cpu_count(), providers=session.get_providers(), mp3_bytes=Path('fixture.mp3').stat().st_size, full_decode='passed', codec=stream['codec_name'], sample_rate=stream['sample_rate'], channels=stream['channels'], bit_rate=stream['bit_rate'], assets_sha256=assets, packages={name: importlib.metadata.version(name) for name in ('kokoro-onnx','onnxruntime','numpy','soundfile')})
Path('results/report.json').write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps(report, indent=2), flush=True)
with open(os.environ['GITHUB_STEP_SUMMARY'], 'a') as out:
    out.write('Synthetic full-length CPU TTS qualification; no inference API or deployment.\n\n```json\n'+json.dumps(report, indent=2)+'\n```\n')
