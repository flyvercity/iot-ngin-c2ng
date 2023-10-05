.SECONDARY:

PYTHON3 ?= python
AWS_CLI ?= aws
DRAWIO ?= drawio
FFMPEG ?= ffmpeg

AWS_PROFILE ?= flyvercity

framerate = 30

gen_videos_path = s3://flyvercity.private/gen-videos/iot-ngin-c2ng/xcoded

signal_overlay_s3 = s3://flyvercity.private/flights/skydrone_2023_08_16/converted/03-04.overlay.gif
signal_overlay = downloads/gif/03-04.overlay.gif


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

downloads/gif/03-04.overlay.gif:
	$(PYTHON3) mkdir.py $(dir $@)
	$(AWS_CLI) --profile $(AWS_PROFILE) s3 cp $(signal_overlay_s3) $@

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


output/images/04-02.png: src/images/04-02.xcf
	$(PYTHON3) mkdir.py $(dir $@)
	echo "Please use GIMP to produce $@ from $<" && exit 1


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
			  -ar 48000 -ac 2 \
			  -r $(framerate) \
			  -y $@


# Skydrone video

output/video/03-04.mp4: downloads/video/03-04.mp4 output/audio/03-04.mp3 $(signal_overlay)
	$(PYTHON3) mkdir.py $(dir $@)
	$(FFMPEG) -i downloads/video/03-04.mp4 \
			  -stream_loop -1 -i $(signal_overlay) \
			  -i output/audio/03-04.mp3 \
			  -filter_complex " \
				[0:v] trim=start=40:end=90,setpts=PTS-STARTPTS [cut], \
				[cut] scale=1280:720 [back], \
				[1:v] scale=640:480 [ovrl], \
				[back][ovrl] overlay=320:120:enable='between(t,30,65):shortest=1' \
			  " \
			  -ar 48000 -ac 2 \
			  -r $(framerate) \
			  -y $@


# Pre-recorded video

output/video/05-00.mp4: downloads/video/05-00.mp4
	$(PYTHON3) mkdir.py $(dir $@)
	$(FFMPEG) -i $< \
			  -vf scale=1280:720 \
			  -ar 48000 -ac 2 \
			  -r $(framerate) \
			  -y $@
