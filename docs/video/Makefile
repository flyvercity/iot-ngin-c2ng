.SECONDARY:

DRAWIO ?= drawio
FFMPEG ?= ffmpeg
AWS_PROFILE ?= flyvercity

deps-check:
	$(DRAWIO) --version
	$(FFMPEG) -version

output/audio/%.mp3: src/speech/%.ssml
	aws --profile $(AWS_PROFILE) polly synthesize-speech \
		--output-format mp3 \
		--voice-id Matthew \
		--text-type ssml \
		--text file://$< \
		$@

output/images/%.png: src/drawings/%.drawio
	$(DRAWIO) --export --width 1920 --height 1080 --output $@ $<

output/slides/%.mp4: output/audio/%.mp3 output/images/%.png
	$(FFMPEG) -r 1 \
			  -loop 1 -i output/images/$*.png \
		      -i output/audio/$*.mp3 -acodec copy \
			  -shortest -vf scale=1280:720 \
			  -y $@

video: output/slides/03-01.mp4
