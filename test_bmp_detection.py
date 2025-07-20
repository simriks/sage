import cv2
import glob
import os
import time
import zipfile
from pathlib import Path
from body_detection import BodyDetectionSystem
from config import Config

class BMPTestProcessor:
    def __init__(self):
        self.config = Config()
        self.detection_system = BodyDetectionSystem(self.config)
        
    def extract_and_process_bmps(self, zip_path, extract_folder="test_bmps"):
        """Extract BMP files from zip and process them"""
        
        print(f"🗂️  Extracting BMPs from: {zip_path}")
        
        # Create extraction folder
        os.makedirs(extract_folder, exist_ok=True)
        
        # Extract zip file
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Extract only BMP files
            bmp_files = [f for f in zip_ref.namelist() if f.lower().endswith('.bmp')]
            
            for bmp_file in bmp_files:
                zip_ref.extract(bmp_file, extract_folder)
            
            print(f"✅ Extracted {len(bmp_files)} BMP files")
        
        # Process the extracted BMPs
        return self.process_bmp_folder(extract_folder)
    
    def process_bmp_folder(self, folder_path):
        """Process all BMP files in folder"""
        
        # Get all BMP files
        bmp_pattern = os.path.join(folder_path, "**/*.bmp")
        bmp_files = glob.glob(bmp_pattern, recursive=True)
        
        if not bmp_files:
            print("❌ No BMP files found!")
            return False
        
        print(f"📸 Found {len(bmp_files)} BMP files")
        
        # Sort files (by name/timestamp)
        bmp_files.sort()
        
        # Create video from BMPs (FIXED DURATION)
        video_path = self.create_video_from_bmps(bmp_files)
        
        if video_path:
            # Run GENERAL analysis first
            self.run_general_analysis(video_path)
            
            # Then run survivor detection
            self.run_detection_test(video_path)
            return True
        
        return False
    
    def create_video_from_bmps(self, bmp_files, target_duration=5, fps=20):
        """Convert BMP sequence to video with MINIMUM 5 seconds"""
        
        print(f"🎬 Converting {len(bmp_files)} BMPs to {target_duration}s video...")
        
        # Read first image to get dimensions
        first_img = cv2.imread(bmp_files[0])
        if first_img is None:
            print("❌ Could not read first BMP file")
            return None
        
        height, width = first_img.shape[:2]
        print(f"📐 Video dimensions: {width}x{height}")
        
        # Calculate frames needed for target duration
        frames_needed = fps * target_duration
        print(f"🎯 Target: {frames_needed} frames for {target_duration}s video")
        
        # If we don't have enough images, duplicate them
        if len(bmp_files) < frames_needed:
            print(f"⚠️  Only {len(bmp_files)} images, duplicating to reach {frames_needed} frames")
            # Repeat the image list to get enough frames
            multiplier = (frames_needed // len(bmp_files)) + 1
            extended_files = (bmp_files * multiplier)[:frames_needed]
        else:
            # If we have too many, space them out evenly
            step = len(bmp_files) // frames_needed
            extended_files = bmp_files[::step][:frames_needed]
        
        print(f"📊 Using {len(extended_files)} frames for video")
        
        # Create output path
        timestamp = int(time.time())
        output_path = f"temp_videos/bmp_test_{timestamp}.mp4"
        os.makedirs("temp_videos", exist_ok=True)
        
        # Set up video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video_writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        # Process images
        frames_written = 0
        for i, bmp_path in enumerate(extended_files):
            img = cv2.imread(bmp_path)
            if img is not None:
                # Resize if needed to match first image dimensions
                if img.shape[:2] != (height, width):
                    img = cv2.resize(img, (width, height))
                
                video_writer.write(img)
                frames_written += 1
                
                # Progress indicator
                if i % 20 == 0:
                    print(f"  Processed {i+1}/{len(extended_files)} frames", end='\r')
        
        video_writer.release()
        
        print(f"\n✅ Video created: {output_path}")
        print(f"📊 Frames written: {frames_written}")
        
        # Check video duration
        test_cap = cv2.VideoCapture(output_path)
        total_frames = test_cap.get(cv2.CAP_PROP_FRAME_COUNT)
        video_fps = test_cap.get(cv2.CAP_PROP_FPS)
        duration = total_frames / video_fps if video_fps > 0 else 0
        test_cap.release()
        
        print(f"🕒 Video duration: {duration:.2f} seconds")
        
        if duration >= 4:
            print("✅ Video duration meets TwelveLabs requirements!")
        else:
            print("⚠️  Warning: Video might still be too short for TwelveLabs API")
        
        return output_path
    
    def run_general_analysis(self, video_path):
        """Run general video analysis to see what's in the BMPs"""
        
        print("\n🔍 GENERAL VIDEO ANALYSIS - What's in your BMP files?")
        print("=" * 60)
        
        try:
            from twelvelabs import TwelveLabs
            
            client = TwelveLabs(api_key=self.config.TWELVELABS_API_KEY)
            
            # Upload video
            print("📤 Uploading video for general analysis...")
            video_upload = client.upload(self.detection_system.index_id, video_path)
            
            # Wait for processing
            print("⏳ Processing video...")
            time.sleep(10)  # Give it time to process
            
            # General analysis queries
            analysis_queries = [
                "What objects, people, or activities are visible in this video?",
                "Describe the overall scene and environment shown in the video.",
                "What is the main content or subject matter of this video?",
                "Are there any people visible? What are they doing?",
                "What type of location or setting is shown in the video?",
                "Are there any vehicles, buildings, or equipment visible?"
            ]
            
            print("\n📋 GENERAL ANALYSIS RESULTS:")
            print("=" * 40)
            
            for i, query in enumerate(analysis_queries, 1):
                try:
                    print(f"\n🔍 Analysis {i}: {query}")
                    
                    response = client.search.query(
                        index_id=self.detection_system.index_id,
                        query=query,
                        options=["visual"]
                    )
                    
                    if response.data:
                        for j, result in enumerate(response.data[:2]):  # Show top 2 results
                            confidence = result.confidence
                            start_time = result.start
                            end_time = result.end
                            
                            print(f"   📊 Result {j+1}: Confidence {confidence:.3f}")
                            print(f"   ⏱️  Time: {start_time:.1f}s - {end_time:.1f}s")
                            
                            if confidence > 0.3:  # Lower threshold for general analysis
                                print(f"   ✅ DETECTED: Content matches query!")
                            else:
                                print(f"   ⚪ Low confidence match")
                    else:
                        print("   ❌ No matches found for this query")
                        
                except Exception as e:
                    print(f"   ❌ Query error: {e}")
                
                time.sleep(2)  # Rate limiting
                
        except Exception as e:
            print(f"❌ General analysis error: {e}")
    
    def run_detection_test(self, video_path):
        """Run survivor detection on the test video"""
        
        print("\n🚨 SURVIVOR DETECTION TEST")
        print("=" * 50)
        
        try:
            # Use your existing detection system
            print("📤 Running survivor detection analysis...")
            results = self.detection_system._analyze_video_with_pegasus(video_path)
            
            print("\n📊 SURVIVOR DETECTION RESULTS:")
            print("=" * 35)
            
            if results and 'data' in results:
                print(f"✅ Analysis completed successfully!")
                print(f"📋 Found {len(results['data'])} analysis clips")
                
                survivors_found = 0
                
                for i, clip in enumerate(results['data']):
                    confidence = clip.get('confidence', 0)
                    start_time = clip.get('start', 0)
                    end_time = clip.get('end', 0)
                    
                    print(f"\n🎬 Clip {i+1}:")
                    print(f"   ⏱️  Time: {start_time:.1f}s - {end_time:.1f}s")
                    print(f"   🎯 Confidence: {confidence:.3f}")
                    
                    if confidence > self.config.CONFIDENCE_THRESHOLD:
                        survivors_found += 1
                        print(f"   🚨 POTENTIAL SURVIVOR DETECTED!")
                        
                        if confidence > self.config.HIGH_PRIORITY_THRESHOLD:
                            print(f"   🔴 HIGH PRIORITY DETECTION!")
                    else:
                        print(f"   ⚪ Below confidence threshold ({self.config.CONFIDENCE_THRESHOLD})")
                
                print(f"\n🎯 SURVIVOR DETECTION SUMMARY:")
                print(f"   Total survivors detected: {survivors_found}")
                print(f"   Detection rate: {survivors_found/len(results['data'])*100:.1f}%")
                
            else:
                print("❌ No detection results returned")
                print("🔍 This could mean:")
                print("   - No survivors detected in the images")
                print("   - Video quality issues")
                print("   - API processing error")
        
        except Exception as e:
            print(f"❌ Detection error: {e}")
        
        finally:
            print(f"\n🗑️  Cleaning up video file: {video_path}")
            if os.path.exists(video_path):
                os.remove(video_path)

def main():
    """Main test function"""
    
    processor = BMPTestProcessor()
    
    # Ask for zip file path
    print("🧪 BMP Detection Test with General Analysis")
    print("=" * 45)
    
    zip_path = input("Enter path to your BMP zip file: ").strip()
    
    if not os.path.exists(zip_path):
        print(f"❌ File not found: {zip_path}")
        return
    
    if not zip_path.lower().endswith('.zip'):
        print("❌ Please provide a .zip file")
        return
    
    print(f"\n🚀 Starting test with: {zip_path}")
    
    # Process the zip file
    success = processor.extract_and_process_bmps(zip_path)
    
    if success:
        print("\n✅ Test completed successfully!")
    else:
        print("\n❌ Test failed")

if __name__ == "__main__":
    main()