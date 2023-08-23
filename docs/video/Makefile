.SECONDARY:

PYTHON3 ?= python
AWS_CLI ?= aws
DRAWIO ?= drawio
FFMPEG ?= ffmpeg

AWS_PROFILE ?= flyvercity

framerate = 30

skydrone_video = s3://flyvercity.private/flights/skydrone_2023_08_16/2023-08-15_18-29-09.mkv
skydrone_video_local = downloads/video/$(notdir $(skydrone_video))
signal_overlay = src/images/skydrone-20m.png

.deps-check:
	$(PYTHON3) --version
	$(AWS_CLI) --version
	$(DRAWIO) --version
	$(FFMPEG) -version
	echo "Dependencies OK" > $@


output/audio/%.mp3: src/speech/%.ssml
	$(PYTHON3) mkdir.py $(dir $@)
	$(AWS_CLI) --profile $(AWS_PROFILE) polly synthesize-speech \
		--engine neural \
		--output-format mp3 \
		--voice-id Matthew \
		--text-type ssml \
		--text file://$< \
		$@

output/images/%.png: src/drawings/%.drawio
	$(PYTHON3) mkdir.py $(dir $@)
	$(DRAWIO) --export --width 1920 --height 1080 --output $@ $<

output/slides/%.mp4: output/audio/%.mp3 output/images/%.png
	$(PYTHON3) mkdir.py $(dir $@)
	$(FFMPEG) -r $(framerate) -loop 1 \
			  -i output/images/$*.png \
		      -i output/audio/$*.mp3 \
			   -shortest -fflags +shortest -max_interleave_delta 100M  \
			  -vf scale=1280:720 \
			  -y $@

$(skydrone_video_local):
	$(PYTHON3) mkdir.py $(dir $@)
	$(AWS_CLI) --profile $(AWS_PROFILE) s3 cp $(skydrone_video) $@

output/video/03-04-skydrone.mp4: $(skydrone_video_local)
	$(PYTHON3) mkdir.py $(dir $@)
	$(FFMPEG) -r $(framerate) \
			  -i $< \
			     -ss 00:00:20 -t 00:01:20 \
			  -y $@

output/video/03-04-skydrone-over.mp4: output/video/03-04-skydrone.mp4
	$(PYTHON3) mkdir.py $(dir $@)
	$(FFMPEG) -r $(framerate) \
			  -i output/video/03-04-skydrone.mp4 \
			  -i $(signal_overlay) \
			     -filter_complex " \
				 	[1:v]scale=640:480 [ovrl], \
				 	[0:v][ovrl] overlay=50:50:enable='between(t,45,80)' \
			     " \
			  -y $@

output/video/03-04-skydrone-aud.mp4: output/video/03-04-skydrone-over.mp4 output/audio/03-04.mp3
	$(PYTHON3) mkdir.py $(dir $@)
	$(FFMPEG) -i output/video/03-04-skydrone-over.mp4 \
			  -i output/audio/03-04.mp3 \
			  -vf scale=1280:720 \
			  -y $@

fragments := output/slides/02-01.mp4 \
			 output/slides/02-02.mp4 \
			 output/slides/02-03.mp4 \
			 output/slides/02-04.mp4 \
			 output/slides/03-01.mp4 \
			 output/video/03-04-skydrone-aud.mp4

output/contents.txt:
	$(PYTHON3) mkdir.py $(dir $@)
	$(PYTHON3) gen_contents.py $(fragments) > $@

video: .deps-check output/contents.txt $(fragments)
	$(FFMPEG) -safe 0 -r $(framerate) -f concat \
			  -i output/contents.txt \
			  -y output/video/deliverable.mp4
