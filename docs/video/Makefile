.SECONDARY:

AWS_CLI ?= aws
DRAWIO ?= drawio
FFMPEG ?= ffmpeg

AWS_PROFILE ?= flyvercity

skydrone_video = s3://flyvercity.private/flights/skydrone_2023_08_16/2023-08-15_18-29-09.mkv
skydrone_video_local = downloads/video/$(notdir $(skydrone_video))

.deps-check:
	$(AWS_CLI) --version
	$(DRAWIO) --version
	$(FFMPEG) -version
	echo "Dependencies OK" > $@

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

$(skydrone_video_local):
	$(AWS_CLI) --profile $(AWS_PROFILE) s3 cp $(skydrone_video) $@

output/video/03-04-skydrone.mkv: $(skydrone_video_local)
	$(FFMPEG) -i $< -ss 00:00:20 -t 00:01:20 \
			  -y $@

fragments := output/slides/02-01.mp4 \
			 output/video/03-04-skydrone.mkv

video: .deps-check output/contents.txt $(fragments)
	$(FFMPEG) -safe 0 -f concat \
			  -i output/contents.txt \
			  -c:v libx264 -pix_fmt yuv420p \
			  -y output/video/deliverable.mp4
