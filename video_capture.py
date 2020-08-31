import os
import cv2
import threading


class VideoCapture(threading.Thread):
    def __init__(self, videoPath, output_path, start_time=0, end_time=None, time_interval=1, output_prefix=None,
                 quality=100):
        super().__init__()
        self._video_path = videoPath
        self._output_path = output_path
        self._time_interval = time_interval
        self._output_prefix = output_prefix
        self._quality = quality
        self._start_time = start_time
        if end_time is not None:
            self._end_time = end_time
        else:
            self._end_time = None

    def __capture__(self):
        cap = cv2.VideoCapture(self._video_path)  # 打开视频文件
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))  # 视频的帧数
        fps = cap.get(cv2.CAP_PROP_FPS)  # 视频的帧率
        duration = total_frames / fps  # 视频的时间

        try:
            os.mkdir(self._output_path)
        except OSError:
            pass
        print('Capturing video frames...')
        prefix = ''
        if self._output_prefix is not None:
            prefix = self._output_path + '_'

        if self._end_time is not None:
            N = (self._end_time - self._start_time) / self._time_interval + 1
            success = True
            count = 0
            while success and count < N:
                cap.set(cv2.CAP_PROP_POS_MSEC, (1000 *
                                                self._start_time + count * 1000 * self._time_interval))
                success, image = cap.read()
                if success:
                    print(f'Capture {count + 1}.')
                    cv2.imwrite(os.path.join(self._output_path, f"{prefix}{count + 1}.jpg"), image,
                                [int(cv2.IMWRITE_JPEG_QUALITY), self._quality])  # save frame as JPEG file
                    count = count + 1
        else:
            success = True
            count = 0
            while success:
                cap.set(cv2.CAP_PROP_POS_MSEC, (1000 *
                                                self._start_time + count * 1000 * self._time_interval))
                success, image = cap.read()
                if success:
                    print(f'Capture {count + 1}.')
                    cv2.imwrite(os.path.join(self._output_path, f"{prefix}{count + 1}.jpg"), image,
                                [int(cv2.IMWRITE_JPEG_QUALITY), self._quality])  # save frame as JPEG file
                    count = count + 1
        cap.release()

    def run(self):
        self.__capture__()


if __name__ == '__main__':
    VideoCapture(videoPath='video/中国房价的未来终于明朗-5分钟看懂房子能不能买-.mp4',
                 output_path='image/', time_interval=10).run()
