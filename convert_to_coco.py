import json
import os
import argparse
from datetime import datetime
import hashlib

class COCOConverter:
    def __init__(self):
        self.coco_data = {
            "info": {
                "description": "Custom annotations for human face",
                "version": "1.0",
                "year": "2025",
                "contributor": "Your Name",
                "date_created": datetime.now().strftime("%Y-%m-%d")
            },
            "categories": [
                {
                    "supercategory": "butterfly",
                    "id": 101,
                    "name": "butterfly",
                    "keypoints": [
                        "Head", "Thorax", "Abdomen", "Left_wing_1", "Left_wing_2", 
                        "Left_wing_3", "Right_wing_1", "Right_wing_2", "Right_wing_3"
                    ],
                    "skeleton": [
                        [0, 1], [1, 2], [1, 3], [1, 4], [1, 5], [1, 6], [1, 7], [1, 8]
                    ]
                }
            ],
            "images": [],
            "annotations": []
        }
        self.image_id_counter = 1
        self.annotation_id_counter = 1

    def generate_unique_id(self, text):
        """Generate a unique ID based on text hash"""
        return int(hashlib.md5(text.encode()).hexdigest()[:10], 16)

    def load_json(self, file_path):
        """Load JSON data from file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            return None

    def save_json(self, file_path, data, is_dir_check=False):
        """Save JSON data to file"""
        if is_dir_check:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def extract_keypoints_from_annotation(self, annotation):
        """Extract keypoints from annotation data"""
        keypoints = []
        if 'keypoints' in annotation:
            for kp in annotation['keypoints']:
                if 'value' in kp and len(kp['value']) >= 3:
                    keypoints.extend(kp['value'])
                elif 'value' in kp and len(kp['value']) == 2:
                    # Add visibility flag if missing
                    keypoints.extend([kp['value'][0], kp['value'][1], 1])
        
        # Ensure we have the right number of keypoints (9 keypoints * 3 = 27 values)
        while len(keypoints) < 27:
            keypoints.extend([0, 0, 0])
        
        return keypoints[:27]  # Limit to expected number

    def calculate_bbox_from_keypoints(self, keypoints):
        """Calculate bounding box from keypoints"""
        if not keypoints or len(keypoints) < 6:
            return [0, 0, 1, 1]
        
        # Extract x, y coordinates (skip visibility flags)
        x_coords = []
        y_coords = []
        
        for i in range(0, len(keypoints), 3):
            if i + 1 < len(keypoints) and keypoints[i] > 0 and keypoints[i + 1] > 0:
                x_coords.append(keypoints[i])
                y_coords.append(keypoints[i + 1])
        
        if not x_coords or not y_coords:
            return [0, 0, 1, 1]
        
        min_x = min(x_coords)
        min_y = min(y_coords)
        max_x = max(x_coords)
        max_y = max(y_coords)
        
        width = max_x - min_x
        height = max_y - min_y
        
        return [min_x, min_y, width, height]

    def convert_annotation_to_coco(self, source_data):
        pass

    def process_folder(self, input_folder):
        """Process all JSON files in a folder"""
        json_files = []
        for root, dirs, files in os.walk(input_folder):
            for file in files:
                if file.endswith('.json'):
                    json_files.append(os.path.join(root, file))
        
        print(f"Found {len(json_files)} JSON files to process")
        folder_data = []
        for json_file in json_files:
            print(f"Processing: {json_file}")
            source_data = self.load_json(json_file)
            
            if source_data:
                folder_data.append(source_data)

        result = self.convert_annotation_to_coco(folder_data)
        if result:
            image_info, annotations = result
            self.coco_data['images'] = [image_info]
            self.coco_data['annotations'] = annotations

        print(f"Processed {len(self.coco_data['images'])} images with {len(self.coco_data['annotations'])} annotations")
        return self.coco_data

    def convert_single_file(self, input_file):
        """Convert a single JSON file to COCO format"""
        source_data = self.load_json(input_file)
        if source_data:
            result = self.convert_annotation_to_coco(source_data)
            if result:
                image_info, annotations = result
                self.coco_data['images'].append(image_info)
                self.coco_data['annotations'].extend(annotations)
        
        return self.coco_data

def main():
    parser = argparse.ArgumentParser(description='Convert annotation format to COCO format')
    parser.add_argument('input_path', type=str, help='Input file or folder path')
    parser.add_argument('output_file', type=str, help='Output COCO JSON file path')
    parser.add_argument('--single-file', action='store_true', help='Process single file instead of folder')
    
    args = parser.parse_args()
    
    converter = COCOConverter()
    
    if args.single_file:
        coco_data = converter.convert_single_file(args.input_path)
    else:
        coco_data = converter.process_folder(args.input_path)
    
    converter.save_json(args.output_file, coco_data)
    print(f"COCO format data saved to: {args.output_file}")

if __name__ == "__main__":
    main()

# Usage examples:
# python convert_to_coco.py "a/OK_001" "output_coco.json" --single-file  # For single file
# python convert_to_coco.py "a" "output_coco.json"  # For entire folder