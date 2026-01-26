import base64
import time
import wave
from pathlib import Path
from langchain_openai import ChatOpenAI
from langchain.messages import HumanMessage
from openai import APIError
from config import OPENROUTER_API_KEY, OPENROUTER_API_HOST, STT_MODEL


class AudioTranscriber:
    def __init__(self, auto_split: bool = True, max_chunk_size_mb: float = 9.5):
        """
        Args:
            auto_split: Büyük dosyaları otomatik olarak böl
            max_chunk_size_mb: Her parçanın maksimum boyutu (MB cinsinden)
        """
        self.llm = ChatOpenAI(
            model=STT_MODEL,
            api_key=OPENROUTER_API_KEY,
            base_url=OPENROUTER_API_HOST,
            timeout=120,
            max_retries=3,
        )
        self.auto_split = auto_split
        self.max_chunk_size_mb = max_chunk_size_mb

    @staticmethod
    def __get_file_size_mb(path: Path) -> float:
        """Dosya boyutunu MB cinsinden döndürür"""
        return path.stat().st_size / (1024 * 1024)

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
        except Exception as e:
            print(f"⚠️ Süre hesaplama hatası: {e}")
            return 0

    @staticmethod
    def __calculate_chunk_duration_for_size(
            audio_path: Path,
            target_size_mb: float
    ) -> int:
        """Hedef dosya boyutuna ulaşmak için gerekli chunk süresini hesaplar."""
        try:
            with wave.open(str(audio_path), 'rb') as wav_file:
                # WAV dosya bilgileri
                n_channels = wav_file.getnchannels()
                sampwidth = wav_file.getsampwidth()
                framerate = wav_file.getframerate()
                n_frames = wav_file.getnframes()

                # Toplam dosya boyutu
                total_size_bytes = n_frames * n_channels * sampwidth
                total_size_mb = total_size_bytes / (1024 * 1024)

                # Toplam süre
                total_duration = n_frames / framerate

                # MB başına süre
                seconds_per_mb = total_duration / total_size_mb if total_size_mb > 0 else 0

                # Hedef boyut için gerekli süre
                chunk_duration = int(seconds_per_mb * target_size_mb)

                # Minimum 10 saniye, maksimum dosya süresinin yarısı
                chunk_duration = max(10, min(chunk_duration, int(total_duration / 2)))

                print(f"📐 Hesaplama: {total_size_mb:.2f}MB = {total_duration:.2f}s")
                print(f"📐 Hedef: {target_size_mb}MB → ~{chunk_duration}s parçalar")

                return chunk_duration

        except Exception as e:
            print(f"⚠️ Chunk süresi hesaplanamadı: {e}")
            return 60  # Varsayılan 60 saniye

    @staticmethod
    def __split_wav_audio_by_size(
            audio_path: Path,
            max_chunk_size_mb: float,
            output_dir: Path = None
    ) -> list[Path]:
        """WAV ses dosyasını belirtilen boyuta göre böler."""
        if output_dir is None:
            output_dir = audio_path.parent / f"{audio_path.stem}_chunks"

        output_dir.mkdir(parents=True, exist_ok=True)

        # Hedef boyuta göre chunk süresini hesapla
        chunk_duration_seconds = AudioTranscriber.__calculate_chunk_duration_for_size(
            audio_path,
            max_chunk_size_mb
        )

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

                # Chunk bilgilerini göster
                chunk_size = AudioTranscriber.__get_file_size_mb(chunk_filename)
                duration = frames_to_read / framerate
                print(f"✂️ Parça {chunk_number}: {chunk_filename.name} ({chunk_size:.2f}MB, {duration:.2f}s)")

                chunks.append(chunk_filename)
                frames_read += frames_to_read
                chunk_number += 1

        return chunks

    @staticmethod
    def __convert_to_wav(input_path: Path) -> Path:
        """FFmpeg kullanarak ses dosyasını WAV formatına çevirir."""
        import subprocess

        output_path = input_path.with_suffix('.wav')

        try:
            print(f"🔄 WAV'a çevriliyor: {input_path.name}")
            subprocess.run([
                'ffmpeg', '-i', str(input_path),
                '-acodec', 'pcm_s16le',
                '-ar', '16000',  # 16kHz
                '-ac', '1',  # Mono
                str(output_path),
                '-y'
            ],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=True
            )

            file_size = AudioTranscriber.__get_file_size_mb(output_path)
            print(f"✅ Dönüştürme tamamlandı: {file_size:.2f}MB")
            return output_path

        except FileNotFoundError:
            raise Exception("❌ FFmpeg bulunamadı. WAV olmayan dosyalar için FFmpeg gereklidir.")
        except subprocess.CalledProcessError as e:
            raise Exception(f"❌ Dönüştürme hatası: {e}")

    @staticmethod
    def __cleanup_temp_files(files: list[Path]):
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

    def __transcribe_chunk_with_retry(
            self,
            chunk_path: Path,
            prompt: str,
            max_retries: int = 3
    ) -> str:
        """Tek bir parçayı retry mekanizması ile transkrip eder"""

        for attempt in range(max_retries):
            try:
                # Dosya boyutunu kontrol et
                file_size = self.__get_file_size_mb(chunk_path)
                if file_size > self.max_chunk_size_mb:
                    raise Exception(
                        f"⚠️ Parça çok büyük ({file_size:.2f}MB). "
                        f"Max {self.max_chunk_size_mb}MB olmalı."
                    )

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
                return response.content

            except APIError as e:
                if e.status_code == 500:
                    wait_time = (attempt + 1) * 10
                    print(f"🔴 HTTP 500 hatası (Deneme {attempt + 1}/{max_retries}). {wait_time}s bekleniyor...")

                    if attempt < max_retries - 1:
                        time.sleep(wait_time)
                    else:
                        raise Exception(
                            f"❌ {max_retries} denemeden sonra başarısız. "
                            f"max_chunk_size_mb değerini azaltmayı deneyin (şu an: {self.max_chunk_size_mb}MB)."
                        )
                else:
                    raise

            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"⚠️ Hata: {e}. Yeniden deneniyor...")
                    time.sleep(5)
                else:
                    raise

    def transcribe(
            self,
            audio_path: Path,
            prompt: str = "Please transcribe this audio file accurately. Only return the transcription, no additional comments."
    ):
        """
        Ses dosyasını transkrip eder. Gerekirse otomatik olarak boyuta göre böler.
        """
        audio_path = Path(audio_path)
        temp_files = []
        wav_file = None

        try:
            # WAV formatına çevir (gerekirse)
            if audio_path.suffix.lower() != '.wav':
                wav_file = self.__convert_to_wav(audio_path)
                temp_files.append(wav_file)
            else:
                wav_file = audio_path

            # Dosya bilgilerini göster
            duration = self.__get_wav_duration(wav_file)
            file_size = self.__get_file_size_mb(wav_file)
            print(f"📊 Dosya: {duration:.2f}s, {file_size:.2f}MB")

            # Dosya boyutu kontrolü
            if self.auto_split and file_size > self.max_chunk_size_mb:
                print(f"📦 Dosya büyük ({file_size:.2f}MB > {self.max_chunk_size_mb}MB)")
                print(f"📦 Max {self.max_chunk_size_mb}MB parçalara bölünüyor...")

                chunks = self.__split_wav_audio_by_size(
                    wav_file,
                    self.max_chunk_size_mb
                )
                temp_files.extend(chunks)

                # Her parçayı transkrip et
                full_transcription = []
                for i, chunk_path in enumerate(chunks, 1):
                    chunk_size = self.__get_file_size_mb(chunk_path)
                    print(f"🎙️ Parça {i}/{len(chunks)} transkrip ediliyor ({chunk_size:.2f}MB)...")

                    chunk_text = self.__transcribe_chunk_with_retry(
                        chunk_path,
                        prompt,
                        max_retries=3
                    )

                    full_transcription.append(chunk_text)
                    print(f"✅ Parça {i} tamamlandı ({len(chunk_text)} karakter)")

                    # API'ye nazik ol
                    if i < len(chunks):
                        time.sleep(2)

                result = "\n\n".join(full_transcription)
                print(f"🎉 Tüm transkripsiyon tamamlandı! ({len(result)} karakter)")

            else:
                # Dosya küçük - direkt transkrip et
                print(f"🎙️ Transkripsiyon başlıyor...")
                result = self.__transcribe_chunk_with_retry(
                    wav_file,
                    prompt,
                    max_retries=3
                )
                print(f"✅ Tamamlandı! ({len(result)} karakter)")

            return result

        finally:
            # Geçici dosyaları temizle
            if temp_files:
                print(f"🧹 Geçici dosyalar temizleniyor...")
                self.__cleanup_temp_files(temp_files)