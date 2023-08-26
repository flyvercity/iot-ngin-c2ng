.SECONDARY:

PYTHON3 ?= python
AWS_CLI ?= aws
DRAWIO ?= drawio
FFMPEG ?= ffmpeg

AWS_PROFILE ?= flyvercity

framerate = 30

gen_videos_path = s3://flyvercity.private/gen-videos/iot-ngin-c2ng/xcoded
signal_overlay = src/images/skydrone-20m.png


# Checking dependencies

.deps-check:
	$(PYTHON3) --version
	$(AWS_CLI) --version
	$(DRAWIO) --version
	$(FFMPEG) -version
	echo "Dependencies OK" > $@


# Fetching data from S3

downloads/video/%.mp4:
	$(PYTHON3) mkdir.py $(dir $@)
	$(AWS_CLI) --profile $(AWS_PROFILE) s3 cp $(gen_videos_path)/$(notdir $@) $@

upsync:
	$(AWS_CLI) --profile $(AWS_PROFILE) s3 sync downloads/video/ s3://flyvercity.private/gen-videos/iot-ngin-c2ng/xcoded

# Generic generation

output/audio/%.mp3: src/speech/%.ssml
	$(PYTHON3) mkdir.py $(dir $@)
	$(AWS_CLI) --profile $(AWS_PROFILE) polly synthesize-speech \
		--engine neural \
		--output-format mp3 \
		--voice-id Stephen \
		--text-type ssml \
		--text file://$< \
		$@

output/images/%.png: src/drawings/%.drawio
	$(PYTHON3) mkdir.py $(dir $@)
	$(DRAWIO) --export --width 1920 --height 1080 --output $@ $<


# Static slides with narration

output/slides/%.mp4: output/audio/%.mp3 output/images/%.png
	$(PYTHON3) mkdir.py $(dir $@)
	$(FFMPEG) -r $(framerate) -loop 1 \
			  -i output/images/$*.png \
		      -i output/audio/$*.mp3 \
			   -shortest -fflags +shortest -max_interleave_delta 100M  \
			  -vf scale=1280:720 \
			  -y $@

# Generic video with narration

output/nvideo/%.mp4: downloads/video/%.mp4 output/audio/%.mp3
	$(PYTHON3) mkdir.py $(dir $@)
	$(FFMPEG) -i downloads/video/$*.mp4 \
		      -i output/audio/$*.mp3 \
			  -map 0:v:0 -map 1:a:0 \
			  -vf scale=1280:720 \
			  -y $@


# Intro video

output/video/01-04.mp4: output/audio/01-04.mp3 \
						downloads/video/01-04.mp4 \
						src/images/01-04.overlay.png
	$(PYTHON3) mkdir.py $(dir $@)
	$(FFMPEG) -i downloads/video/01-04.mp4 \
		      -i output/audio/01-04.mp3 \
			  -i src/images/01-04.overlay.png \
			  -filter_complex " \
			  	[0:v]scale=1280:720 [back], \
				[2:v]scale=1280:720 [ovrl], \
				[back][ovrl] overlay=0:0' \
			  " \
			  -y $@


# Skydrone video

output/video/03-04.mp4: downloads/video/03-04.mp4 output/audio/03-04.mp3 $(signal_overlay)
	$(PYTHON3) mkdir.py $(dir $@)
	$(FFMPEG) -i downloads/video/03-04.mp4 \
			  -i $(signal_overlay) \
			  -i output/audio/03-04.mp3 \
			  -filter_complex " \
				[0:v] trim=start=20:end=90,setpts=PTS-STARTPTS [cut], \
				[1:v] scale=640:480 [ovrl], \
				[cut][ovrl] overlay=50:50:enable='between(t,45,80)' \
			  " \
			  -y $@

# Complete video

fragments := output/nvideo/01-01.mp4 \
			 output/nvideo/01-02.mp4 \
			 output/nvideo/01-03.mp4 \
			 output/video/01-04.mp4 \
			 output/slides/02-01.mp4 \
			 output/slides/02-02.mp4 \
			 output/slides/02-03.mp4 \
			 output/slides/02-04.mp4 \
			 output/slides/02-05.mp4 \
			 output/slides/03-01.mp4 \
			 output/video/03-04.mp4 \
			 output/slides/04-01.mp4 \
			 output/nvideo/04-04.mp4 \
			 output/nvideo/04-05.mp4 \
			 output/nvideo/04-06.mp4 \

output/contents.txt:
	$(PYTHON3) mkdir.py $(dir $@)
	$(PYTHON3) gen_contents.py $(fragments) > $@

video: .deps-check output/contents.txt $(fragments)
	$(FFMPEG) -safe 0 -r $(framerate) -f concat \
			  -i output/contents.txt \
			  -y output/video/deliverable.mp4
