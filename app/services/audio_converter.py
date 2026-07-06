import os
import subprocess


def convert_to_wav(input_path):
  
    output_path = os.path.splitext(input_path)[0] + ".wav"

    print(f"[Converter] Input: {input_path}")
    print(f"[Converter] Output: {output_path}")

    try:
        subprocess.run(
            [
                "ffmpeg",
                "-y",             
                "-i", input_path,  
                "-ac", "1",        
                "-ar", "16000",    
                output_path
            ],
            check=True,
            capture_output=True,
            text=True
        )

        print("[Converter] Conversion successful")

        if not os.path.exists(output_path):
            raise Exception("WAV file was not created")

        return output_path

    except subprocess.CalledProcessError as e:
        print("[Converter] FFmpeg Error:")
        print(e.stderr)

        raise Exception(
            f"Audio conversion failed: {e.stderr}"
        )