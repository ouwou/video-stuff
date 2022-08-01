import av

def get_dims(frame_num, total_frames, w, h):
    frac = frame_num / total_frames
    return (int(frac * w) + 1, int(frac * h) + 1)

with av.open("output.webm", "w") as out:
    with av.open("source.mp4", "r") as container:
        audio = container.streams.audio[0]
        video = container.streams.video[0]
        total_frames = video.frames

        audio_stream = out.add_stream("libopus")
        video_stream = out.add_stream("vp8", rate=video.average_rate)
        video_stream.width = video.width
        video_stream.height = video.height
        video_stream.pix_fmt = "yuv420p"

        video_i = 0
        audio_i = 0
        for frame in container.decode():
            if isinstance(frame, av.VideoFrame):
                codec = av.CodecContext.create("vp8", mode="w")
                codec.pix_fmt = "yuv420p"
                codec.bit_rate = 500000
                if video_i == 0:
                    codec.width = video.width
                    codec.height = video.height
                else:
                    codec.width, codec.height = get_dims(video_i, total_frames, video.width, video.height)
                packets = codec.encode(frame)
                for packet in packets:
                    packet.stream = video_stream
                out.mux(packets)
                video_i += 1
            elif isinstance(frame, av.AudioFrame):
                out.mux(audio_stream.encode(frame))
                audio_i += 1
            print(f"{video_i}/{total_frames}V, {audio_i}A", end="\r")
        print()
