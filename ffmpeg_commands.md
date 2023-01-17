# Concatinate all mp3 files

	ffmpeg -i "concat:1.mp3|2.mp3|3.mp3|4.mp3|5.mp3|6.mp3|7.mp3|8.mp3|9.mp3|10.mp3|11.mp3|12.mp3" -map 0:a:0 -acodec  copy -b:a 32k  full.mp3

# Downsample
	ffmpeg -i full.mp3 -ac 1 -ab 64000 -ar 22050 out.mp3
