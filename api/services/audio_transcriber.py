import base64
import wave
from pathlib import Path
from langchain_openai import ChatOpenAI
from langchain.messages import HumanMessage
from config import OPENROUTER_API_KEY, OPENROUTER_API_HOST, STT_MODEL


class AudioTranscriber:
    def __init__(self, auto_split: bool = True, chunk_duration_seconds: int = 60 * 2):
        """
        Args:
            auto_split: Büyük dosyaları otomatik olarak böl
            chunk_duration_seconds: Her parçanın saniye cinsinden uzunluğu
        """
        self.llm = ChatOpenAI(
            model=STT_MODEL,
            api_key=OPENROUTER_API_KEY,
            base_url=OPENROUTER_API_HOST,
        )
        self.auto_split = auto_split
        self.chunk_duration_seconds = chunk_duration_seconds

    @staticmethod
    def __encode_audio_to_base64(path: Path) -> str:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    @staticmethod
    def __get_wav_duration(audio_path: Path) -> float:
        """WAV dosyasının süresini saniye cinsinden döndürür."""
        try:
            with wave.open(str(audio_path), 'rb') as wav_file:
                frames = wav_file.getnframes()
                rate = wav_file.getframerate()
                return frames / float(rate)
        except:
            return 0

    @staticmethod
    def __split_wav_audio(
            audio_path: Path,
            chunk_duration_seconds: int,
            output_dir: Path = None
    ) -> list[Path]:
        """WAV ses dosyasını belirtilen sürelere böler."""
        if output_dir is None:
            output_dir = audio_path.parent / f"{audio_path.stem}_chunks"

        output_dir.mkdir(parents=True, exist_ok=True)

        with wave.open(str(audio_path), 'rb') as wav_file:
            n_channels = wav_file.getnchannels()
            sampwidth = wav_file.getsampwidth()
            framerate = wav_file.getframerate()
            n_frames = wav_file.getnframes()

            frames_per_chunk = int(framerate * chunk_duration_seconds)

            chunks = []
            chunk_number = 1
            frames_read = 0

            while frames_read < n_frames:
                frames_to_read = min(frames_per_chunk, n_frames - frames_read)
                audio_data = wav_file.readframes(frames_to_read)

                chunk_filename = output_dir / f"{audio_path.stem}_part_{chunk_number:03d}.wav"

                with wave.open(str(chunk_filename), 'wb') as chunk_file:
                    chunk_file.setnchannels(n_channels)
                    chunk_file.setsampwidth(sampwidth)
                    chunk_file.setframerate(framerate)
                    chunk_file.writeframes(audio_data)

                chunks.append(chunk_filename)
                duration = frames_to_read / framerate
                print(f"Parça {chunk_number} oluşturuldu: {chunk_filename.name} ({duration:.2f} saniye)")

                frames_read += frames_to_read
                chunk_number += 1

        return chunks

    @staticmethod
    def __convert_to_wav(input_path: Path) -> Path:
        """FFmpeg kullanarak ses dosyasını WAV formatına çevirir."""
        import subprocess

        output_path = input_path.with_suffix('.wav')

        try:
            subprocess.run([
                'ffmpeg', '-i', str(input_path),
                '-acodec', 'pcm_s16le',
                '-ar', '44100',
                '-ac', '2',
                str(output_path),
                '-y'
            ], check=True, capture_output=True, stderr=subprocess.DEVNULL)

            return output_path
        except FileNotFoundError:
            raise Exception("FFmpeg bulunamadı. WAV olmayan dosyalar için FFmpeg gereklidir.")
        except subprocess.CalledProcessError as e:
            raise Exception(f"Dönüştürme hatası: {e}")

    @staticmethod
    def __cleanup_temp_files(files: list[Path], keep_original: bool = True):
        """Geçici dosyaları temizler."""
        for file in files:
            if file.exists():
                try:
                    file.unlink()
                except:
                    pass

        # Boş dizinleri de temizle
        for file in files:
            if file.parent.exists() and not any(file.parent.iterdir()):
                try:
                    file.parent.rmdir()
                except:
                    pass

    def transcribe(
            self,
            audio_path: Path,
            prompt: str = "Please transcribe this audio file. and dont give any responses about text only transcribe please"
    ):
        """
        Ses dosyasını transkrip eder. Gerekirse otomatik olarak böler.
        """
        audio_path = Path(audio_path)
        temp_files = []
        wav_file = None

        try:
            # WAV formatına çevir (gerekirse)
            if audio_path.suffix.lower() != '.wav':
                print(f"Dosya WAV formatına çevriliyor: {audio_path.name}")
                wav_file = self.__convert_to_wav(audio_path)
                temp_files.append(wav_file)
            else:
                wav_file = audio_path

            # Dosya süresini kontrol et
            duration = self.__get_wav_duration(wav_file)

            # Otomatik bölme aktifse ve dosya uzunsa böl
            if self.auto_split and duration > self.chunk_duration_seconds:
                print(
                    f"Dosya uzun ({duration:.2f} saniye), {self.chunk_duration_seconds} saniyelik parçalara bölünüyor...")

                chunks = self.__split_wav_audio(
                    wav_file,
                    self.chunk_duration_seconds
                )
                temp_files.extend(chunks)

                # Her parçayı transkrip et
                full_transcription = []
                for i, chunk_path in enumerate(chunks, 1):
                    print(f"Parça {i}/{len(chunks)} transkrip ediliyor...")

                    base64_audio = self.__encode_audio_to_base64(chunk_path)
                    message = HumanMessage(
                        content=[
                            {"type": "text", "text": prompt},
                            {
                                "type": "input_audio",
                                "input_audio": {
                                    "data": base64_audio,
                                    "format": "wav",
                                },
                            },
                        ]
                    )

                    response = self.llm.invoke([message])
                    full_transcription.append(response.content)
                    print(f"Parça {i} tamamlandı")

                result = "\n\n".join(full_transcription)
            else:
                # Dosya kısa veya auto_split kapalı - direkt transkrip et
                base64_audio = self.__encode_audio_to_base64(wav_file)

                message = HumanMessage(
                    content=[
                        {"type": "text", "text": prompt},
                        {
                            "type": "input_audio",
                            "input_audio": {
                                "data": base64_audio,
                                "format": wav_file.suffix.replace(".", ""),
                            },
                        },
                    ]
                )

                response = self.llm.invoke([message])
                result = response.content

            return result

        finally:
            # Geçici dosyaları temizle
            if temp_files:
                self.__cleanup_temp_files(temp_files)

