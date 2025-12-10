"""
Audio Feedback Module - Piper TTS
Provides high-quality text-to-speech guidance for blind users
"""

import threading
import queue
import wave
import io
import time
import audioop
from pathlib import Path
from piper import PiperVoice
import pyaudio
import config


class AudioFeedback:
    """Handles text-to-speech audio output using Piper TTS"""

    def __init__(self):
        """Initialize audio feedback system"""
        self.voice = None
        self.audio_player = None
        self.initialized = False

        # Queue management
        self.speech_queue = queue.Queue()
        self.is_speaking = False
        self.worker_thread = None
        self.should_stop = False

        # Message deduplication
        self.last_spoken_message = None
        self.last_speech_time = 0

    def initialize(self, model_path=None):
        """
        Initialize Piper TTS engine

        Args:
            model_path: Path to .onnx model file (uses config default if None)

        Returns:
            True if successful, False otherwise
        """
        try:
            print("Loading Piper TTS voice model...")

            # Use config path or default
            if model_path is None:
                model_path = config.PIPER_MODEL_PATH

            # Resolve paths
            base_dir = Path(__file__).resolve().parent
            model_path = Path(model_path)

            if not model_path.is_absolute():
                model_path = base_dir / model_path

            # Validate model file
            if not model_path.exists():
                raise FileNotFoundError(f"Piper model missing: {model_path}")

            # Load Piper voice
            self.voice = PiperVoice.load(str(model_path))

            # Initialize PyAudio for playback
            self.audio_player = pyaudio.PyAudio()

            self.initialized = True

            # Start worker thread for non-blocking speech
            self.worker_thread = threading.Thread(
                target=self._speech_worker,
                daemon=True
            )
            self.worker_thread.start()

            print(f"✅ Piper TTS audio initialized (sample rate: {self.voice.config.sample_rate} Hz)")

            # Welcome message
            self.speak("Navigation system ready", priority=True)

            return True

        except FileNotFoundError as e:
            print(f"❌ {e}")
            print("   Download from: https://huggingface.co/rhasspy/piper-voices")
            return False

        except Exception as e:
            print(f"❌ Audio initialization failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    def speak(self, text, priority=False):
        """
        Queue text for speech output

        Args:
            text: Text to speak
            priority: If True, clear queue and speak immediately
        """
        if not self.initialized or not config.ENABLE_AUDIO:
            return

        # Check cooldown period
        current_time = time.time() * 1000  # ms
        if not priority and (current_time - self.last_speech_time) < config.SPEECH_COOLDOWN_MS:
            return

        # Check message deduplication
        if not priority and not config.REPEAT_SAME_MESSAGE:
            if text == self.last_spoken_message:
                return

        if priority:
            # Clear queue for urgent messages
            while not self.speech_queue.empty():
                try:
                    self.speech_queue.get_nowait()
                except queue.Empty:
                    break

        # Add to queue
        self.speech_queue.put((text, priority))

    def _speech_worker(self):
        """Worker thread that processes speech queue"""
        while not self.should_stop:
            try:
                # Get text from queue (timeout to check should_stop)
                text, priority = self.speech_queue.get(timeout=0.1)

                # Synthesize and play
                self._synthesize_and_play(text)

                # Update last speech time and message
                self.last_speech_time = time.time() * 1000
                self.last_spoken_message = text

            except queue.Empty:
                continue
            except Exception as e:
                print(f"Speech error: {e}")
                self.is_speaking = False

    def _synthesize_and_play(self, text):
        """
        Synthesize text to audio and play it

        Args:
            text: Text to synthesize
        """
        try:
            self.is_speaking = True

            # Create BytesIO buffer
            wav_buffer = io.BytesIO()

            # Open as wave file and synthesize into it
            with wave.open(wav_buffer, 'wb') as wav_file:
                # synthesize_wav() writes to an open wave.Wave_write object
                self.voice.synthesize_wav(text, wav_file)

            # Get the complete WAV bytes
            wav_buffer.seek(0)
            wav_data = wav_buffer.read()

            # Check if we got audio data (more than just WAV header)
            if len(wav_data) <= 44:  # 44 bytes = empty WAV header
                print(f"⚠️  Warning: No audio generated for text: '{text}'")
                self.is_speaking = False
                return

            # Play the WAV data
            self._play_audio(wav_data)

            self.is_speaking = False

        except Exception as e:
            print(f"Synthesis error: {e}")
            import traceback
            traceback.print_exc()
            self.is_speaking = False

    def _play_audio(self, wav_data):
        """
        Play WAV audio data

        Args:
            wav_data: WAV file bytes
        """
        try:
            # Open WAV data
            wav_stream = io.BytesIO(wav_data)
            wav_file = wave.open(wav_stream, 'rb')

            # Open audio stream
            stream = self.audio_player.open(
                format=self.audio_player.get_format_from_width(wav_file.getsampwidth()),
                channels=wav_file.getnchannels(),
                rate=wav_file.getframerate(),
                output=True
            )

            # Play in chunks
            chunk_size = 1024
            data = wav_file.readframes(chunk_size)

            # Apply software volume
            sample_width = wav_file.getsampwidth()
            volume = max(0.0, min(1.0, getattr(config, "AUDIO_VOLUME", 1.0)))

            while data and not self.should_stop:
                if volume != 1.0:
                    try:
                        data = audioop.mul(data, sample_width, volume)
                    except Exception:
                        pass  # Play at full volume if adjustment fails
                stream.write(data)
                data = wav_file.readframes(chunk_size)

            # Cleanup
            stream.stop_stream()
            stream.close()
            wav_file.close()

        except Exception as e:
            print(f"Playback error: {e}")
            import traceback
            traceback.print_exc()

    def speak_guidance(self, guidance_dict):
        """
        Speak navigation guidance with appropriate urgency

        Args:
            guidance_dict: Guidance dictionary from GuidanceEngine
        """
        if not self.initialized:
            return

        message = guidance_dict.get('message', '')
        urgency = guidance_dict.get('urgency', 'medium')

        # Add urgency cues
        if urgency == 'critical':
            message = f"Warning! {message}"
        elif urgency == 'high':
            message = f"Caution. {message}"

        # Determine priority
        priority = urgency in ['critical', 'high']

        # Speak
        self.speak(message, priority=priority)

    def speak_status(self, status_text):
        """
        Speak system status updates

        Args:
            status_text: Status message to speak
        """
        if config.SPEAK_ON_STATUS_CHANGE:
            self.speak(status_text, priority=True)

    def test_audio(self):
        """Test audio output with a sample message"""
        self.speak("Audio test. Navigation system working correctly.", priority=True)

    def is_busy(self):
        """
        Check if currently speaking or has queued messages

        Returns:
            True if speaking or queue not empty
        """
        return self.is_speaking or not self.speech_queue.empty()

    def stop_speaking(self):
        """Stop current speech and clear queue"""
        # Clear queue
        while not self.speech_queue.empty():
            try:
                self.speech_queue.get_nowait()
            except queue.Empty:
                break

        self.is_speaking = False

    def set_volume(self, volume):
        """
        Set playback volume

        Args:
            volume: 0.0 to 1.0
        """
        config.AUDIO_VOLUME = volume

    def shutdown(self):
        """Clean shutdown of audio system"""
        print("Shutting down audio system...")

        self.should_stop = True

        # Wait for worker thread
        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=2.0)

        # Cleanup PyAudio
        if self.audio_player:
            self.audio_player.terminate()

        self.initialized = False
        print("✅ Audio system shutdown complete")

    def __del__(self):
        """Destructor to ensure cleanup"""
        if self.initialized:
            self.shutdown()