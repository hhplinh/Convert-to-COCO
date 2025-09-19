import convert_to_coco
import os
import argparse
import json

class ButterflyToCOCOConverter(convert_to_coco.COCOConverter):
    def __init__(self):
        super().__init__()
        self.id_counter = 4e16

    def convert_annotation_to_coco(self, data_folder):
        id_counter = int(self.id_counter)
        for data in data_folder:
            if not data:
                continue
            
            image_id = id_counter

            file_name = f"butterfly/original/{data['name']}"
            width = data['width']
            height = data['height']
            image_info = {
                "id": image_id,
                "file_name": file_name,
                "width": width,
                "height": height
            }
            self.coco_data['images'].append(image_info)

            annotation_id = id_counter
            bbox_area = 1
            keypoints = [0] * 27
            bbox = [0, 0, 1, 1]
            
            id_counter += 1

            if 'annotations' in data:
                anns = data['annotations']
                keypoints = []
                
                for ann in anns:
                    list_keypoints = ann["keypoints"]
                    for kp in list_keypoints:
                        keypoints.extend(kp["value"])

                if keypoints:
                    x_coords = []
                    y_coords = []
                    for i in range(0, len(keypoints), 3):
                        if i + 1 < len(keypoints) and keypoints[i] > 0 and keypoints[i + 1] > 0:
                            x_coords.append(keypoints[i])
                            y_coords.append(keypoints[i + 1])
                    
                    x_topleft = min(x_coords)
                    y_topleft = min(y_coords)
                    x_topright = max(x_coords, default=1)
                    y_topright = max(y_coords, default=1)

                    bbox = [x_topleft, y_topleft, x_topright - x_topleft, y_topright - y_topleft]

                    bbox_area = bbox[2] * bbox[3]

            annotations = {
                "id": annotation_id,
                "image_id": image_id,
                "category_id": 101,
                "bbox": bbox,
                "area": bbox_area,
                "iscrowd": 0,
                "num_keypoints": 9,
                "keypoints": keypoints,
            }
            self.coco_data['annotations'].append(annotations)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert butterfly annotations to COCO format')
    parser.add_argument('input_path', type=str, help='Input file or folder path')
    parser.add_argument('output_file', type=str, help='Output COCO JSON file path')
    parser.add_argument('--single-file', action='store_true', help='Process single file instead of folder')
    
    args = parser.parse_args()
    
    converter = ButterflyToCOCOConverter()
    
    if args.single_file:
        source_data = converter.load_json_from_file(args.input_path)
        if source_data:
            coco_data = converter.convert_single_file(args.input_path)
            converter.save_json(args.output_file, coco_data)
    else:
        coco_data = converter.process_folder(args.input_path)
        converter.save_json(args.output_file, coco_data)
        
    print(f"Conversion completed. COCO data saved to {args.output_file}")

# python butterfly_to_coco.py jsons butterfly_coco.json

# python butterfly_to_coco.py a butterfly_coco.json