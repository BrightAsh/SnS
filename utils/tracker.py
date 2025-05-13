import numpy as np
from scipy.spatial import distance as dist
from collections import OrderedDict


class CentroidTracker:
    def __init__(self, max_disappeared=5, max_distance=50):
        self.next_object_id = 0
        self.objects = OrderedDict()         # {id: (cx, cy)}
        self.disappeared = OrderedDict()     # {id: count}

        self.max_disappeared = max_disappeared
        self.max_distance = max_distance

    def register(self, centroid):
        self.objects[self.next_object_id] = centroid
        self.disappeared[self.next_object_id] = 0
        self.next_object_id += 1

    def deregister(self, object_id):
        del self.objects[object_id]
        del self.disappeared[object_id]

    def update(self, detections):
        # 입력이 없으면 모두 사라졌다고 판단
        if len(detections) == 0:
            for object_id in list(self.disappeared.keys()):
                self.disappeared[object_id] += 1
                if self.disappeared[object_id] > self.max_disappeared:
                    self.deregister(object_id)
            return self.objects

        input_centroids = np.zeros((len(detections), 2), dtype="int")

        for (i, det) in enumerate(detections):
            x1, y1, x2, y2 = det["bbox"]
            cx = int((x1 + x2) / 2.0)
            cy = int((y1 + y2) / 2.0)
            input_centroids[i] = (cx, cy)

        # 트래킹 초기 상태
        if len(self.objects) == 0:
            for i in range(len(input_centroids)):
                self.register(input_centroids[i])
        else:
            object_ids = list(self.objects.keys())
            object_centroids = list(self.objects.values())

            D = dist.cdist(np.array(object_centroids), input_centroids)
            rows = D.min(axis=1).argsort()
            cols = D.argmin(axis=1)[rows]

            used_rows, used_cols = set(), set()

            for (row, col) in zip(rows, cols):
                if row in used_rows or col in used_cols:
                    continue
                if D[row, col] > self.max_distance:
                    continue

                object_id = object_ids[row]
                self.objects[object_id] = input_centroids[col]
                self.disappeared[object_id] = 0

                used_rows.add(row)
                used_cols.add(col)

            # 새 객체 등록
            for col in set(range(len(input_centroids))) - used_cols:
                self.register(input_centroids[col])

            # 사라진 객체 관리
            for row in set(range(len(object_centroids))) - used_rows:
                object_id = object_ids[row]
                self.disappeared[object_id] += 1
                if self.disappeared[object_id] > self.max_disappeared:
                    self.deregister(object_id)

        return self.objects  # {id: (cx, cy)}
