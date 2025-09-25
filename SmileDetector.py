from studio.custom_block import *
import cv2
import os

class SmileDetector(Block):
    op_code = 'SmileDetector'
    title = 'SmileDetector'
    tooltip = 'Detect smile using Haar Cascade XMLs from project folder'

    def init(self):
        self.width = 300
        self.height = 380

        self.input_sockets = [SocketTypes.ImageAny('Camera')]
        self.output_sockets = [
            SocketTypes.ImageAny('Annotated'),
            SocketTypes.String('Label'),
            SocketTypes.Boolean('IsSmiling'),
            SocketTypes.Number('Face Count')  # ✅ Yeni çıkış: yüz sayısı
        ]

        self.param['min_neighbors'] = SliderLabeled(
            min=1, max=30, val=20,
            label="Smile minNeighbors",
            tooltip="Gülümsemeyi tespit ederken komşu bölge sayısı"
        )

        self.param['scale_factor'] = SliderLabeled(
            min=10, max=20, val=17,
            label="Smile scaleFactor x0.1",
            tooltip="Gülümseme tespiti için ölçekleme faktörü"
        )

        try:
            base_path = os.path.dirname(__file__)
            face_path = os.path.join(base_path, 'haarcascade_frontalface_default.xml')
            smile_path = os.path.join(base_path, 'haarcascade_smile.xml')

            self.face_cascade = cv2.CascadeClassifier(face_path)
            self.smile_cascade = cv2.CascadeClassifier(smile_path)

            if self.face_cascade.empty() or self.smile_cascade.empty():
                raise Exception("Cascade dosyaları yüklenemedi.")

            self.logInfo("Cascade dosyaları başarıyla yüklendi.")
        except Exception as e:
            self.logError(f"Haar cascade yüklenemedi: {str(e)}")

    def run(self):
        img = self.input['Camera'].data
        if img is None:
            self.logError("Giriş görüntüsü yok.")
            return

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

        face_count = len(faces)  # ✅ Yüz sayısı

        label = "No Face"
        annotated = img.copy()
        is_smiling = False

        smile_min_neighbors = int(self.param['min_neighbors'].value)
        smile_scale_factor = self.param['scale_factor'].value / 10.0

        for (x, y, w, h) in faces:
            roi_gray = gray[y:y+h, x:x+w]
            smiles = self.smile_cascade.detectMultiScale(
                roi_gray,
                scaleFactor=smile_scale_factor,
                minNeighbors=smile_min_neighbors
            )

            if len(smiles) > 0:
                label = "Smiling"
                is_smiling = True
                color = (0, 255, 0)
            else:
                label = "Not Smiling"
                color = (0, 0, 255)

            cv2.rectangle(annotated, (x, y), (x+w, y+h), color, 2)
            cv2.putText(annotated, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

        self.output['Annotated'].data = annotated
        self.output['Label'].data = label
        self.output['IsSmiling'].data = is_smiling
        self.output['Face Count'].data = face_count  # ✅ Yeni çıkışa veri yaz

add_block(SmileDetector.op_code, SmileDetector)
